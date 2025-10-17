# Amazon Seller MCP Server Setup

This guide will help you set up and use the Amazon Seller MCP server with your LangGraph agent.

## Prerequisites

- Node.js 16+ installed
- Python 3.13+
- Amazon Seller account with SP-API access
- SP-API credentials (Client ID, Client Secret, Refresh Token)

## Setup Steps

### 1. Configure Amazon SP-API Credentials

Edit the file `amazon-mcp-server/.env` and add your credentials:

```env
SP_API_CLIENT_ID=your_client_id_here
SP_API_CLIENT_SECRET=your_client_secret_here
SP_API_REFRESH_TOKEN=your_refresh_token_here
SP_API_MARKETPLACE_ID=ATVPDKIKX0DER
SP_API_REGION=us-east-1
```

**How to get these credentials:**

1. **Client ID & Secret**:
   - Go to Amazon Seller Central
   - Navigate to Apps & Services → Develop Apps
   - Create a new app or use existing app
   - Copy the LWA Client ID and Client Secret

2. **Refresh Token**:
   - Follow Amazon's OAuth flow to authorize your app
   - You'll receive a refresh token that you can use indefinitely
   - See: https://developer-docs.amazon.com/sp-api/docs/authorizing-selling-partner-api-applications

3. **Marketplace ID**:
   - US: ATVPDKIKX0DER
   - Canada: A2EUQ1WTGCTBG2
   - Mexico: A1AM78C64UM0Y8
   - Full list: https://developer-docs.amazon.com/sp-api/docs/marketplace-ids

### 2. Test MCP Server Standalone

Test that the Node.js MCP server can connect to Amazon SP-API:

```bash
cd amazon-mcp-server
node index.js
```

You should see: `Amazon Seller MCP Server running on stdio`

Press Ctrl+C to stop.

### 3. Test Python MCP Client

Test that Python can connect to the MCP server:

```bash
python mcp_client.py
```

You should see:
```
✓ Connected to Amazon MCP server
✓ Available tools: 4

Available tools:
  - get_orders: Get orders from Amazon Seller account...
  - get_inventory: Get current inventory summary...
  - get_listings: Get product listings...
  - get_sales_metrics: Get sales metrics...
```

### 4. Run the Full LangGraph Agent

```bash
python main.py
```

You should see:
```
Loading Amazon tools...
✓ Connected to Amazon MCP server
✓ Available tools: 4
✓ Loaded 4 Amazon tools

Chatbot ready! (type 'quit' to exit)
Try: 'What's my current inventory?' or 'How many orders today?'
```

## Available Tools

The MCP server exposes 4 tools:

1. **get_orders** - Get orders from your Amazon seller account
   - Optional parameter: `createdAfter` (ISO 8601 date)
   - Example: "Show me orders from the last week"

2. **get_inventory** - Get current inventory summary
   - No parameters required
   - Example: "What's my current inventory?"

3. **get_listings** - Get product listings
   - Optional parameter: `sku` (specific SKU)
   - Example: "Show me all my product listings"

4. **get_sales_metrics** - Get sales metrics
   - Optional parameter: `interval` (DAY, WEEK, or MONTH)
   - Example: "What are my daily sales metrics?"

## Example Queries

Try asking your agent:

- "What's my current inventory?"
- "Show me today's orders"
- "How many orders did I get yesterday?"
- "What are my weekly sales metrics?"
- "Show me all my product listings"
- "Get inventory for SKU ABC123"

## Troubleshooting

### Error: "Failed to get access token"
- Check that your SP_API_CLIENT_ID, SP_API_CLIENT_SECRET, and SP_API_REFRESH_TOKEN are correct
- Ensure your refresh token hasn't expired

### Error: "SP-API request failed: 403"
- Your app may not have permission for that endpoint
- Check your app permissions in Seller Central

### Error: "Cannot connect to Amazon MCP server"
- Make sure Node.js is installed: `node --version`
- Check that `amazon-mcp-server/` directory exists
- Verify `.env` file exists in `amazon-mcp-server/`

### MCP server doesn't start
- Run `cd amazon-mcp-server && npm install` to ensure dependencies are installed
- Check for syntax errors: `node index.js`

## Project Structure

```
langgraph-project/
├── main.py                    # Main LangGraph agent
├── amazon_agent.py            # Amazon agent integration
├── mcp_client.py              # Python MCP client
├── pyproject.toml             # Python dependencies
├── .env                       # OpenAI API key
│
└── amazon-mcp-server/         # Custom MCP server
    ├── index.js               # MCP server entry point
    ├── sp-api-client.js       # SP-API wrapper (no AWS)
    ├── tools.js               # Tool definitions
    ├── package.json           # Node.js dependencies
    └── .env                   # SP-API credentials
```

## Adding More Tools

To add more Amazon SP-API endpoints:

1. Add method to `amazon-mcp-server/sp-api-client.js`
2. Add tool definition to `amazon-mcp-server/tools.js`
3. Add case to switch statement in `amazon-mcp-server/index.js`
4. Add LangChain tool wrapper in `amazon_agent.py`

## Notes

- This implementation uses **only LWA OAuth** (no AWS credentials needed)
- Access tokens are automatically refreshed when expired
- The MCP server runs as a subprocess when you run `main.py`
- All SP-API requests go through the secure MCP protocol

## Resources

- [Amazon SP-API Documentation](https://developer-docs.amazon.com/sp-api/)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
