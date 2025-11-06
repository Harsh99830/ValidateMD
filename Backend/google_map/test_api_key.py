import os
import requests
from dotenv import load_dotenv
import os.path

# Load environment variables from parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Get API key from environment
api_key = os.getenv('GOOGLE_MAPS_API_KEY')
print(f"Using API key: {api_key[:5]}...{api_key[-5:] if api_key else ''}")

# Test address
test_address = "1600 Amphitheatre Parkway, Mountain View, CA"

# Make direct request to Google Maps Geocoding API
url = f"https://maps.googleapis.com/maps/api/geocode/json?address={test_address}&key={api_key}"
print(f"\nMaking request to: {url}")

response = requests.get(url)
data = response.json()

print("\nResponse status:", response.status_code)
print("Response body:")
print(data)

# Check for errors
if data.get('status') == 'OK':
    print("\n✅ Success! The API key is working correctly.")
    print(f"Found location: {data['results'][0]['formatted_address']}")
else:
    print("\n❌ Error:")
    print(f"Status: {data.get('status')}")
    print(f"Error message: {data.get('error_message', 'No error message')}")
    print("\nCommon issues:")
    print("1. Make sure the API key is correct")
    print("2. Enable the following APIs in Google Cloud Console:")
    print("   - Geocoding API")
    print("   - Maps JavaScript API")
    print("3. Check if billing is enabled for your project")
