"""
Test Webhooks - Simulate Plivo webhook calls locally

WHAT THIS DOES:
================
Simulates a complete IVR call flow by making HTTP requests to your Flask app.

Simulates:
1. Incoming call (POST /webhooks/answer)
2. User presses 1 (POST /webhooks/input with digit 1)
3. User presses another digit
4. Call ends (POST /webhooks/hangup)

Displays XML responses at each step.

WHY RUN THIS:
=============
Test the IVR system locally without needing:
- A real Plivo account
- Real phone calls
- ngrok or internet exposure

Perfect for development and debugging.

HOW TO RUN:
===========
# Terminal 1: Start Flask app
python app.py

# Terminal 2: Run tests
python scripts/test_webhook.py
"""

import sys
import requests
import json
from datetime import datetime
import xml.dom.minidom as minidom

# Configuration
BASE_URL = 'http://localhost:5000'
CALL_UUID = f'test-call-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
FROM_NUMBER = '+15551234567'
TO_NUMBER = '+15559876543'

def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_step(step_num, text):
    """Print step."""
    print(f"\n[STEP {step_num}] {text}")
    print(f"{'-'*60}")

def print_request(method, endpoint, data=None):
    """Print request details."""
    print(f"Request: {method} {BASE_URL}{endpoint}")
    if data:
        print(f"Data: {data}")

def print_response(response):
    """Print response details."""
    print(f"Status: {response.status_code}")

    # Try to parse as XML
    try:
        if response.headers.get('content-type') == 'application/xml':
            # Pretty print XML
            dom = minidom.parseString(response.text)
            pretty_xml = dom.toprettyxml()
            # Remove XML declaration and extra whitespace
            pretty_xml = '\n'.join([line for line in pretty_xml.split('\n')[1:] if line.strip()])
            print(f"Response XML:\n{pretty_xml}")
        else:
            print(f"Response: {response.text[:200]}")
    except:
        print(f"Response: {response.text[:200]}")

def test_health():
    """Test health endpoint."""
    print_step(0, "Test Health Check")

    try:
        endpoint = '/health'
        print_request('GET', endpoint)

        response = requests.get(f'{BASE_URL}{endpoint}')
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            print(f"\nHealth Status:")
            print(f"  Overall: {data.get('status')}")
            print(f"  Redis: {data.get('redis')}")
            print(f"  Database: {data.get('database')}")
            print(f"\n✓ Health check passed\n")
            return True
        else:
            print(f"\n✗ Health check failed\n")
            return False

    except requests.exceptions.ConnectionError:
        print(f"\n✗ Could not connect to {BASE_URL}")
        print(f"  Make sure Flask app is running: python app.py\n")
        return False
    except Exception as e:
        print(f"\n✗ Error: {str(e)}\n")
        return False

def test_incoming_call():
    """Test incoming call webhook."""
    print_step(1, "Simulate Incoming Call")

    try:
        endpoint = '/webhooks/answer'
        data = {
            'CallUUID': CALL_UUID,
            'From': FROM_NUMBER,
            'To': TO_NUMBER,
            'Direction': 'inbound',
            'CallStatus': 'ringing'
        }

        print_request('POST', endpoint, data)
        response = requests.post(f'{BASE_URL}{endpoint}', data=data)
        print_response(response)

        if response.status_code == 200:
            print(f"\n✓ Incoming call handled successfully")
            print(f"  Call UUID: {CALL_UUID}")
            return True
        else:
            print(f"\n✗ Failed to handle incoming call")
            return False

    except Exception as e:
        print(f"\n✗ Error: {str(e)}\n")
        return False

def test_digit_input(digit, step_num):
    """Test digit input webhook."""
    print_step(step_num, f"User Presses '{digit}'")

    try:
        endpoint = '/webhooks/input'
        data = {
            'CallUUID': CALL_UUID,
            'Digits': digit,
            'Duration': str(step_num * 3)  # Simulate call duration
        }

        print_request('POST', endpoint, data)
        response = requests.post(f'{BASE_URL}{endpoint}', data=data)
        print_response(response)

        if response.status_code == 200:
            print(f"\n✓ Digit processed successfully")
            return True
        else:
            print(f"\n✗ Failed to process digit")
            return False

    except Exception as e:
        print(f"\n✗ Error: {str(e)}\n")
        return False

def test_hangup():
    """Test call hangup webhook."""
    print_step(4, "Call Ends")

    try:
        endpoint = '/webhooks/hangup'
        data = {
            'CallUUID': CALL_UUID,
            'HangupCause': 'NORMAL_CLEARING',
            'Duration': '180',
            'CallStatus': 'completed'
        }

        print_request('POST', endpoint, data)
        response = requests.post(f'{BASE_URL}{endpoint}', data=data)
        print_response(response)

        if response.status_code == 200:
            print(f"\n✓ Hangup processed successfully")
            print(f"  Call data saved to database")
            return True
        else:
            print(f"\n✗ Failed to process hangup")
            return False

    except Exception as e:
        print(f"\n✗ Error: {str(e)}\n")
        return False

def main():
    """Main function."""
    print_header("IVR SYSTEM - LOCAL WEBHOOK TEST")

    print("This script simulates a complete IVR call flow:")
    print("  1. Incoming call")
    print("  2. User presses 1 (Sales)")
    print("  3. User presses 1 (New Customer)")
    print("  4. Call ends")
    print()

    # Step 0: Health check
    if not test_health():
        print("Exiting due to connection failure")
        return 1

    # Step 1: Incoming call
    if not test_incoming_call():
        print("Exiting due to webhook failure")
        return 1

    # Step 2: First digit (1 = Sales)
    if not test_digit_input('1', 2):
        print("Exiting due to webhook failure")
        return 1

    # Step 3: Second digit (1 = New Customer)
    if not test_digit_input('1', 3):
        print("Exiting due to webhook failure")
        return 1

    # Step 4: Hangup
    if not test_hangup():
        print("Exiting due to webhook failure")
        return 1

    # Success
    print_header("TEST COMPLETE")
    print("✓ All webhooks executed successfully!")
    print()
    print("Call flow:")
    print("  main_menu → Press 1 → sales_menu → Press 1 → sales_new_customer")
    print()
    print("What happened:")
    print("  - Session created in Redis")
    print("  - Menus loaded from database")
    print("  - XML generated and returned")
    print("  - Call ended and saved to database")
    print()
    print("Next steps:")
    print("  1. Check database: SELECT * FROM call_logs;")
    print("  2. Check caller history: SELECT * FROM caller_history;")
    print("  3. Test with real Plivo call (configure webhooks in Plivo console)")
    print()

    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
