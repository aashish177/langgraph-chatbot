import asyncio
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

class AmazonMCPClient:
    """Manages connection to Amazon Seller MCP Server"""

    def __init__(self):
        self.session = None
        self.available_tools = []
        self.server_path = os.path.join(os.getcwd(), "amazon-mcp-server")

    @asynccontextmanager
    async def connect(self):
        """Connect to the MCP server and yield the session"""

        # Configure server parameters
        server_params = StdioServerParameters(
            command="node",
            args=["index.js"],
            env=None,  # Server will load its own .env
            cwd=self.server_path
        )

        # Connect via stdio
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()

                # List available tools from server
                tools_list = await session.list_tools()
                self.available_tools = tools_list.tools

                print(f"✓ Connected to Amazon MCP server")
                print(f"✓ Available tools: {len(self.available_tools)}")

                self.session = session
                yield session

    async def call_tool(self, tool_name: str, arguments: dict = None):
        """Call a specific MCP tool"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        args = arguments or {}
        result = await self.session.call_tool(tool_name, args)
        return result

    def get_tools_info(self):
        """Get information about available tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in self.available_tools
        ]

# Test function
async def test_connection():
    """Test the MCP connection"""
    client = AmazonMCPClient()

    async with client.connect() as session:
        print("\nAvailable tools:")
        for tool in client.available_tools:
            print(f"  - {tool.name}: {tool.description}")

        # Test get_orders
        print("\nTesting get_orders tool...")
        try:
            result = await client.call_tool("get_orders", {})
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
