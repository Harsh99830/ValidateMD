import os
import pandas as pd
import time
from Backend.validation.validate_provider import run_validations
from Backend.validation.pdf_extract.parser import extract_with_vision_api
from Backend.validation.pdf_extract.ocr_engine import extract_text_from_pdf, clean_ocr_text

# ----------------------------------------------------------
# STEP 1: Detect file type and extract information
# ----------------------------------------------------------

def extract_from_csv(file_path):
    """Extract provider data from CSV."""
    df = pd.read_csv(file_path)
    providers = []
    for _, row in df.iterrows():
        providers.append({
            "npi": str(row.get("npi_number") or row.get("NPI_Number") or ""),
            "name": row.get("name") or f"{row.get('first_name', '')} {row.get('last_name', '')}",
            "address": row.get("Address") or row.get("address"),
            "phone": str(row.get("Phone") or ""),
            "specialty": row.get("Specialty") or row.get("speciality") or ""
        })
    return providers

def extract_from_pdf(file_path):
    """Extract provider data from PDF using Vision API."""
    print("\n🧠 Extracting provider info from PDF using OpenAI Vision API...")
    info = extract_with_vision_api(file_path)
    
    if "error" in info:
        print(f"⚠️ Vision API failed: {info['error']}")
        return []
    
    provider = {
        "npi": info.get("NPI_Number", ""),
        "name": info.get("Name", ""),
        "address": info.get("Address", ""),
        "phone": info.get("Phone", ""),
        "specialty": info.get("Specialty", "")
    }
    return [provider]

def detect_file_type(file_path):
    """Detect if file is CSV or PDF and call the appropriate extractor."""
    ext = file_path.lower().split(".")[-1]
    if ext == "csv":
        return extract_from_csv(file_path)
    elif ext == "pdf":
        return extract_from_pdf(file_path)
    else:
        raise ValueError("❌ Unsupported file type. Please provide a .csv or .pdf file.")

# ----------------------------------------------------------
# STEP 2: Run validations for each provider
# ----------------------------------------------------------

def process_providers(providers):
    """Run validations and compute confidence scores."""
    all_results = []
    
    for idx, provider in enumerate(providers, start=1):
        print("\n" + "="*70)
        print(f"🔍 VALIDATING PROVIDER {idx}")
        print("="*70)
        print(f"👤 Name: {provider['name']}")
        print(f"📛 NPI: {provider['npi']}")
        print(f"🏢 Address: {provider['address']}")
        print(f"📞 Phone: {provider['phone']}")
        print(f"💼 Specialty: {provider['specialty']}")
        print("-"*70)

        try:
            result = run_validations(provider)

            print("📊 Method Confidence Scores:")
            for method, score in result["method_confidences"].items():
                print(f"   • {method}: {score:.2f}%")

            print("------------------------------------------------------------")
            print("📈 Combined Field Confidences:")
            for field, score in result["combined_field_confidences"].items():
                print(f"   • {field}: {score:.2f}%")

            print("------------------------------------------------------------")
            print(f"✨ Overall Confidence: {result['overall_confidence']:.2f}%")
            print("="*70)

            all_results.append({
                **provider,
                **result
            })
        except Exception as e:
            print(f"❌ Validation failed for {provider['name']}: {e}")
    
    return all_results

# ----------------------------------------------------------
# STEP 3: Entry point
# ----------------------------------------------------------

def main():
    print("🩺 PROVIDER DATA VALIDATION SYSTEM")
    print("="*60)

    input_folder = "inputs"
    if not os.path.exists(input_folder):
        print("❌ 'inputs' folder not found. Please create it and add your file.")
        return

    # List available files
    files = [f for f in os.listdir(input_folder) if f.lower().endswith((".pdf", ".csv"))]
    if not files:
        print("❌ No input file found in 'inputs' folder.")
        return

    print("\n📂 Available files in 'inputs/' folder:")
    for i, f in enumerate(files, start=1):
        print(f"   {i}. {f}")

    chosen_file = input("\n✏️  Enter the exact filename you want to process (e.g. data.csv): ").strip()
    file_path = os.path.join(input_folder, chosen_file)

    if not os.path.exists(file_path):
        print(f"❌ File '{chosen_file}' not found in 'inputs' folder.")
        return

    # Extract provider data
    providers = detect_file_type(file_path)
    if not providers:
        print("❌ No provider data could be extracted.")
        return

    start_time = time.time()
    results = process_providers(providers)
    end_time = time.time()

    # Save all results to outputs
    os.makedirs("outputs", exist_ok=True)
    output_file = "outputs/final_validation_results.csv"
    pd.DataFrame(results).to_csv(output_file, index=False)

    print(f"\n✅ All results saved to {output_file}")
    print(f"⏱️  Process completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
