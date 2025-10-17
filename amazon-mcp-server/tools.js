export const tools = [
  {
    name: 'get_orders',
    description: 'Get orders from Amazon Seller account. Can filter by creation date.',
    inputSchema: {
      type: 'object',
      properties: {
        createdAfter: {
          type: 'string',
          description: 'ISO 8601 date (e.g., 2024-01-01T00:00:00Z). Get orders created after this date.',
        },
      },
    },
  },
  {
    name: 'get_inventory',
    description: 'Get current inventory summary including available quantity, inbound quantity, and fulfillment channel.',
    inputSchema: {
      type: 'object',
      properties: {},
    },
  },
  {
    name: 'get_listings',
    description: 'Get product listings. Can get specific SKU or all listings.',
    inputSchema: {
      type: 'object',
      properties: {
        sku: {
          type: 'string',
          description: 'Specific SKU to retrieve. If omitted, returns all listings.',
        },
      },
    },
  },
  {
    name: 'get_sales_metrics',
    description: 'Get sales metrics including order count, total sales, and units ordered.',
    inputSchema: {
      type: 'object',
      properties: {
        interval: {
          type: 'string',
          description: 'Time interval: DAY, WEEK, or MONTH',
          enum: ['DAY', 'WEEK', 'MONTH'],
        },
      },
    },
  },
];
