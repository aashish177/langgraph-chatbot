import fetch from 'node-fetch';

class SPAPIClient {
  constructor(config) {
    this.clientId = config.clientId;
    this.clientSecret = config.clientSecret;
    this.refreshToken = config.refreshToken;
    this.marketplaceId = config.marketplaceId;
    this.region = config.region;
    this.accessToken = null;
    this.tokenExpiry = null;
  }

  // Get access token using LWA OAuth (same as Postman)
  async getAccessToken() {
    // Reuse token if still valid
    if (this.accessToken && this.tokenExpiry && Date.now() < this.tokenExpiry) {
      return this.accessToken;
    }

    const response = await fetch('https://api.amazon.com/auth/o2/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'refresh_token',
        refresh_token: this.refreshToken,
        client_id: this.clientId,
        client_secret: this.clientSecret,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to get access token: ${response.status} ${errorText}`);
    }

    const data = await response.json();
    this.accessToken = data.access_token;
    this.tokenExpiry = Date.now() + (data.expires_in * 1000) - 60000; // Refresh 1 min early

    return this.accessToken;
  }

  // Make SP-API request
  async makeRequest(endpoint, method = 'GET', body = null) {
    const accessToken = await this.getAccessToken();

    const baseUrl = `https://sellingpartnerapi-na.amazon.com`;
    const url = `${baseUrl}${endpoint}`;

    const options = {
      method,
      headers: {
        'x-amz-access-token': accessToken,
        'Content-Type': 'application/json',
      },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`SP-API request failed: ${response.status} ${errorText}`);
    }

    return await response.json();
  }

  // Tool methods
  async getOrders(params = {}) {
    const { createdAfter, marketplaceIds } = params;
    const marketplace = marketplaceIds || this.marketplaceId;

    // Default to orders from last 7 days if no date specified
    let dateFilter = createdAfter;
    if (!dateFilter) {
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
      dateFilter = sevenDaysAgo.toISOString();
    }

    let endpoint = `/orders/v0/orders?MarketplaceIds=${marketplace}&CreatedAfter=${dateFilter}`;

    return await this.makeRequest(endpoint);
  }

  async getInventory() {
    const endpoint = `/fba/inventory/v1/summaries?details=true&granularityType=Marketplace&granularityId=${this.marketplaceId}&marketplaceIds=${this.marketplaceId}`;
    return await this.makeRequest(endpoint);
  }

  async getListings(params = {}) {
    const { sku } = params;
    const endpoint = sku
      ? `/listings/2021-08-01/items/${this.marketplaceId}/${sku}`
      : `/listings/2021-08-01/items/${this.marketplaceId}`;

    return await this.makeRequest(endpoint);
  }

  async getSalesMetrics(params = {}) {
    const { interval = 'DAY', granularity = 'Total' } = params;
    const endpoint = `/sales/v1/orderMetrics?marketplaceIds=${this.marketplaceId}&interval=${interval}&granularity=${granularity}`;
    return await this.makeRequest(endpoint);
  }
}

export default SPAPIClient;
