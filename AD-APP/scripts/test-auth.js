#!/usr/bin/env node

/**
 * Authentication Testing Script
 * Run this script to validate your backend API endpoints
 * 
 * Usage: node scripts/test-auth.js
 */

const https = require('https');
const http = require('http');

// Configuration - Update these values
const CONFIG = {
  API_BASE_URL: 'http://localhost:8787', // Local development
  // API_BASE_URL: 'https://your-actual-worker-url', // Replace with URL from dashboard
  TEST_USERNAME: 'testuser456',  // New user for auto-approval test
  TEST_PASSWORD: 'testpass456',
};

// Helper function to make HTTP requests
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const isHttps = url.startsWith('https');
    const client = isHttps ? https : http;
    
    const req = client.request(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve({ status: res.statusCode, data: jsonData });
        } catch {
          resolve({ status: res.statusCode, data: data });
        }
      });
    });

    req.on('error', reject);
    
    if (options.body) {
      req.write(JSON.stringify(options.body));
    }
    
    req.end();
  });
}

// Test functions
async function testHealthCheck() {
  console.log('🔍 Testing health check...');
  try {
    const response = await makeRequest(`${CONFIG.API_BASE_URL}/health`);
    if (response.status === 200) {
      console.log('✅ Health check passed');
      return true;
    } else {
      console.log('❌ Health check failed:', response.status);
      return false;
    }
  } catch (error) {
    console.log('❌ Health check error:', error.message);
    return false;
  }
}

async function testRegistration() {
  console.log('🔍 Testing user registration...');
  try {
    const response = await makeRequest(`${CONFIG.API_BASE_URL}/api/register`, {
      method: 'POST',
      body: {
        username: CONFIG.TEST_USERNAME,
        password: CONFIG.TEST_PASSWORD,
      },
    });
    
    if (response.status === 201) {
      console.log('✅ Registration successful');
      return true;
    } else if (response.status === 409) {
      console.log('ℹ️ User already exists (this is fine for testing)');
      return true;
    } else {
      console.log('❌ Registration failed:', response.status, response.data);
      return false;
    }
  } catch (error) {
    console.log('❌ Registration error:', error.message);
    return false;
  }
}

async function testLogin() {
  console.log('🔍 Testing user login...');
  try {
    const response = await makeRequest(`${CONFIG.API_BASE_URL}/api/login`, {
      method: 'POST',
      body: {
        username: CONFIG.TEST_USERNAME,
        password: CONFIG.TEST_PASSWORD,
      },
    });
    
    if (response.status === 200 && response.data.token) {
      console.log('✅ Login successful');
      return response.data.token;
    } else {
      console.log('❌ Login failed:', response.status, response.data);
      return null;
    }
  } catch (error) {
    console.log('❌ Login error:', error.message);
    return null;
  }
}

async function testProtectedEndpoint(token) {
  console.log('🔍 Testing protected endpoint...');
  try {
    const response = await makeRequest(`${CONFIG.API_BASE_URL}/api/designs`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    if (response.status === 200) {
      console.log('✅ Protected endpoint accessible');
      return true;
    } else {
      console.log('❌ Protected endpoint failed:', response.status, response.data);
      return false;
    }
  } catch (error) {
    console.log('❌ Protected endpoint error:', error.message);
    return false;
  }
}

// Main test runner
async function runTests() {
  console.log('🚀 Starting Authentication API Tests\n');
  console.log(`Testing API: ${CONFIG.API_BASE_URL}\n`);
  
  let passedTests = 0;
  let totalTests = 0;
  
  // Test 1: Health Check
  totalTests++;
  if (await testHealthCheck()) passedTests++;
  console.log('');
  
  // Test 2: Registration
  totalTests++;
  if (await testRegistration()) passedTests++;
  console.log('');
  
  // Test 3: Login
  totalTests++;
  const token = await testLogin();
  if (token) passedTests++;
  console.log('');
  
  // Test 4: Protected Endpoint (only if login succeeded)
  if (token) {
    totalTests++;
    if (await testProtectedEndpoint(token)) passedTests++;
    console.log('');
  }
  
  // Results
  console.log('📊 Test Results:');
  console.log(`✅ Passed: ${passedTests}/${totalTests}`);
  console.log(`❌ Failed: ${totalTests - passedTests}/${totalTests}`);
  
  if (passedTests === totalTests) {
    console.log('\n🎉 All tests passed! Your API is ready for the mobile app.');
  } else {
    console.log('\n⚠️ Some tests failed. Please check your API configuration.');
    console.log('\nTroubleshooting:');
    console.log('1. Verify your API_BASE_URL is correct');
    console.log('2. Check that your Cloudflare Worker is deployed');
    console.log('3. Ensure CORS is properly configured');
    console.log('4. Check the worker logs for errors');
  }
}

// Update configuration check
if (CONFIG.API_BASE_URL.includes('your-worker-name')) {
  console.log('⚠️  Please update the API_BASE_URL in this script with your actual Cloudflare Worker URL');
  console.log('Edit scripts/test-auth.js and replace the API_BASE_URL value.\n');
}

// Run tests
runTests().catch(console.error); 