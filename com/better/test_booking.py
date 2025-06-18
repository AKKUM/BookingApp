import requests
import json

def test_booking_api():
    """Test the booking API locally"""

    # Test data
    booking_data = {
        "username": "BET1868995",
        "password": "W3ek3ndw@rri0rs4",
        "initial_url": "https://bookings.better.org.uk/location/canons-leisure-centre",
        "logged_in_url": "https://bookings.better.org.uk/location/canons-leisure-centre/badminton-40min/2025-06-22/by-time/slot/09:40-10:20",
        "court_number": "Court 3"
    }

    try:
        # Test local API
        response = requests.post(
            "http://localhost:5001/book",
            headers={"Content-Type": "application/json"},
            json=booking_data,
            timeout=60
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get("http://localhost:5001/health")
        print(f"Health Check: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Health check failed: {e}")

if __name__ == "__main__":
    print("Testing Health Check...")
    test_health_check()

    print("\nTesting Booking API...")
    print("Make sure to update the email/password in the script!")
    # Uncomment the line below when ready to test
    test_booking_api()