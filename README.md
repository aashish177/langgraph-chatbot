# LangGraph Multi-Agent Chatbot with Amazon Seller Integration

An intelligent multi-agent chatbot built with LangGraph that routes conversations to specialized agents and integrates with Amazon Seller Partner API via a custom MCP (Model Context Protocol) server.

## Features

### Multi-Agent Routing
- **Emotional Support Agent**: Provides empathetic responses for emotional queries
- **Logical Agent**: Handles factual and analytical questions
- **Amazon Seller Agent**: Access real-time Amazon seller data with tool calling

### Amazon Seller Integration
- **No AWS Required**: Direct SP-API access using only OAuth credentials
- **Real-time Data**: Query orders, inventory, listings, and sales metrics
- **MCP Architecture**: Clean separation between Python agent and Node.js SP-API client
- **Tool Calling**: LLM automatically selects and executes appropriate tools

### Available Amazon Tools
1. **Get Orders** - Retrieve orders with optional date filtering
2. **Get Inventory** - View current inventory levels and fulfillment details
3. **Get Listings** - Access product listings by SKU or all listings
4. **Get Sales Metrics** - Analyze sales data by day, week, or month

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input                                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│               Message Classifier                             │
│  (Determines: emotional | logical | amazon_query)            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Router                                    │
│         Routes to appropriate agent                          │
└─────┬─────────────────┬─────────────────┬──────────────────┘
      │                 │                 │
      ▼                 ▼                 ▼
┌──────────┐    ┌──────────┐    ┌────────────────────────────┐
│Therapist │    │ Logical  │    │   Amazon Seller Agent      │
│  Agent   │    │  Agent   │    │                            │
└──────────┘    └──────────┘    │ ┌────────────────────────┐ │
                                │ │ Python MCP Client      │ │
                                │ └───────────┬────────────┘ │
                                │             │ stdio        │
                                │             ▼              │
                                │ ┌────────────────────────┐ │
                                │ │ Node.js MCP Server     │ │
                                │ │ (SP-API Client)        │ │
                                │ └───────────┬────────────┘ │
                                │             │ HTTPS        │
                                │             ▼              │
                                │ ┌────────────────────────┐ │
                                │ │ Amazon SP-API          │ │
                                │ └────────────────────────┘ │
                                └────────────────────────────┘
```

## Prerequisites

- **Python 3.13+**
- **Node.js 16+**
- **OpenAI API Key** (for GPT-4o-mini)
- **Amazon Seller Account** with SP-API access
- **Amazon SP-API Credentials**:
  - LWA Client ID
  - LWA Client Secret
  - Refresh Token

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd langgraph-project
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Install Python dependencies
uv sync
# or
pip install -r requirements.txt
```

### 3. Set Up Node.js MCP Server

```bash
cd amazon-mcp-server
npm install
cd ..
```

### 4. Configure Environment Variables

**Main Project (.env):**
```bash
# OpenAI API Key
LLM_API_KEY=sk-proj-your-openai-api-key-here
```

**Amazon MCP Server (amazon-mcp-server/.env):**
```bash
SP_API_CLIENT_ID=amzn1.application-oa2-client.your-client-id
SP_API_CLIENT_SECRET=amzn1.oa2-cs.v1.your-client-secret
SP_API_REFRESH_TOKEN=Atzr|your-refresh-token-here
SP_API_MARKETPLACE_ID=ATVPDKIKX0DER
SP_API_REGION=us-east-1
```

## Getting Amazon SP-API Credentials

### Step 1: Register as SP-API Developer

1. Go to [Amazon Seller Central](https://sellercentral.amazon.com)
2. Navigate to **Apps & Services** → **Develop Apps**
3. Click **Add New App Client**

### Step 2: Create Your App

Fill out the form:
- **App Name**: Your app name (e.g., "My Inventory Tool")
- **OAuth Redirect URI**: `https://localhost` (for testing)
- **IAM Role ARN**: Leave blank for single-seller use

Click **Save** to get:
- ✅ **LWA Client ID**
- ✅ **LWA Client Secret**

### Step 3: Get Refresh Token

Follow Amazon's [OAuth authorization flow](https://developer-docs.amazon.com/sp-api/docs/authorizing-selling-partner-api-applications) to obtain your refresh token.

**Quick method for self-authorization:**

1. Open this URL in browser (replace `YOUR_CLIENT_ID`):
```
https://sellercentral.amazon.com/apps/authorize/consent?application_id=YOUR_CLIENT_ID&redirect_uri=https://localhost
```

2. Click "Authorize" and copy the authorization code from the redirect URL

3. Exchange code for refresh token:
```bash
curl -X POST https://api.amazon.com/auth/o2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_AUTH_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=https://localhost"
```

4. Save the `refresh_token` from the response

### Marketplace IDs

Common marketplace IDs:
- **US**: `ATVPDKIKX0DER`
- **Canada**: `A2EUQ1WTGCTBG2`
- **Mexico**: `A1AM78C64UM0Y8`
- **UK**: `A1F83G8C2ARO7P`

[Full list of marketplace IDs](https://developer-docs.amazon.com/sp-api/docs/marketplace-ids)

## Usage

### Run the Chatbot

```bash
python main.py
```

### Example Interactions

**Emotional Support:**
```
You: I'm feeling stressed about work
Assistant: I hear that you're feeling stressed about work...
```

**Logical Questions:**
```
You: What is the capital of France?
Assistant: The capital of France is Paris.
```

**Amazon Seller Queries:**
```
You: What are my orders from today?
Assistant: You have 3 orders today:
1. Order #113-5128268-1592224
   - Status: Pending
   - Total: $49.99
   - Items: 1
...
```

```
You: Show me my inventory levels
Assistant: Your current inventory summary:
- Total SKUs: 45
- Available units: 1,247
- Inbound units: 350
...
```

```
You: What are my sales metrics for this week?
Assistant: Sales metrics for this week:
- Total orders: 87
- Total revenue: $4,523.45
- Units sold: 156
...
```

## Testing

### Test Scripts Included

**1. Check Credentials**
```bash
./check_credentials.sh
```

**2. Test SP-API Connection (Node.js)**
```bash
cd amazon-mcp-server
node test-connection.js
```

**3. Test MCP Integration (Python)**
```bash
python test_mcp_client.py
```

**4. Test Full Agent**
```bash
python main.py
# Try: "How many orders today?"
```

## Project Structure

```
langgraph-project/
├── main.py                    # Main LangGraph agent with routing
├── amazon_agent.py            # Amazon tool factory & LangChain integration
├── mcp_client.py              # Python MCP client
├── test_mcp_client.py         # Integration test script
├── check_credentials.sh       # Credential validation script
├── pyproject.toml             # Python dependencies
├── .env                       # OpenAI API key
├── .venv/                     # Python virtual environment
│
├── amazon-mcp-server/         # Node.js MCP Server
│   ├── index.js               # MCP server entry point
│   ├── sp-api-client.js       # SP-API wrapper (no AWS!)
│   ├── tools.js               # MCP tool definitions
│   ├── test-connection.js     # SP-API connection test
│   ├── package.json           # Node.js dependencies
│   ├── .env                   # SP-API credentials
│   └── node_modules/          # Node.js packages
│
├── AMAZON_MCP_SETUP.md        # Detailed setup guide
└── README.md                  # This file
```

## How It Works

### Message Classification
The chatbot uses GPT-4o-mini to classify incoming messages:

```python
Literal["emotional", "logical", "amazon_query"]
```

### Agent Routing
Based on classification, the router directs to the appropriate agent:

| Classification | Agent | Capabilities |
|---------------|-------|--------------|
| `emotional` | Therapist Agent | Empathy, emotional support |
| `logical` | Logical Agent | Facts, analysis, information |
| `amazon_query` | Amazon Seller Agent | SP-API data via tools |

### Tool Calling Flow

1. **User asks**: "What are my orders?"
2. **Classifier**: Detects `amazon_query`
3. **Router**: Sends to Amazon Seller Agent
4. **LLM**: Decides to call `get_orders` tool
5. **Python**: Executes tool → connects to MCP server
6. **Node.js MCP Server**: Makes SP-API request
7. **Amazon SP-API**: Returns order data
8. **Response flows back** through the chain
9. **LLM**: Formats data into natural language
10. **User sees**: "You have 3 orders today..."

## Why No AWS Required?

This implementation uses **LWA (Login with Amazon) OAuth only** for authentication, bypassing the typical AWS Signature V4 requirement.

### Traditional Approach (With AWS)
```
Authentication:
├── LWA OAuth (Client ID, Secret, Refresh Token)
└── AWS SigV4 (Access Key, Secret Key, IAM Role)
```

### Our Approach (Without AWS)
```
Authentication:
└── LWA OAuth (Client ID, Secret, Refresh Token)
```

**Why this works:**
- For **single-seller** access (your own account), Amazon SP-API accepts just the LWA access token
- AWS credentials are only required for **multi-seller SaaS applications**
- Simpler setup, fewer dependencies, no AWS account needed!

## Adding More Tools

### 1. Add SP-API Method

Edit `amazon-mcp-server/sp-api-client.js`:

```javascript
async getFinancialEvents() {
  const endpoint = `/finances/v0/financialEvents`;
  return await this.makeRequest(endpoint);
}
```

### 2. Define MCP Tool

Edit `amazon-mcp-server/tools.js`:

```javascript
{
  name: 'get_financial_events',
  description: 'Get financial events including payments and refunds',
  inputSchema: {
    type: 'object',
    properties: {},
  },
}
```

### 3. Add Tool Handler

Edit `amazon-mcp-server/index.js`:

```javascript
case 'get_financial_events':
  result = await spApiClient.getFinancialEvents();
  break;
```

### 4. Create LangChain Tool

Edit `amazon_agent.py`:

```python
def get_financial_events() -> str:
    """Get financial events"""
    result = asyncio.run(self._call_tool("get_financial_events", {}))
    return result

tools.append(StructuredTool.from_function(
    func=get_financial_events,
    name="get_financial_events",
    description="Get financial events including payments and refunds"
))
```

## Troubleshooting

### "Failed to get access token"
- ✅ Check `SP_API_CLIENT_ID` is correct
- ✅ Check `SP_API_CLIENT_SECRET` is correct
- ✅ Verify `SP_API_REFRESH_TOKEN` hasn't expired
- ✅ Ensure no extra quotes or spaces in `.env` file

### "403 Forbidden"
- ✅ Your app may not have permission for that endpoint
- ✅ Check app permissions in Amazon Seller Central
- ✅ Some endpoints require additional authorization

### "Cannot connect to MCP server"
- ✅ Ensure Node.js is installed: `node --version`
- ✅ Check `amazon-mcp-server/` directory exists
- ✅ Verify `.env` file exists in `amazon-mcp-server/`
- ✅ Run `npm install` in `amazon-mcp-server/`

### Blank responses from agent
- ✅ Check OpenAI API key is valid
- ✅ Verify you have API credits
- ✅ Look for errors in console output
- ✅ Test with simple query: "What is 2+2?"

### MCP protocol errors
- ✅ Ensure `dotenv` isn't printing to stdout
- ✅ Check Node.js server starts without errors
- ✅ Test standalone: `cd amazon-mcp-server && node index.js`

## Configuration

### Custom Marketplace

Edit `amazon-mcp-server/.env`:
```bash
SP_API_MARKETPLACE_ID=A1F83G8C2ARO7P  # UK
SP_API_REGION=eu-west-1
```

### Change LLM Model

Edit `main.py`:
```python
llm = init_chat_model(
    model="gpt-4",  # Use GPT-4 instead of GPT-4o-mini
    model_provider="openai"
)
```

### Add Custom Agent

1. Create agent function in `main.py`
2. Add to `MessageClassifier` literal types
3. Update classifier prompt
4. Add routing logic
5. Register node in graph builder

## Dependencies

### Python
- **langgraph** (>=0.6.10) - State graph for agent workflows
- **langchain-openai** (>=0.3.35) - OpenAI integration
- **langchain** (>=0.3.27) - LangChain core
- **python-dotenv** (>=1.1.1) - Environment variable management
- **mcp** (>=1.0.0) - Model Context Protocol client
- **pydantic** - Data validation and structured outputs

### Node.js
- **@modelcontextprotocol/sdk** - MCP server SDK
- **dotenv** - Environment variable loading
- **node-fetch** - HTTP client for API requests

## Resources

- [Amazon SP-API Documentation](https://developer-docs.amazon.com/sp-api/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section
- Review `AMAZON_MCP_SETUP.md` for detailed setup help
- Open an issue on GitHub

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Uses [Model Context Protocol](https://modelcontextprotocol.io/)
- Powered by [OpenAI GPT-4o-mini](https://openai.com/)
- Amazon SP-API integration without AWS complexity

---

**Made with ❤️ for Amazon Sellers**
