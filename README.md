# MCP-PROJECT 🤖

**Minimal, production-quality MCP agent with LLM-driven tool calling via OpenRouter.**

Demonstrates the full Model Context Protocol flow: LLM decides which tool to call → forwards to MCP server → executes → returns final response.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model_Context_Protocol-6B21A8)
![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-FF6B35)
![AsyncIO](https://img.shields.io/badge/Async-AsyncIO-00BFFF)

---

## How It Works

```
You (terminal input)
        │
        ▼
┌───────────────────┐
│    client.py      │  ← sends prompt + tool schemas to LLM via OpenRouter
│  (OpenRouter LLM) │
└────────┬──────────┘
         │  LLM decides: "I need tool X with args Y"
         ▼
┌───────────────────┐
│    server.py      │  ← MCP server exposes registered Python tools via SSE
│  (MCP Server)     │
└────────┬──────────┘
         │  tool executes, returns result
         ▼
┌───────────────────┐
│    client.py      │  ← sends tool result back to LLM for final response
└───────────────────┘
         │
         ▼
  Terminal output
```

---

## Quickstart

```bash
git clone https://github.com/mayur295-ai/MCP-PROJECT
cd MCP-PROJECT
pip install -r requirements.txt
# Add your OpenRouter API key to .env
```

**Terminal 1 — start the MCP server:**
```bash
python server.py
```

**Terminal 2 — start the client:**
```bash
python client.py
```

---

## Example Session

```
You: add 5 and 3
[LLM → tool: add(5, 3) → MCP server → result: 8]
Agent: The result is 8.

You: multiply 4 and 6
[LLM → tool: multiply(4, 6) → MCP server → result: 24]
Agent: 4 multiplied by 6 equals 24.

You: greet Mayuresh
[LLM → tool: greet("Mayuresh") → MCP server → result: "Hello, Mayuresh!"]
Agent: Hello, Mayuresh!
```

---

## Files

| File | Purpose |
|------|---------|
| `server.py` | MCP server — registers and exposes tools via SSE transport |
| `client.py` | MCP client — connects LLM to server, handles tool call loop |
| `requirements.txt` | Dependencies |
| `.env` | API key (not committed) |

---

## Stack

- **Python 3.10+**
- **Model Context Protocol (MCP)** — tool registration and SSE transport
- **OpenRouter** — LLM API (swap model via config)
- **AsyncIO** — non-blocking client/server communication

---

## Extending — Add Your Own Tools

In `server.py`, register a new tool:

```python
@mcp.tool()
def square(n: int) -> int:
    """Return the square of a number."""
    return n * n
```

Restart the server. The LLM will automatically discover and use it.

---

## Part of AURA_OS

This project explores the MCP protocol as a tool-dispatch layer for AURA_OS.
More complex agents with memory and edge inference are in:
- [ai-agent-memory](https://github.com/mayur295-ai/ai-agent-memory)
- [edge-ai-inference](https://github.com/mayur295-ai/edge-ai-inference)

---

*Built by [Mayuresh Chougule](https://github.com/mayur295-ai)*
