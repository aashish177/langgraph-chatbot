#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import SPAPIClient from './sp-api-client.js';
import { tools } from './tools.js';

// Load environment variables manually to avoid dotenv's stdout pollution
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const envPath = join(__dirname, '.env');

try {
  const envFile = readFileSync(envPath, 'utf8');
  envFile.split('\n').forEach(line => {
    const match = line.match(/^([^=:#]+?)\s*=\s*(.*)?\s*$/);
    if (match) {
      const key = match[1].trim();
      let value = match[2] ? match[2].trim() : '';
      // Remove quotes if present
      value = value.replace(/^['"](.*)['"]$/, '$1');
      process.env[key] = value;
    }
  });
} catch (error) {
  // .env file not found or error reading it
  console.error('Warning: Could not load .env file');
}

// Initialize SP-API client
const spApiClient = new SPAPIClient({
  clientId: process.env.SP_API_CLIENT_ID,
  clientSecret: process.env.SP_API_CLIENT_SECRET,
  refreshToken: process.env.SP_API_REFRESH_TOKEN,
  marketplaceId: process.env.SP_API_MARKETPLACE_ID,
  region: process.env.SP_API_REGION || 'us-east-1',
});

// Create MCP server
const server = new Server(
  {
    name: 'amazon-seller-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result;

    switch (name) {
      case 'get_orders':
        result = await spApiClient.getOrders(args);
        break;

      case 'get_inventory':
        result = await spApiClient.getInventory();
        break;

      case 'get_listings':
        result = await spApiClient.getListings(args);
        break;

      case 'get_sales_metrics':
        result = await spApiClient.getSalesMetrics(args);
        break;

      default:
        throw new Error(`Unknown tool: ${name}`);
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Amazon Seller MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
