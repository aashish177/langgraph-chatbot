"""
Simple test script to verify MCP client connection to Amazon MCP server
"""
import asyncio
import sys
from mcp_client import AmazonMCPClient


async def test_connection():
    print("Testing MCP Client → MCP Server → Amazon SP-API\n")

    client = AmazonMCPClient()

    try:
        print("Step 1: Connecting to MCP server...")
        async with client.connect() as session:
            print("✓ Connected to MCP server\n")

            # List available tools
            print("Step 2: Listing available tools...")
            tools_info = client.get_tools_info()
            print(f"✓ Found {len(tools_info)} tools:\n")
            for tool in tools_info:
                print(f"  - {tool['name']}: {tool['description']}")
            print()

            # Test calling a tool
            print("Step 3: Testing get_orders tool...")
            result = await client.call_tool("get_orders", {})

            # Check if we got a valid response
            if result.content and len(result.content) > 0:
                response_text = result.content[0].text

                # Check for error
                if response_text.startswith("Error:"):
                    print(f"✗ Tool call failed: {response_text}\n")
                    print("Troubleshooting:")
                    print("1. Check your credentials in amazon-mcp-server/.env")
                    print("2. Make sure your refresh token is valid")
                    print("3. Verify your app has permissions for Orders API")
                    sys.exit(1)
                else:
                    print("✓ Successfully called SP-API via MCP server")
                    print(f"  Response preview: {response_text[:200]}...\n")

            print("🎉 All tests passed! Your MCP integration is working.")

    except ConnectionError as e:
        print(f"✗ Connection error: {e}\n")
        print("Troubleshooting:")
        print("1. Make sure Node.js is installed: node --version")
        print("2. Check that amazon-mcp-server/ directory exists")
        print("3. Verify .env file exists in amazon-mcp-server/")
        sys.exit(1)

    except Exception as e:
        print(f"✗ Unexpected error: {e}\n")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Amazon MCP Client Test")
    print("=" * 60)
    print()

    asyncio.run(test_connection())
