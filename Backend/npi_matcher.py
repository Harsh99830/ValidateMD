import requests
import pandas as pd
import re
import openai
import os
import logging
import time
import traceback
from typing import Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)


# Initialize OpenAI and check for API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable is not set. Please set it to use AI features.")
openai.api_key = OPENAI_API_KEY

def openai_call(prompt: str, model: str = "gpt-4o-mini") -> Optional[str]:
    """Make OpenAI API call for intelligent validation"""
    logger.debug(f"Making OpenAI API call: {prompt[:100]}...")
    start_time = time.time()
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a healthcare data validation expert. Be concise and accurate."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.1
    )
    duration = time.time() - start_time
    logger.debug(f"OpenAI API call completed in {duration:.2f}s")
    return response.choices[0].message.content.strip()

def normalize_status_with_ai(status_text: str) -> str:
    """Use AI to normalize provider status"""
    logger.debug(f"Normalizing status: {status_text}")
    
    prompt = f"""
    Normalize this healthcare provider status to standard format:
    Input: "{status_text}"
    
    Options: ACTIVE, INACTIVE, UNKNOWN
    Rules: 
    - 'A', 'Active', 'Practicing' → ACTIVE
    - 'I', 'Inactive', 'Retired' → INACTIVE  
    - Anything else → UNKNOWN
    
    Return only: ACTIVE or INACTIVE or UNKNOWN
    """
    
    ai_response = openai_call(prompt)
    if ai_response and ai_response in ['ACTIVE', 'INACTIVE', 'UNKNOWN']:
        logger.debug(f"AI normalized status: {status_text} -> {ai_response}")
        return ai_response
    raise RuntimeError("OpenAI API failed to return a valid response for status normalization.")

def map_procedure_to_specialty(procedure: str, current_specialty: str) -> str:
    """Use AI to check if procedure matches specialty"""
    logger.debug(f"Checking procedure-specialty match: '{procedure}' vs '{current_specialty}'")
    
    prompt = f"""
    As a medical expert, determine if this healthcare procedure is typically performed by a provider with this specialty:
    Procedure: "{procedure}"
    Provider Specialty: "{current_specialty}"
    
    Consider:
    - Surgical procedures require surgical specialties
    - Medical procedures match medical specialties  
    - Some procedures span multiple specialties
    
    Return only: MATCH or MISMATCH or UNCERTAIN
    """
    
    ai_response = openai_call(prompt)
    if ai_response and ai_response in ['MATCH', 'MISMATCH', 'UNCERTAIN']:
        logger.debug(f"AI procedure-specialty result: {ai_response}")
        return ai_response
    raise RuntimeError("OpenAI API failed to return a valid response for procedure-specialty mapping.")

def compare_address_ai(csv_addr: str, npi_addr: str) -> str:
    """Use AI for intelligent address comparison"""
    logger.debug(f"Comparing addresses: CSV='{csv_addr}' vs NPI='{npi_addr}'")
    
    prompt = f"""
    Compare these two healthcare practice addresses. Are they likely the same physical location?
    Address 1: "{csv_addr}"
    Address 2: "{npi_addr}"
    
    Consider:
    - Same street number and name = same location
    - Different suite/unit numbers = same building
    - Minor formatting differences = same address
    - Completely different streets = different locations
    
    Return only: SAME or DIFFERENT
    """
    
    ai_response = openai_call(prompt)
    if ai_response and ai_response in ['SAME', 'DIFFERENT']:
        logger.debug(f"AI address comparison result: {ai_response}")
        return ai_response
    raise RuntimeError("OpenAI API failed to return a valid response for address comparison.")

def compare_address_fallback(addr1: str, addr2: str) -> str:
    """Rule-based address comparison fallback"""
    # Remove suite numbers and normalize
    clean1 = re.sub(r'SUITE\s+\d+|STE\s+\d+|UNIT\s+\d+', '', addr1, flags=re.IGNORECASE).strip()
    clean2 = re.sub(r'SUITE\s+\d+|STE\s+\d+|UNIT\s+\d+', '', addr2, flags=re.IGNORECASE).strip()
    
    # Extract just numbers and street name
    nums1 = re.findall(r'\d+', clean1)
    nums2 = re.findall(r'\d+', clean2)
    
    if nums1 and nums2 and nums1[0] == nums2[0]:
        return "SAME"
    return "DIFFERENT"

def get_npi_provider_data(npi_number: str) -> Dict:
    """Get comprehensive provider data from NPI registry"""
    logger.info(f"Fetching NPI data for: {npi_number}")
    start_time = time.time()
    
    url = f"https://npiregistry.cms.hhs.gov/api/?version=2.1&number={npi_number}"
    
    try:
        logger.debug(f"Making NPI API request to: {url}")
        response = requests.get(url, timeout=10)
        data = response.json()
        
        duration = time.time() - start_time
        logger.info(f"NPI API call for {npi_number} completed in {duration:.2f}s")
        
        if data["result_count"] > 0:
            provider = data["results"][0]
            npi_info = extract_all_provider_info(provider)
            
            logger.debug(f"NPI data found for {npi_number}: {npi_info['full_name']}")
            return {
                **npi_info,
                'status': 'SUCCESS'
            }
        else:
            logger.warning(f"NPI number not found: {npi_number}")
            return {
                'first_name': "NOT_FOUND",
                'last_name': "",
                'full_name': "NOT_FOUND",
                'status': 'NOT_FOUND'
            }
            
    except requests.exceptions.Timeout:
        logger.error(f"NPI API timeout for {npi_number}")
        return {
            'first_name': "ERROR",
            'last_name': "",
            'full_name': "ERROR: Request timeout",
            'status': 'ERROR'
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"NPI API network error for {npi_number}: {e}")
        return {
            'first_name': "ERROR",
            'last_name': "",
            'full_name': f"ERROR: Network error - {str(e)}",
            'status': 'ERROR'
        }
    except Exception as e:
        logger.error(f"NPI API unexpected error for {npi_number}: {e}")
        return {
            'first_name': "ERROR",
            'last_name': "",
            'full_name': f"ERROR: {str(e)}",
            'status': 'ERROR'
        }

def extract_all_provider_info(provider: Dict) -> Dict:
    """Extract all available provider information from NPI data"""
    
    basic = provider.get('basic', {})
    addresses = provider.get('addresses', [])
    taxonomies = provider.get('taxonomies', [])
    
    # Find primary practice address
    practice_address = None
    for addr in addresses:
        if addr.get('address_purpose') == 'LOCATION':
            practice_address = addr
            break
    if not practice_address and addresses:
        practice_address = addresses[0]
    
    # Find primary specialty
    primary_specialty = None
    for tax in taxonomies:
        if tax.get('primary', False):
            primary_specialty = tax
            break
    if not primary_specialty and taxonomies:
        primary_specialty = taxonomies[0]
    
    result = {
        'first_name': basic.get('first_name', 'N/A'),
        'last_name': basic.get('last_name', 'N/A'),
        'full_name': f"{basic.get('first_name', '')} {basic.get('last_name', '')}",
        'Credential': basic.get('credential', 'N/A'),
        'Status': 'ACTIVE' if basic.get('status') == 'A' else 'INACTIVE',
        'Address': practice_address.get('address_1', 'N/A') if practice_address else 'N/A',
        'City': practice_address.get('city', 'N/A') if practice_address else 'N/A',
        'State': practice_address.get('state', 'N/A') if practice_address else 'N/A',
        'Zip': practice_address.get('postal_code', 'N/A') if practice_address else 'N/A',
        'Phone': practice_address.get('telephone_number', 'N/A') if practice_address else 'N/A',
        'Speciality': primary_specialty.get('desc', 'N/A') if primary_specialty else 'N/A',
        'License_number': primary_specialty.get('license', 'N/A') if primary_specialty else 'N/A',
        'Education': 'N/A - Not available in NPI registry',
        'enumeration_date': basic.get('enumeration_date', 'N/A'),
        'last_updated': basic.get('last_updated', 'N/A'),
        'gender': basic.get('sex', 'N/A'),
    }
    
    logger.debug(f"Extracted provider info: {result['full_name']}, Specialty: {result['Speciality']}")
    return result

def enhanced_validate_provider(csv_provider: Dict, npi_data: Dict) -> tuple:
    """Enhanced validation with AI intelligence"""
    provider_name = f"{csv_provider.get('first_name')} {csv_provider.get('last_name')}"
    logger.debug(f"Enhanced validation for: {provider_name}")
    
    mismatches = []
    ai_insights = []
    
    # 1. Status normalization with AI
    logger.debug("Validating status...")
    csv_status_normalized = normalize_status_with_ai(csv_provider['Status'])
    npi_status_normalized = normalize_status_with_ai(npi_data['Status'])
    
    if csv_status_normalized != npi_status_normalized:
        mismatches.append(f"STATUS: CSV '{csv_provider['Status']}' → NPI '{npi_data['Status']}'")
        ai_insights.append(f"AI normalized status: CSV '{csv_status_normalized}' vs NPI '{npi_status_normalized}'")
        logger.debug(f"Status mismatch: CSV={csv_status_normalized}, NPI={npi_status_normalized}")
    
    # 2. Specialty/procedure matching with AI
    logger.debug("Validating specialty...")
    specialty_match = map_procedure_to_specialty(csv_provider['Speciality'], npi_data['Speciality'])
    if specialty_match == "MISMATCH":
        mismatches.append(f"SPECIALTY: CSV '{csv_provider['Speciality']}' vs NPI '{npi_data['Speciality']}'")
        ai_insights.append("AI detected specialty/procedure mismatch")
        logger.debug("Specialty mismatch detected")
    elif specialty_match == "MATCH":
        ai_insights.append("AI confirmed specialty/procedure compatibility")
        logger.debug("Specialty match confirmed")
    
    # 3. Address comparison with AI
    logger.debug("Validating address...")
    address_match = compare_address_ai(csv_provider['Address'], npi_data['Address'])
    if address_match == "DIFFERENT":
        mismatches.append(f"ADDRESS: CSV '{csv_provider['Address']}' vs NPI '{npi_data['Address']}'")
        logger.debug("Address mismatch detected")
    else:
        ai_insights.append("AI confirmed addresses represent same location")
        logger.debug("Address match confirmed")
    
    # 4. License number matching (exact match required)
    logger.debug("Validating license...")
    if (csv_provider.get('License_number') and npi_data['License_number'] != 'N/A' and
        str(csv_provider['License_number']).upper() != str(npi_data['License_number']).upper()):
        mismatches.append(f"LICENSE: CSV '{csv_provider['License_number']}' vs NPI '{npi_data['License_number']}'")
        logger.debug("License number mismatch detected")
    
    logger.debug(f"Validation complete: {len(mismatches)} mismatches, {len(ai_insights)} AI insights")
    return mismatches, ai_insights

def validate_providers_from_csv(csv_file_path: str, use_ai: bool = True, limit: int = None) -> List[Dict]:
    """Validate providers from CSV file"""
    logger.info(f"Starting CSV validation: {csv_file_path}, AI: {use_ai}, Limit: {limit}")
    start_time = time.time()
    
    try:
        # Read CSV file
        logger.info(f"Reading CSV file: {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        logger.info(f"CSV loaded successfully. Total rows: {len(df)}")
        logger.debug(f"CSV columns: {df.columns.tolist()}")
        
        if limit:
            df = df.head(limit)
            logger.info(f"Limited to {limit} providers")
        
        results = []
        
        for index, provider in df.iterrows():
            provider_num = index + 1
            npi_number = provider['npi_number']
            logger.info(f"Processing provider {provider_num}/{len(df)}: NPI {npi_number}")
            
            # Add small delay to avoid rate limiting
            if provider_num > 1:
                time.sleep(0.5)  # 500ms delay between NPI API calls
            
            npi_data = get_npi_provider_data(npi_number)
            csv_dict = provider.to_dict()
            
            if npi_data['status'] == 'SUCCESS':
                if use_ai:
                    logger.debug(f"Using AI validation for provider {provider_num}")
                    mismatches, ai_insights = enhanced_validate_provider(csv_dict, npi_data)
                else:
                    logger.debug(f"Using basic validation for provider {provider_num}")
                    mismatches = check_data_match_basic(csv_dict, npi_data)
                    ai_insights = []
                
                match_status = "PERFECT_MATCH" if len(mismatches) == 0 else f"{len(mismatches)}_MISMATCHES"
                logger.info(f"Provider {provider_num} - Status: {match_status}, Mismatches: {len(mismatches)}")
            else:
                mismatches = []
                ai_insights = []
                match_status = npi_data['status']
                logger.warning(f"Provider {provider_num} - NPI lookup failed: {match_status}")
            
            results.append({
                'provider_id': provider_num,
                'csv_data': csv_dict,
                'npi_data': npi_data,
                'mismatches': mismatches,
                'ai_insights': ai_insights,
                'match_status': match_status,
                'ai_enabled': use_ai
            })
        
        total_duration = time.time() - start_time
        logger.info(f"Validation completed in {total_duration:.2f}s. Processed {len(results)} providers")
        
        return results
        
    except pd.errors.EmptyDataError:
        logger.error("CSV file is empty")
        raise Exception("CSV file is empty")
    except pd.errors.ParserError:
        logger.error("CSV file parsing error")
        raise Exception("Invalid CSV file format")
    except KeyError as e:
        logger.error(f"Missing required column in CSV: {e}")
        raise Exception(f"Missing required column: {e}")
    except Exception as e:
        logger.error(f"CSV validation failed: {e}")
        logger.error(traceback.format_exc())
        raise

def check_data_match_basic(csv_provider: Dict, npi_data: Dict) -> List[str]:
    """Basic rule-based data matching (fallback)"""
    mismatches = []
    
    # Basic field comparisons
    fields_to_check = ['first_name', 'last_name', 'Credential', 'City', 'State', 'Zip', 'Phone']
    for field in fields_to_check:
        csv_val = str(csv_provider.get(field, '')).upper()
        npi_val = str(npi_data.get(field, '')).upper()
        if csv_val != npi_val and csv_val and npi_val and npi_val != 'N/A':
            mismatches.append(f"{field.upper()}: CSV '{csv_provider.get(field)}' vs NPI '{npi_data.get(field)}'")
    
    logger.debug(f"Basic validation found {len(mismatches)} mismatches")
    return mismatches

def get_validation_summary(results: List[Dict]) -> Dict:
    """Generate summary statistics from validation results"""
    logger.debug("Generating validation summary")
    
    total_providers = len(results)
    successful_lookups = len([r for r in results if r['npi_data']['status'] == 'SUCCESS'])
    perfect_matches = len([r for r in results if r['match_status'] == 'PERFECT_MATCH'])
    ai_insights_count = sum(len(r['ai_insights']) for r in results)
    
    # Count mismatches by type
    mismatch_types = {}
    for result in results:
        for mismatch in result['mismatches']:
            mismatch_type = mismatch.split(':')[0]
            mismatch_types[mismatch_type] = mismatch_types.get(mismatch_type, 0) + 1
    
    summary = {
        'total_providers': total_providers,
        'successful_lookups': successful_lookups,
        'perfect_matches': perfect_matches,
        'ai_insights_count': ai_insights_count,
        'mismatch_types': mismatch_types,
        'success_rate': (successful_lookups / total_providers * 100) if total_providers > 0 else 0,
        'match_rate': (perfect_matches / successful_lookups * 100) if successful_lookups > 0 else 0
    }
    
    logger.info(f"Summary generated: {summary}")
    return summary