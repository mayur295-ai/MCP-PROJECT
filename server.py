import sys
from mcp.src.server.fastmcp import FastMCP

# Initialize FastMCP named ToolServer
mcp = FastMCP("ToolServer")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together.
    
    Args:
        a: First number to add.
        b: Second number to add.
    """
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together.
    
    Args:
        a: First number to multiply.
        b: Second number to multiply.
    """
    return a * b

@mcp.tool()
def greet(name: str) -> str:
    """Greet a person by their name.
    
    Args:
        name: Name of the person to greet.
    """
    return f"Hello, {name}!"

if __name__ == "__main__":
    print("Starting MCP server with FastMCP on http://localhost:8000/sse ...", file=sys.stderr)
    # Start the server using Server-Sent Events (SSE) transport
    mcp.run(transport='sse')
