from Backend.validation.web_scraper.npino_scraper import scrape_npino
from Backend.validation.confidence.confidence import evaluate_all
from Backend.validation.npi_registry import validate_via_npi_registry
from Backend.validation.google_maps_validation import validate_via_google

def run_validations(extracted):
    npi_result = validate_via_npi_registry(extracted["npi"])
    web_result = scrape_npino(extracted["npi"])
    maps_result = validate_via_google(extracted["address"])

    method_results = {
        "npi_registry": npi_result,
        "web_scrape": web_result,
        "google_maps": maps_result
    }

    method_scores, combined_fields, per_method_fields, overall = evaluate_all(extracted, method_results)

    return {
        "method_confidences": {m: v["method_score"] for m, v in method_scores.items()},
        "combined_field_confidences": combined_fields,
        "overall_confidence": overall
    }

if __name__ == "__main__":
    # Example dummy provider input (replace this with your extraction logic)
    extracted = {
        "npi": "1003000480",
        "name": "Kevin Bradley Rothchild",
        "address": "1550 S Potomac St Ste 100, Aurora, CO 80012",
        "phone": "303-493-7000",
        "specialty": "Pediatrics"
    }

    result = run_validations(extracted)

    print("\n================= 🩺 PROVIDER VALIDATION SUMMARY =================")
    print(f"👤 Name: {extracted['name']}")
    print(f"📛 NPI: {extracted['npi']}")
    print(f"🏢 Address: {extracted['address']}")
    print(f"📞 Phone: {extracted['phone']}")
    print(f"💼 Specialty: {extracted['specialty']}")
    print("------------------------------------------------------------")
    print("📊 Method Confidence Scores:")
    for method, score in result['method_confidences'].items():
        print(f"   • {method}: {score:.2f}%")
    print("------------------------------------------------------------")
    print("📈 Combined Field Confidences:")
    for field, score in result['combined_field_confidences'].items():
        print(f"   • {field}: {score:.2f}%")
    print("------------------------------------------------------------")
    print(f"✨ Overall Confidence: {result['overall_confidence']:.2f}%")
    print("============================================================\n")
