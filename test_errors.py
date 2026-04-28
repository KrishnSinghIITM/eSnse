#!/usr/bin/env python3
"""Test error handling in the /query endpoint."""

__test__ = False

import json
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_query(user_id, question, description):
    """Test a query and print results."""
    print(f"\n{'='*60}")
    print(f"Test: {description}")
    print(f"{'='*60}")
    print(f"User ID: {user_id}, Question: {question}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"user_id": user_id, "question": question},
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    """Run all tests."""
    print("Testing eSnse /query endpoint error handling")
    
    # Test 1: Valid query
    test_query(1, "How much did I spend on food?", "Valid query - should succeed")
    
    # Test 2: Cached query - should be instant
    print("\nTesting cached response...")
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/query",
        json={"user_id": 1, "question": "How much did I spend on food?"},
        timeout=30
    )
    elapsed = time.time() - start
    print(f"Cached query response time: {elapsed:.4f}s")
    print(f"Contains 'Cached': {'Cached' in response.json()['result']}")
    
    # Test 3: Query with non-existent category
    test_query(1, "How much did I spend on gambling?", "Non-existent category - testing no results handling")
    
    # Test 4: Query for user with no data
    test_query(999, "How much did I spend?", "Non-existent user - testing no results handling")
    
    # Test 5: Different user
    test_query(2, "How much did I spend on travel?", "Different user - new query")
    
    # Test 6: Cache stats
    print(f"\n{'='*60}")
    print("Cache Statistics")
    print(f"{'='*60}")
    response = requests.get(f"{BASE_URL}/cache/stats")
    print(json.dumps(response.json(), indent=2))
    
    # Test 7: Health check
    print(f"\n{'='*60}")
    print("Health Check")
    print(f"{'='*60}")
    response = requests.get(f"{BASE_URL}/health")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    main()
