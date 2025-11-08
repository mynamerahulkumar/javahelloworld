#!/usr/bin/env python3
"""
Test script for login validation
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from auth.client_auth import client_auth

def test_login():
    print("=" * 50)
    print("Testing Login Validation")
    print("=" * 50)
    
    print(f"\nCSV Path: {client_auth.csv_path}")
    print(f"CSV Exists: {client_auth.csv_path.exists()}")
    
    # Reload clients
    client_auth.reload_clients()
    
    print(f"\nClients loaded: {len(client_auth.clients)}")
    for email, data in client_auth.clients.items():
        print(f"  {email}: client_id={data['client_id']}, password={'***' if data['password'] else 'N/A'}")
    
    # Test cases
    print("\n" + "=" * 50)
    print("Test Cases")
    print("=" * 50)
    
    # Test 1: Valid credentials
    print("\nTest 1: Valid email and client_id")
    result, msg = client_auth.validate_client('234576', 'dharacoding@gmail.com')
    print(f"  Result: {result}, Message: {msg}")
    
    # Test 2: Valid credentials with password
    print("\nTest 2: Valid email, client_id, and password")
    result, msg = client_auth.validate_client('234576', 'dharacoding@gmail.com', '234575')
    print(f"  Result: {result}, Message: {msg}")
    
    # Test 3: Invalid email
    print("\nTest 3: Invalid email")
    result, msg = client_auth.validate_client('234576', 'invalid@email.com')
    print(f"  Result: {result}, Message: {msg}")
    
    # Test 4: Invalid client_id
    print("\nTest 4: Invalid client_id")
    result, msg = client_auth.validate_client('999999', 'dharacoding@gmail.com')
    print(f"  Result: {result}, Message: {msg}")
    
    # Test 5: Wrong password (if password exists in CSV)
    print("\nTest 5: Wrong password")
    result, msg = client_auth.validate_client('234576', 'dharacoding@gmail.com', 'wrongpassword')
    print(f"  Result: {result}, Message: {msg}")
    
    # Test 6: Second valid user
    print("\nTest 6: Second valid user")
    result, msg = client_auth.validate_client('234578', 'srpaitech@gmail.com', '234576')
    print(f"  Result: {result}, Message: {msg}")

if __name__ == "__main__":
    test_login()





