import re
import openai
import json
import os

# Set your API key (recommended via environment variable)
openai.api_key = os.getenv("OPENAI_API_KEY", "api_here")

def extract_provider_info(text):
    name = re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+', text)
    license_no = re.search(r'License\s*Number[:\-]?\s*([A-Z0-9\-]+)', text)
    phone = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    specialty = re.search(r'Speciality[:\-]?\s*(.+)', text)
    address = re.search(r'Address[:\-]?\s*(.+)', text)

    return {
        "Name": name.group(0) if name else None,
        "License_No": license_no.group(1).strip() if license_no else None,
        "Phone": phone.group(0) if phone else None,
        "Specialty": specialty.group(1).strip() if specialty else None,
        "Address": address.group(1).strip() if address else None
    }

from openai import OpenAI
import base64
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "api_here"))

def extract_with_vision_api(pdf_path):
    """Extract text from PDF using OpenAI's Vision API"""
    try:
        # Convert PDF to images (first page only for demo)
        import fitz
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=300)
        
        # Save as temp image
        temp_img_path = "temp_scan.png"
        pix.save(temp_img_path)
        
        # Encode image to base64
        with open(temp_img_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Clean up temp file
        os.remove(temp_img_path)
        
        # Prepare the prompt
        prompt = """
        Extract the following fields from this document. The document may be a form or handwritten note.
        
        Return the results as a JSON object with these fields (keep the field names exactly as shown):
        {
          "Name": "Full name of the provider",
          "NPI_Number": "National Provider Identifier number",
          "Credentials": "Professional credentials (e.g., MD, RN, DO, etc.)",
          "Status": "Professional status or license status",
          "Address": "Full practice or business address",
          "Phone": "Contact phone number in (XXX) XXX-XXXX format",
          "Specialty": "Medical specialty or practice area",
          "License_Number": "Professional license number",
          "Email": "Email address if available"
        }
        
        Instructions:
        1. If a field cannot be determined, use null for that field
        2. For phone numbers, standardize the format to (XXX) XXX-XXXX
        3. For addresses, include street, city, state, and ZIP code if available
        4. For names, use title case (e.g., "John Smith" not "JOHN SMITH")
        5. If the document is a form, match the fields to the labeled sections
        """
        
        # Call the Vision API with the latest model
        response = client.chat.completions.create(
            model="gpt-4o",  # Updated to use the latest GPT-4 model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1000,
            temperature=0.2
        )
        
        # Extract and parse the response
        raw_output = response.choices[0].message.content
        
        # Clean up the response to ensure it's valid JSON
        json_start = raw_output.find('{')
        json_end = raw_output.rfind('}') + 1
        json_str = raw_output[json_start:json_end].strip()
        
        # Parse the JSON and ensure all fields are present
        result = json.loads(json_str)
        
        # Ensure all expected fields exist in the result
        expected_fields = ["Name", "NPI_Number", "Credentials", "Status", "Address", 
                         "Phone", "Specialty", "License_Number", "Email"]
        
        return {field: result.get(field, None) for field in expected_fields}
        
    except Exception as e:
        print(f"Error in OpenAI Vision API call: {str(e)}")
        return {
            "error": "Failed to process with OpenAI Vision API",
            "details": str(e)
        }
