from parser import extract_provider_info, extract_with_vision_api

def print_loading_animation():
    import sys
    import time
    
    for i in range(3):
        for c in ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']:
            sys.stdout.write(f'\rProcessing document {c} ')
            sys.stdout.flush()
            time.sleep(0.1)

# Main execution
print("Medical Document Information Extractor")
print("-" * 35)
pdf_path = input("Enter the path of your scanned provider PDF: ").strip()

print("\nProcessing document with OpenAI Vision API...")
print_loading_animation()

# Use the Vision API directly
info = extract_with_vision_api(pdf_path)

print("\n" + "="*50)
print("Document Processing Complete")
print("-" * 50)

print("\nDocument Analysis Results:")
print("-" * 50)

# Display results
print("\nExtracted Information:")
print("-" * 50)

if isinstance(info, dict):
    if 'error' in info:
        print(f"Error: {info['error']}")
        if 'details' in info:
            print(f"Details: {info['details']}")
    else:
        for key, value in info.items():
            if value:  # Only show non-empty fields
                print(f"{key}: {value}")
else:
    print(info)

print("\n" + "="*50)
print("Analysis Complete")
print("="*50)