import os
import logging
import googlemaps
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AddressVerifier:
    def __init__(self, api_key: str = None):
        """Initialize the AddressVerifier with Google Maps API key.
        
        Args:
            api_key: Google Maps API key. If not provided, will try to get from GOOGLE_MAPS_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Google Maps API key not provided. "
                "Please set the GOOGLE_MAPS_API_KEY environment variable or pass it as an argument."
            )
        self.gmaps = googlemaps.Client(key=self.api_key)
    
    def verify_address(self, address: str) -> Dict:
        """Verify if an address exists using Google Places API.
        
        Args:
            address: The address string to verify
            
        Returns:
            Dict containing verification results with keys:
            - 'is_valid': bool indicating if address is valid
            - 'formatted_address': str of the formatted address from Google
            - 'location': dict with 'lat' and 'lng' if valid
            - 'partial_match': bool indicating if this is a partial match
            - 'place_id': Google's unique identifier for the place
        """
        try:
            # First, find the place ID using the text search
            places_result = self.gmaps.places(address)
            
            if not places_result.get('results'):
                return {
                    'is_valid': False,
                    'formatted_address': None,
                    'location': None,
                    'partial_match': False,
                    'place_id': None,
                    'error': 'No results found for this address'
                }
            
            # Get the first result (most relevant)
            place = places_result['results'][0]
            place_id = place.get('place_id')
            
            # Get more details about the place
            place_details = self.gmaps.place(place_id, fields=['formatted_address', 'geometry', 'name'])
            
            return {
                'is_valid': True,
                'formatted_address': place_details['result'].get('formatted_address'),
                'location': place_details['result'].get('geometry', {}).get('location'),
                'partial_match': any([
                    'partial_match' in place,
                    'partial' in place.get('types', [])
                ]),
                'place_id': place_id,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error verifying address '{address}': {str(e)}")
            return {
                'is_valid': False,
                'formatted_address': None,
                'location': None,
                'partial_match': False,
                'match_type': [],
                'error': str(e)
            }
    
    def verify_addresses_from_csv(
        self,
        input_file: str,
        address_columns: List[str],
        output_file: str = None,
        id_column: str = None
    ) -> pd.DataFrame:
        """Verify addresses from a CSV file.
        
        Args:
            input_file: Path to input CSV file
            address_columns: List of column names that form the full address (in order of priority)
            output_file: Optional path to save results (CSV)
            id_column: Optional column name to use as identifier in results
            
        Returns:
            DataFrame with verification results
        """
        try:
            # Read the input file
            df = pd.read_csv(input_file)
            
            # Combine address components into a single string
            df['full_address'] = df[address_columns].apply(
                lambda x: ', '.join(x.dropna().astype(str)), axis=1
            )
            
            # Verify each address
            results = []
            for idx, row in df.iterrows():
                result = {
                    'original_address': row['full_address'],
                    **self.verify_address(row['full_address'])
                }
                
                # Add ID if specified
                if id_column and id_column in row:
                    result['id'] = row[id_column]
                
                results.append(result)
                
                # Log progress
                if (idx + 1) % 10 == 0:
                    logger.info(f"Processed {idx + 1}/{len(df)} addresses")
            
            # Convert results to DataFrame
            result_df = pd.DataFrame(results)
            
            # Save results if output file is specified
            if output_file:
                result_df.to_csv(output_file, index=False)
                logger.info(f"Results saved to {output_file}")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            raise

def main():
    # Load environment variables from .env file in the parent directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(env_path)
    
    print(f"Looking for .env at: {env_path}")
    print(f"GOOGLE_MAPS_API_KEY is set: {'Yes' if os.getenv('GOOGLE_MAPS_API_KEY') else 'No'}")
    
    try:
        # Initialize verifier
        verifier = AddressVerifier()
        
        # Path to the CSV file in the same directory
        csv_file = 'updated_NPI_provider_details.csv'
        
        # Read the first 5 rows from CSV
        print(f"\nReading first 5 addresses from {csv_file}...")
        df = pd.read_csv(csv_file, nrows=5)
        
        # Process each address
        for idx, row in df.iterrows():
            # Combine address components
            full_address = f"{row['Address']}, {row['City']}, {row['State']} {row['Zip']}"
            print(f"\n--- Verifying address {idx + 1} ---")
            print(f"Provider: {row['first_name']} {row['last_name']}")
            print(f"Original address: {full_address}")
            
            # Verify the address
            result = verifier.verify_address(full_address)
            
            # Print results
            if result['is_valid']:
                print(f"✅ Valid address")
                print(f"   Formatted: {result['formatted_address']}")
                print(f"   Location: {result['location']}")
                if result['partial_match']:
                    print("   ⚠️  Note: This is a partial match")
            else:
                print(f"❌ Invalid address")
                if 'error' in result and result['error']:
                    print(f"   Error: {result['error']}")
            
            # Add a small delay to avoid hitting API rate limits
            import time
            time.sleep(1)
        
        print("\nAddress verification complete!")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        if os.getenv('DEBUG'):
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
