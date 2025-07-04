#!/bin/bash

echo "🔍 Testing different Cloudflare Worker URL patterns..."
echo "Worker name: design-gallery-worker"
echo "Account ID: 0b3de96b3a72833e38311290e9acfc3a"
echo ""

# Pattern 1: Standard format
echo "1. Testing: https://design-gallery-worker.0b3de96b3a72833e38311290e9acfc3a.workers.dev"
curl -s -o /dev/null -w "Status: %{http_code}\n" "https://design-gallery-worker.0b3de96b3a72833e38311290e9acfc3a.workers.dev/health" 2>/dev/null || echo "❌ Cannot resolve host"

# Pattern 2: Simplified format
echo "2. Testing: https://design-gallery-worker.workers.dev"
curl -s -o /dev/null -w "Status: %{http_code}\n" "https://design-gallery-worker.workers.dev/health" 2>/dev/null || echo "❌ Cannot resolve host"

# Pattern 3: With subdomain
echo "3. Testing: https://design-gallery-worker.shiva-venigalla.workers.dev"
curl -s -o /dev/null -w "Status: %{http_code}\n" "https://design-gallery-worker.shiva-venigalla.workers.dev/health" 2>/dev/null || echo "❌ Cannot resolve host"

# Pattern 4: Alternative format
echo "4. Testing: https://0b3de96b3a72833e38311290e9acfc3a.design-gallery-worker.workers.dev"
curl -s -o /dev/null -w "Status: %{http_code}\n" "https://0b3de96b3a72833e38311290e9acfc3a.design-gallery-worker.workers.dev/health" 2>/dev/null || echo "❌ Cannot resolve host"

echo ""
echo "✅ If any returned Status: 200, that's your URL!"
echo "❌ If all failed, check the Cloudflare Dashboard" 