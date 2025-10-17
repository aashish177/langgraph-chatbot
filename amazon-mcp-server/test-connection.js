// Simple test script to verify SP-API connection
import SPAPIClient from './sp-api-client.js';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

async function testConnection() {
  console.log('Testing Amazon SP-API connection...\n');

  // Check credentials are loaded
  console.log('Checking credentials:');
  console.log('✓ Client ID:', process.env.SP_API_CLIENT_ID ? '✓ Present' : '✗ Missing');
  console.log('✓ Client Secret:', process.env.SP_API_CLIENT_SECRET ? '✓ Present' : '✗ Missing');
  console.log('✓ Refresh Token:', process.env.SP_API_REFRESH_TOKEN ? '✓ Present' : '✗ Missing');
  console.log('✓ Marketplace ID:', process.env.SP_API_MARKETPLACE_ID || 'Not set');
  console.log();

  // Initialize client
  const client = new SPAPIClient({
    clientId: process.env.SP_API_CLIENT_ID,
    clientSecret: process.env.SP_API_CLIENT_SECRET,
    refreshToken: process.env.SP_API_REFRESH_TOKEN,
    marketplaceId: process.env.SP_API_MARKETPLACE_ID,
    region: process.env.SP_API_REGION || 'us-east-1',
  });

  try {
    // Test 1: Get access token
    console.log('Test 1: Getting access token...');
    const token = await client.getAccessToken();
    console.log('✓ Successfully obtained access token');
    console.log('  Token preview:', token.substring(0, 20) + '...');
    console.log();

    // Test 2: Make a simple API call (get orders)
    console.log('Test 2: Making SP-API request (get orders)...');
    // Get orders from the last 7 days
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    const createdAfter = sevenDaysAgo.toISOString();

    const orders = await client.getOrders({ createdAfter });
    console.log('✓ Successfully connected to SP-API');
    console.log('  Response:', JSON.stringify(orders, null, 2).substring(0, 300) + '...');
    console.log();

    console.log('🎉 All tests passed! Your SP-API connection is working.');

  } catch (error) {
    console.error('✗ Error:', error.message);
    console.error();

    if (error.message.includes('Failed to get access token')) {
      console.error('Troubleshooting:');
      console.error('1. Check your SP_API_CLIENT_ID is correct');
      console.error('2. Check your SP_API_CLIENT_SECRET is correct');
      console.error('3. Check your SP_API_REFRESH_TOKEN is valid and not expired');
    } else if (error.message.includes('403')) {
      console.error('Troubleshooting:');
      console.error('1. Your app may not have permission for this endpoint');
      console.error('2. Check app permissions in Amazon Seller Central');
    } else if (error.message.includes('401')) {
      console.error('Troubleshooting:');
      console.error('1. Your access token may be invalid');
      console.error('2. Try regenerating your refresh token');
    }

    process.exit(1);
  }
}

testConnection();
