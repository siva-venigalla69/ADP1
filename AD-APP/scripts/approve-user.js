#!/usr/bin/env node

const https = require('https');
const http = require('http');

// Configuration
const API_BASE_URL = 'http://localhost:8787';
const ADMIN_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjEsInVzZXJuYW1lIjoiYWRtaW4iLCJpc0FkbWluIjp0cnVlLCJleHAiOjE3NTE1NDgxNzQsImlhdCI6MTc1MTQ2MTc3NH0.9epnBFsRcdS-T2Lg0noHM57c5IhJKIgZMlXMqQebt08';

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

async function approveUser() {
  console.log('🔍 Getting list of users...');
  
  try {
    // Get users list
    const usersResponse = await makeRequest(`${API_BASE_URL}/api/admin/users`, {
      headers: {
        'Authorization': `Bearer ${ADMIN_TOKEN}`,
      },
    });
    
    console.log('Users list:', JSON.stringify(usersResponse, null, 2));
    
    if (usersResponse.status === 200 && Array.isArray(usersResponse.data)) {
      // Find testuser123
      const testUser = usersResponse.data.find(user => user.username === 'testuser123');
      
      if (testUser) {
        console.log(`Found testuser123 with ID: ${testUser.id}`);
        
        // Approve the user
        const approveResponse = await makeRequest(`${API_BASE_URL}/api/admin/approve-user`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${ADMIN_TOKEN}`,
          },
          body: {
            userId: testUser.id,
            approved: true,
          },
        });
        
        console.log('Approval result:', JSON.stringify(approveResponse, null, 2));
        
        if (approveResponse.status === 200) {
          console.log('✅ User approved successfully!');
        } else {
          console.log('❌ Failed to approve user');
        }
      } else {
        console.log('❌ testuser123 not found in users list');
      }
    } else {
      console.log('❌ Failed to get users list');
    }
  } catch (error) {
    console.error('Error:', error.message);
  }
}

approveUser(); 