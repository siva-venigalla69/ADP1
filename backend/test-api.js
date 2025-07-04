const axios = require('axios');

// Configuration
const BASE_URL = 'http://localhost:8787'; // Change to your Worker URL
let authToken = '';
let adminToken = '';

// Colors for console output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// Test helper function
async function testEndpoint(name, method, url, data = null, headers = {}) {
  try {
    const config = {
      method,
      url: `${BASE_URL}${url}`,
      headers,
      ...(data && { data })
    };
    
    const response = await axios(config);
    log(`✅ ${name}: ${response.status} ${response.statusText}`, 'green');
    return response.data;
  } catch (error) {
    log(`❌ ${name}: ${error.response?.status || 'ERROR'} ${error.response?.statusText || error.message}`, 'red');
    if (error.response?.data) {
      console.log('   Error details:', error.response.data);
    }
    return null;
  }
}

// Test authentication endpoints
async function testAuth() {
  log('\n🔐 Testing Authentication Endpoints', 'blue');
  
  // Test registration
  const registerResponse = await testEndpoint(
    'User Registration',
    'POST',
    '/api/register',
    {
      username: 'testuser',
      password: 'testpass123'
    }
  );
  
  // Test login with regular user
  const loginResponse = await testEndpoint(
    'User Login',
    'POST',
    '/api/login',
    {
      username: 'testuser',
      password: 'testpass123'
    }
  );
  
  if (loginResponse?.token) {
    authToken = loginResponse.token;
    log(`   User token: ${authToken.substring(0, 20)}...`, 'yellow');
  }
  
  // Test admin login
  const adminLoginResponse = await testEndpoint(
    'Admin Login',
    'POST',
    '/api/login',
    {
      username: 'admin',
      password: 'admin123'
    }
  );
  
  if (adminLoginResponse?.token) {
    adminToken = adminLoginResponse.token;
    log(`   Admin token: ${adminToken.substring(0, 20)}...`, 'yellow');
  }
}

// Test design endpoints
async function testDesigns() {
  log('\n🎨 Testing Design Endpoints', 'blue');
  
  const authHeaders = { Authorization: `Bearer ${authToken}` };
  const adminHeaders = { Authorization: `Bearer ${adminToken}` };
  
  // Test get designs (empty initially)
  await testEndpoint('Get Designs', 'GET', '/api/designs', null, authHeaders);
  
  // Test get featured designs
  await testEndpoint('Get Featured Designs', 'GET', '/api/designs/featured', null, authHeaders);
  
  // Test create design (admin only)
  const createDesignResponse = await testEndpoint(
    'Create Design',
    'POST',
    '/api/designs',
    {
      title: 'Test Saree Design',
      description: 'A beautiful test saree',
      short_description: 'Beautiful test saree',
      long_description: 'This is a detailed description of a beautiful test saree with intricate patterns',
      r2_object_key: 'sarees/test_saree_123.jpg',
      category: 'Sarees',
      style: 'Traditional',
      colour: 'Red',
      fabric: 'Silk',
      occasion: 'Wedding',
      size_available: 'S,M,L,XL',
      price_range: 'Premium',
      tags: 'wedding,traditional,silk',
      featured: 1,
      designer_name: 'Test Designer',
      collection_name: 'Test Collection',
      season: 'Wedding'
    },
    adminHeaders
  );
  
  let designId = null;
  if (createDesignResponse?.design?.id) {
    designId = createDesignResponse.design.id;
    log(`   Created design ID: ${designId}`, 'yellow');
  }
  
  // Test get single design
  if (designId) {
    await testEndpoint(`Get Design ${designId}`, 'GET', `/api/designs/${designId}`, null, authHeaders);
    
    // Test record view
    await testEndpoint(`Record View ${designId}`, 'POST', `/api/designs/${designId}/view`, null, authHeaders);
    
    // Test update design
    await testEndpoint(
      `Update Design ${designId}`,
      'PUT',
      `/api/designs/${designId}`,
      {
        title: 'Updated Test Saree Design',
        featured: 0
      },
      adminHeaders
    );
  }
  
  // Test search
  await testEndpoint('Search Designs', 'GET', '/api/search?q=test&category=Sarees', null, authHeaders);
  
  // Test designs with filters
  await testEndpoint('Get Designs with Filters', 'GET', '/api/designs?category=Sarees&style=Traditional&featured=true', null, authHeaders);
}

// Test categories
async function testCategories() {
  log('\n📂 Testing Category Endpoints', 'blue');
  
  const authHeaders = { Authorization: `Bearer ${authToken}` };
  
  await testEndpoint('Get Categories', 'GET', '/api/categories', null, authHeaders);
}

// Test favorites
async function testFavorites() {
  log('\n❤️ Testing Favorites Endpoints', 'blue');
  
  const authHeaders = { Authorization: `Bearer ${authToken}` };
  
  await testEndpoint('Get Favorites', 'GET', '/api/favorites', null, authHeaders);
  
  // Test add to favorites (assuming design ID 1 exists)
  await testEndpoint('Add to Favorites', 'POST', '/api/favorites/1', null, authHeaders);
  
  // Test get favorites again
  await testEndpoint('Get Favorites After Add', 'GET', '/api/favorites', null, authHeaders);
  
  // Test remove from favorites
  await testEndpoint('Remove from Favorites', 'DELETE', '/api/favorites/1', null, authHeaders);
}

// Test admin endpoints
async function testAdmin() {
  log('\n👑 Testing Admin Endpoints', 'blue');
  
  const adminHeaders = { Authorization: `Bearer ${adminToken}` };
  
  // Test get users
  await testEndpoint('Get Users', 'GET', '/api/admin/users', null, adminHeaders);
  
  // Test approve user
  await testEndpoint(
    'Approve User',
    'POST',
    '/api/admin/approve-user',
    {
      userId: 2, // Assuming testuser has ID 2
      approved: true
    },
    adminHeaders
  );
  
  // Test upload URL generation
  await testEndpoint(
    'Generate Upload URL',
    'POST',
    '/api/admin/upload-url',
    {
      filename: 'test-image.jpg',
      category: 'sarees',
      contentType: 'image/jpeg'
    },
    adminHeaders
  );
  
  // Test analytics
  await testEndpoint('Get Analytics', 'GET', '/api/admin/analytics?period=7', null, adminHeaders);
}

// Test settings
async function testSettings() {
  log('\n⚙️ Testing Settings Endpoints', 'blue');
  
  const adminHeaders = { Authorization: `Bearer ${adminToken}` };
  
  // Test get settings (public)
  await testEndpoint('Get Settings', 'GET', '/api/settings');
  
  // Test update settings (admin only)
  await testEndpoint(
    'Update Settings',
    'PUT',
    '/api/admin/settings',
    {
      allow_screenshots: 1,
      allow_downloads: 0,
      watermark_enabled: 1,
      maintenance_mode: 0
    },
    adminHeaders
  );
  
  // Test get settings after update
  await testEndpoint('Get Settings After Update', 'GET', '/api/settings');
}

// Test error cases
async function testErrorCases() {
  log('\n🚨 Testing Error Cases', 'blue');
  
  // Test unauthorized access
  await testEndpoint('Unauthorized Access', 'GET', '/api/designs');
  
  // Test invalid token
  await testEndpoint(
    'Invalid Token',
    'GET',
    '/api/designs',
    null,
    { Authorization: 'Bearer invalid-token' }
  );
  
  // Test admin-only endpoint with regular user
  await testEndpoint(
    'Admin Endpoint with User Token',
    'GET',
    '/api/admin/users',
    null,
    { Authorization: `Bearer ${authToken}` }
  );
  
  // Test invalid endpoints
  await testEndpoint('Invalid Endpoint', 'GET', '/api/nonexistent');
  
  // Test malformed requests
  await testEndpoint(
    'Malformed Registration',
    'POST',
    '/api/register',
    { username: 'test' } // Missing password
  );
}

// Main test runner
async function runAllTests() {
  log('🚀 Starting API Tests', 'blue');
  log('=====================================', 'blue');
  
  // Test basic endpoint
  await testEndpoint('Health Check', 'GET', '/health');
  await testEndpoint('Root Endpoint', 'GET', '/');
  
  // Run test suites
  await testAuth();
  await testCategories();
  await testDesigns();
  await testFavorites();
  await testAdmin();
  await testSettings();
  await testErrorCases();
  
  log('\n✨ API Tests Completed!', 'blue');
  log('=====================================', 'blue');
}

// Command line interface
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
Usage: node test-api.js [options]

Options:
  --url <url>     Set the base URL (default: http://localhost:8787)
  --auth          Test only authentication endpoints
  --designs       Test only design endpoints
  --admin         Test only admin endpoints
  --settings      Test only settings endpoints
  --errors        Test only error cases
  --help, -h      Show this help message

Examples:
  node test-api.js
  node test-api.js --url https://your-worker.your-subdomain.workers.dev
  node test-api.js --auth --designs
    `);
    process.exit(0);
  }
  
  // Parse URL option
  const urlIndex = args.indexOf('--url');
  if (urlIndex !== -1 && args[urlIndex + 1]) {
    BASE_URL = args[urlIndex + 1];
    log(`Using base URL: ${BASE_URL}`, 'yellow');
  }
  
  // Run specific test suites
  const runAuth = args.includes('--auth');
  const runDesigns = args.includes('--designs');
  const runAdmin = args.includes('--admin');
  const runSettings = args.includes('--settings');
  const runErrors = args.includes('--errors');
  
  if (runAuth || runDesigns || runAdmin || runSettings || runErrors) {
    (async () => {
      if (runAuth) await testAuth();
      if (runDesigns) {
        if (!authToken) await testAuth();
        await testDesigns();
      }
      if (runAdmin) {
        if (!adminToken) await testAuth();
        await testAdmin();
      }
      if (runSettings) {
        if (!adminToken) await testAuth();
        await testSettings();
      }
      if (runErrors) await testErrorCases();
    })();
  } else {
    runAllTests();
  }
} 