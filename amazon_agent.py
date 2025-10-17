from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from mcp_client import AmazonMCPClient
import asyncio
from typing import Optional

# Pydantic models for tool inputs
class GetOrdersInput(BaseModel):
    createdAfter: Optional[str] = Field(None, description="ISO 8601 date to filter orders")

class GetListingsInput(BaseModel):
    sku: Optional[str] = Field(None, description="Specific SKU to retrieve")

class GetSalesMetricsInput(BaseModel):
    interval: Optional[str] = Field("DAY", description="Time interval: DAY, WEEK, or MONTH")

class AmazonToolsFactory:
    """Creates LangChain tools from MCP Amazon tools"""

    def __init__(self):
        self.mcp_client = AmazonMCPClient()

    async def create_tools(self):
        """Create all Amazon tools for LangChain"""

        # Test connection and get available tools
        async with self.mcp_client.connect():
            tools_info = self.mcp_client.get_tools_info()

        # Create LangChain tools
        tools = []

        # Get Orders tool
        def get_orders(createdAfter: Optional[str] = None) -> str:
            """Get orders from Amazon Seller account"""
            args = {}
            if createdAfter:
                args["createdAfter"] = createdAfter

            result = asyncio.run(self._call_tool("get_orders", args))
            return result

        tools.append(StructuredTool.from_function(
            func=get_orders,
            name="get_orders",
            description="Get orders from Amazon Seller account. Can filter by creation date.",
            args_schema=GetOrdersInput
        ))

        # Get Inventory tool
        def get_inventory() -> str:
            """Get current inventory summary"""
            result = asyncio.run(self._call_tool("get_inventory", {}))
            return result

        tools.append(StructuredTool.from_function(
            func=get_inventory,
            name="get_inventory",
            description="Get current inventory summary including available quantity and fulfillment details."
        ))

        # Get Listings tool
        def get_listings(sku: Optional[str] = None) -> str:
            """Get product listings"""
            args = {}
            if sku:
                args["sku"] = sku

            result = asyncio.run(self._call_tool("get_listings", args))
            return result

        tools.append(StructuredTool.from_function(
            func=get_listings,
            name="get_listings",
            description="Get product listings. Can get specific SKU or all listings.",
            args_schema=GetListingsInput
        ))

        # Get Sales Metrics tool
        def get_sales_metrics(interval: str = "DAY") -> str:
            """Get sales metrics"""
            result = asyncio.run(self._call_tool("get_sales_metrics", {"interval": interval}))
            return result

        tools.append(StructuredTool.from_function(
            func=get_sales_metrics,
            name="get_sales_metrics",
            description="Get sales metrics including order count, total sales, and units ordered.",
            args_schema=GetSalesMetricsInput
        ))

        return tools

    async def _call_tool(self, tool_name: str, arguments: dict):
        """Helper to call MCP tool"""
        async with self.mcp_client.connect() as session:
            result = await session.call_tool(tool_name, arguments)
            # Extract text content from result
            if result.content and len(result.content) > 0:
                return result.content[0].text
            return str(result)

# Function to get tools (called from main.py)
def get_amazon_tools():
    """Get Amazon tools for LangChain"""
    factory = AmazonToolsFactory()
    tools = asyncio.run(factory.create_tools())
    return tools
