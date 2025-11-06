# confidence.py
from rapidfuzz import fuzz
import math

# ---------- CONFIG: weights (tweak as needed) ----------
# Importance of each field when computing a method's score and the final overall score
FIELD_WEIGHTS = {
    "npi": 0.30,        # legal identifier (most important)
    "name": 0.25,
    "address": 0.20,
    "phone": 0.15,
    "specialty": 0.10
}

# Reliability weights for each validation method when combining per-field confidences
METHOD_WEIGHTS = {
    "npi_registry": 0.45,    # official API, most reliable
    "web_scrape": 0.30,      # scraped site (npino) - good but sometimes noisy
    "google_maps": 0.25      # geocode/place match - good for address/phone
}

# Per-field thresholds or tuning
PHONE_EXACT_BONUS = 10      # extra points if phone exact match
NPI_EXACT_SCORE = 100       # exact NPI match => 100 for npi field

# ---------- Utility similarity functions ----------
def name_similarity(a: str, b: str) -> float:
    """Return 0-100 fuzzy similarity for names (token set ratio)."""
    if not a or not b:
        return 0.0
    return float(fuzz.token_set_ratio(a, b))

def address_similarity(a: str, b: str) -> float:
    """Return 0-100 fuzzy similarity for addresses (token set ratio)."""
    if not a or not b:
        return 0.0
    return float(fuzz.token_set_ratio(a, b))

def specialty_similarity(a: str, b: str) -> float:
    """Return 0-100 similarity for specialty strings (case-insensitive exact or fuzzy)."""
    if not a or not b:
        return 0.0
    a_clean = a.lower().strip()
    b_clean = b.lower().strip()
    if a_clean == b_clean:
        return 100.0
    return float(fuzz.token_sort_ratio(a_clean, b_clean))

def phone_similarity(a: str, b: str) -> float:
    """Return 0-100 phone similarity. Normalize digits and prefer exact match."""
    if not a or not b:
        return 0.0
    da = "".join(ch for ch in a if ch.isdigit())
    db = "".join(ch for ch in b if ch.isdigit())
    if not da or not db:
        return 0.0
    if da == db:
        return min(100.0, 100.0 + PHONE_EXACT_BONUS)  # capped later
    # partial match: compute ratio of longest common substring over max length
    lev = fuzz.ratio(da, db)
    return float(lev)

def npi_similarity(a: str, b: str) -> float:
    """If NPI strings equal -> 100 else 0 (optionally fuzzy)"""
    if not a or not b:
        return 0.0
    a_digits = "".join(ch for ch in a if ch.isdigit())
    b_digits = "".join(ch for ch in b if ch.isdigit())
    return 100.0 if (a_digits and b_digits and a_digits == b_digits) else 0.0

# ---------- Compute field-level confidence for a single method ----------
def field_confidence_for_method(field: str, extracted_value, method_value) -> float:
    """Dispatch to appropriate similarity function and return score 0..100 (cap to 100)."""
    if field == "name":
        s = name_similarity(extracted_value, method_value)
    elif field == "address":
        s = address_similarity(extracted_value, method_value)
    elif field == "specialty":
        s = specialty_similarity(extracted_value, method_value)
    elif field == "phone":
        s = phone_similarity(extracted_value, method_value)
    elif field == "npi":
        s = npi_similarity(extracted_value, method_value)
    else:
        s = 0.0
    # cap 0..100
    s = max(0.0, min(100.0, float(s)))
    return s

# ---------- Compute a single method's overall confidence (weighted field avg) ----------
def compute_method_score(method_name: str, extracted: dict, method_result: dict, fields=None):
    """
    method_name: one of 'npi_registry', 'web_scrape', 'google_maps'
    extracted: dict from OCR / claimed fields (keys: name, address, phone, specialty, npi)
    method_result: dict returned by that method scraped or API (similar keys)
    returns: (method_score [0-100], breakdown dict of field confidences)
    """
    if fields is None:
        fields = list(FIELD_WEIGHTS.keys())
    breakdown = {}
    weighted_sum = 0.0
    weight_total = 0.0
    for f in fields:
        ext_val = extracted.get(f)
        m_val = method_result.get(f)
        conf = field_confidence_for_method(f, ext_val, m_val)
        # for NPI registry you may trust NPI exact match more: but we already do npi_similarity exact=100.
        breakdown[f] = round(conf, 2)
        w = FIELD_WEIGHTS.get(f, 0.0)
        weighted_sum += conf * w
        weight_total += w
    method_score = (weighted_sum / weight_total) if weight_total > 0 else 0.0
    return round(method_score, 2), breakdown

# ---------- Combine per-field confidences across methods ---------- 
def compute_combined_field_confidences(extracted: dict, method_results: dict, method_weights=None):
    """
    method_results: dict with keys = 'npi_registry','web_scrape','google_maps' -> each is method_result dict
    method_weights (optional): per-method reliability weights, default from METHOD_WEIGHTS
    returns: dict {field: combined_confidence}, and per-method field confidences
    """
    if method_weights is None:
        method_weights = METHOD_WEIGHTS
    fields = list(FIELD_WEIGHTS.keys())
    # compute per-method field confidences first
    per_method_field = {}
    for method_name, result in method_results.items():
        per_field = {}
        for f in fields:
            per_field[f] = field_confidence_for_method(f, extracted.get(f), result.get(f))
        per_method_field[method_name] = per_field

    # combine per field using method weights
    combined = {}
    for f in fields:
        num = 0.0
        den = 0.0
        for method_name, per_field in per_method_field.items():
            w = method_weights.get(method_name, 0.0)
            num += per_field[f] * w
            den += w
        combined[f] = round((num / den) if den else 0.0, 2)
    return combined, per_method_field

# ---------- Compute overall provider confidence ----------
def compute_overall_confidence(combined_field_confidences: dict, field_weights=None):
    """Final overall confidence = weighted avg of per-field combined confidences"""
    if field_weights is None:
        field_weights = FIELD_WEIGHTS
    num = 0.0
    den = 0.0
    for f, conf in combined_field_confidences.items():
        w = field_weights.get(f, 0.0)
        num += conf * w
        den += w
    overall = (num / den) if den else 0.0
    return round(overall, 2)

# ---------- Helper: full pipeline given extracted + method outputs ----------
def evaluate_all(extracted: dict, method_results: dict, method_weights=None, field_weights=None):
    """
    Returns:
      - method_scores: {method_name: (score, breakdown)}
      - combined_fields: {field: confidence}
      - per_method_field_confidences: {method_name: {field: confidence}}
      - overall_confidence: float
    """
    # compute each method score
    method_scores = {}
    for method_name, result in method_results.items():
        score, breakdown = compute_method_score(method_name, extracted, result)
        method_scores[method_name] = {"method_score": score, "breakdown": breakdown}

    # combined per-field confidences
    combined_fields, per_method_field_confidences = compute_combined_field_confidences(
        extracted, method_results, method_weights
    )

    # normalize combined_fields to 0..100 already
    overall = compute_overall_confidence(combined_fields, field_weights)
    return method_scores, combined_fields, per_method_field_confidences, overall

# ---------- Example quick demo (callable) ----------
def demo():
    """
    Example usage. Replace the example dicts with your real outputs.
    """
    extracted = {
        "npi": "1003000480",
        "name": "Kevin Bradley Rothchild",
        "address": "1550 S Potomac St Ste 100, Aurora, CO 80012",
        "phone": "303-493-7000",
        "specialty": "Pediatrics"
    }

    # Example method outputs (replace with your actual method outputs)
    npireg = {
        "npi": "1003000480",
        "name": "Kevin B Rothchild",
        "address": "1550 S Potomac St Ste 100, Aurora, CO 80012",
        "phone": "3034937000",
        "specialty": "Pediatrics"
    }
    web = {
        "npi": "1003000480",
        "name": "NPI 1003000480 Kevin Bradley Rothchild in Aurora - Address, Medicare Status, and Contact",
        "address": "1550 S Potomac St, Aurora, CO",
        "phone": "(303) 493-7000",
        "specialty": "Pediatrics"
    }
    maps = {
        "npi": None,
        "name": None,
        "address": "1550 S Potomac St Ste 100, Aurora, CO 80012",
        "phone": "+1 303-493-7000",
        "specialty": None
    }

    methods = {"npi_registry": npireg, "web_scrape": web, "google_maps": maps}
    method_scores, combined_fields, per_method_fields, overall = evaluate_all(extracted, methods)

    print("=== METHOD SCORES ===")
    for method, v in method_scores.items():
        print(method, v["method_score"], v["breakdown"])
    print("\n=== PER-FIELD COMBINED CONFIDENCES ===")
    for f, c in combined_fields.items():
        print(f, c)
    print("\n=== OVERALL CONFIDENCE ===")
    print(overall)

if __name__ == "__main__":
    demo()
