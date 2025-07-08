#!/usr/bin/env python3
"""
Quick API Test Script for Design Gallery Backend
Tests basic functionality to ensure the API is working correctly
"""

import requests
import json
import sys
from typing import Dict, Any, Optional, Tuple


def test_endpoint(url: str, method: str = "GET", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Tuple[bool, Any]:
    """Test a single endpoint and return success status."""
    try:
        response = requests.request(
            method=method,
            url=url,
            json=data,
            headers=headers or {},
            timeout=10
        )
        
        print(f"  {method} {url} -> {response.status_code}")
        
        if response.status_code < 400:
            return True, response
        else:
            print(f"    ❌ Error: {response.text[:100]}")
            return False, response
            
    except Exception as e:
        print(f"    ❌ Exception: {e}")
        return False, None


def main():
    """Run quick API tests."""
    
    API_BASE_URL = "http://localhost:8000"
    
    print("🚀 Quick API Test for Design Gallery Backend")
    print(f"Testing: {API_BASE_URL}")
    print("=" * 50)
    
    total_tests = 0
    passed_tests = 0
    
    # Test 1: Health Check
    print("\n1️⃣ Health Check...")
    total_tests += 1
    success, response = test_endpoint(f"{API_BASE_URL}/health")
    if success:
        passed_tests += 1
        data = response.json()
        print(f"    ✅ Status: {data.get('status')}")
        print(f"    ✅ Version: {data.get('version')}")
    
    # Test 2: App Info
    print("\n2️⃣ App Info...")
    total_tests += 1
    success, response = test_endpoint(f"{API_BASE_URL}/info")
    if success:
        passed_tests += 1
        data = response.json()
        print(f"    ✅ App: {data.get('app_name')}")
        print(f"    ✅ Environment: {data.get('environment')}")
        print(f"    ✅ Debug: {data.get('debug')}")
    
    # Test 3: API Documentation
    print("\n3️⃣ API Documentation...")
    total_tests += 1
    success, response = test_endpoint(f"{API_BASE_URL}/docs")
    if success:
        passed_tests += 1
        print(f"    ✅ Documentation available at {API_BASE_URL}/docs")
    
    # Test 4: User Registration
    print("\n4️⃣ User Registration...")
    total_tests += 1
    success, response = test_endpoint(
        f"{API_BASE_URL}/api/auth/register",
        method="POST",
        data={"username": "quicktest", "password": "test123"}
    )
    if success:
        passed_tests += 1
        data = response.json()
        print(f"    ✅ Message: {data.get('message')}")
    
    # Test 5: Invalid Login (should fail gracefully)
    print("\n5️⃣ Invalid Login (should fail gracefully)...")
    total_tests += 1
    success, response = test_endpoint(
        f"{API_BASE_URL}/api/auth/login",
        method="POST",
        data={"username": "nonexistent", "password": "wrong"}
    )
    if response and response.status_code == 401:
        passed_tests += 1
        print(f"    ✅ Properly rejected invalid credentials")
    elif response:
        print(f"    ❌ Expected 401, got {response.status_code}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 QUICK TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All basic tests passed!")
        print("✅ Your API is ready for development")
        print(f"🌐 API Documentation: {API_BASE_URL}/docs")
        print("🧪 Run comprehensive tests: python test_all_endpoints.py")
    else:
        print("\n⚠️ Some tests failed")
        print("Please check:")
        print("1. Server is running: uvicorn app.main:app --reload")
        print("2. Environment variables are set correctly")
        print("3. Database is accessible")
        print("4. Dependencies are installed")
        
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 