#!/bin/bash

echo "=================================="
echo "Amazon SP-API Credentials Check"
echo "=================================="
echo ""

ENV_FILE="amazon-mcp-server/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: $ENV_FILE not found"
    echo ""
    echo "Please create the file with your credentials:"
    echo "  SP_API_CLIENT_ID=your_client_id_here"
    echo "  SP_API_CLIENT_SECRET=your_client_secret_here"
    echo "  SP_API_REFRESH_TOKEN=your_refresh_token_here"
    echo "  SP_API_MARKETPLACE_ID=ATVPDKIKX0DER"
    echo "  SP_API_REGION=us-east-1"
    exit 1
fi

echo "Checking credentials in $ENV_FILE:"
echo ""

check_var() {
    var_name=$1
    if grep -q "^${var_name}=" "$ENV_FILE"; then
        value=$(grep "^${var_name}=" "$ENV_FILE" | cut -d '=' -f 2)
        if [ "$value" = "your_client_id_here" ] || [ "$value" = "your_client_secret_here" ] || [ "$value" = "your_refresh_token_here" ]; then
            echo "⚠️  $var_name: NOT CONFIGURED (still has placeholder)"
        elif [ -z "$value" ]; then
            echo "❌ $var_name: EMPTY"
        else
            # Show first 10 chars
            preview="${value:0:20}..."
            echo "✅ $var_name: $preview"
        fi
    else
        echo "❌ $var_name: MISSING"
    fi
}

check_var "SP_API_CLIENT_ID"
check_var "SP_API_CLIENT_SECRET"
check_var "SP_API_REFRESH_TOKEN"
check_var "SP_API_MARKETPLACE_ID"
check_var "SP_API_REGION"

echo ""
echo "=================================="
echo ""

# Check Node.js
echo "Checking Node.js installation:"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js installed: $NODE_VERSION"
else
    echo "❌ Node.js not installed"
    echo "   Install with: brew install node"
fi

echo ""
