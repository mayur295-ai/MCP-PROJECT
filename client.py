import os
import re
import json
import asyncio
import traceback
from dotenv import load_dotenv
from openai import AsyncOpenAI, RateLimitError, APITimeoutError
from mcp import ClientSession
from mcp.client.sse import sse_client

# Model to use — openrouter/free auto-picks an available free model with tool support
MODEL = "openrouter/free"

# Load API key
load_dotenv()
API_KEY = os.getenv("API_KEY")


def parse_arguments(raw: str) -> dict:
    """Robustly parse tool-call arguments even if the model returns slightly malformed JSON."""
    # Try standard JSON first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Some models wrap keys without quotes — fix that
    fixed = re.sub(r"(\w+)\s*:", r'"\1":', raw)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass
    # Last resort: try to extract key=value pairs like a=5 b=3
    pairs = re.findall(r'"?(\w+)"?\s*[:=]\s*"?([^,}"]+)"?', raw)
    result = {}
    for k, v in pairs:
        v = v.strip()
        try:
            result[k] = int(v)
        except ValueError:
            try:
                result[k] = float(v)
            except ValueError:
                result[k] = v
    return result


async def llm_call(client, retries=3, **kwargs):
    """Call the LLM with automatic retry on rate-limit and timeout errors."""
    for attempt in range(retries):
        try:
            return await client.chat.completions.create(**kwargs)
        except RateLimitError:
            wait = 2 ** (attempt + 1)
            print(f"⏳ Rate limited, retrying in {wait}s...")
            await asyncio.sleep(wait)
        except APITimeoutError:
            wait = 3 ** (attempt + 1)
            print(f"⏳ Request timed out, retrying in {wait}s...")
            await asyncio.sleep(wait)
    # Final attempt — let it raise
    return await client.chat.completions.create(**kwargs)


async def run_session(session, client, openai_tools):
    """Main interaction loop — separated so SSE stays alive."""
    print("\n🚀 Ready! Try:")
    print("  add 5 and 3")
    print("  multiply 4 and 6")
    print("  greet Mayuresh")
    print("  (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        messages = [{"role": "user", "content": user_input}]

        print("Thinking...")

        try:
            # 🤖 LLM decides which tool to call
            response = await llm_call(
                client,
                model=MODEL,
                messages=messages,
                tools=openai_tools,
                tool_choice="auto",
            )

            choice = response.choices[0]

            # 🔧 If tool is called
            if choice.message.tool_calls:
                tool_call = choice.message.tool_calls[0]
                tool_name = tool_call.function.name
                args = parse_arguments(tool_call.function.arguments)

                print(f"🔧 Calling tool: {tool_name} with {args}")

                # ⚡ Execute tool via MCP
                result = await session.call_tool(tool_name, arguments=args)

                result_text = "\n".join(
                    [c.text for c in result.content if c.type == "text"]
                )

                print(f"📦 Tool result: {result_text}")

                # 🧠 Send tool result back to LLM for final human-readable answer
                messages.append(choice.message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": result_text,
                })

                final = await llm_call(
                    client,
                    model=MODEL,
                    messages=messages,
                )

                print(f"\n🤖 Assistant: {final.choices[0].message.content}\n")

            else:
                print(f"\n🤖 Assistant: {choice.message.content}\n")

        except Exception as inner_err:
            if isinstance(inner_err, BaseExceptionGroup):
                for exc in inner_err.exceptions:
                    print(f"\n❌ Sub-error: {type(exc).__name__}: {exc}")
            else:
                print(f"\n❌ Error: {type(inner_err).__name__}: {inner_err}")
                traceback.print_exc()


async def main():
    if not API_KEY:
        print("❌ Set API_KEY in .env file")
        return

    # 🔑 OpenRouter client (with extended timeout for free-tier models)
    llm = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
        timeout=120.0,   # free models can be slow
    )

    # 🌐 MCP Server URL
    url = "http://localhost:8000/sse"
    print(f"Connecting to MCP server at {url}...")

    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("✅ Connected to MCP server!")

                # 📦 Get available tools
                tools_response = await session.list_tools()

                # 🔄 Convert MCP tools → OpenAI format
                openai_tools = []
                for tool in tools_response.tools:
                    openai_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    })

                # Run the interaction loop
                await run_session(session, llm, openai_tools)

    except Exception as e:
        if isinstance(e, BaseExceptionGroup):
            print("\n❌ Connection error (details):")
            for exc in e.exceptions:
                print(f"   • {type(exc).__name__}: {exc}")
        else:
            print(f"\n❌ Error: {type(e).__name__}: {e}")
            traceback.print_exc()
        print("👉 Make sure server is running: python server.py")


if __name__ == "__main__":
    asyncio.run(main())