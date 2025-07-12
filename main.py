from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("test-mcp")


# Add an addition tool
@mcp.tool()
def sum(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://name")
def get_greeting() -> str:
    """Get a personalized greeting"""
    return f"Hello, Laurenz!"


# # Run the server
# if __name__ == "__main__":
#     mcp.run(transport="sse")