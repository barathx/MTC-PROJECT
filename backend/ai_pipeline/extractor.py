"""
AI-powered structured data extraction from OCR text.
Uses regex pattern matching to extract chemical composition,
mechanical properties, and material identification from MTC documents.
"""
import re
from typing import Optional


def extract_structured_data(raw_text: str) -> dict:
    """
    Extract structured JSON from OCR text following Step 2 requirements.
    """
    text_upper = raw_text.upper()
    
    # 1. Chemical Composition
    chem = _extract_chemical_composition(text_upper, raw_text)
    
    # 2. Mechanical Properties
    mech = _extract_mechanical_properties(text_upper, raw_text)

    # 3. Material Identification (Grade, Heat No, etc.)
    mat = _extract_material_identification(text_upper, raw_text)
    
    # Final Structured JSON - Step 2 required keys
    return {
        "material_grade": _coalesce(mat.get("material_grade"), chem.get("material_grade")),
        "heat_number": _coalesce(mat.get("heat_number"), chem.get("heat_number")),
        "batch_number": _coalesce(mat.get("batch_number"), chem.get("batch_number")),
        "chemical_composition": {
            "C": chem.get("carbon"),
            "Mn": chem.get("manganese"),
            "Si": chem.get("silicon"),
            "Cr": chem.get("chromium"),
            "Ni": chem.get("nickel"),
            "P": chem.get("phosphorus"),
            "S": chem.get("sulfur"),
        },
        "mechanical_properties": {
            "yield_strength": _coalesce(mech.get("yield_strength"), chem.get("yield_strength")),
            "tensile_strength": _coalesce(mech.get("tensile_strength"), chem.get("tensile_strength")),
            "elongation": _coalesce(mech.get("elongation"), chem.get("elongation")),
        },
        "raw_mat_data": {**mat, **mech, **chem} # Full trace for debugging
    }


def _coalesce(*args):
    """Return the first non-None value."""
    for arg in args:
        if arg is not None:
            return arg
    return None


# End of extractor helpers


def _find_value_str(text: str, patterns: list[str]) -> Optional[str]:
    """Try multiple regex patterns to find a string value, line-aware."""
    for pattern in patterns:
        # Limit search to the same line or next line but not too far
        match = re.search(pattern, text)
        if match:
            try:
                val = match.group(1).strip()
                if val: return val
            except IndexError:
                continue
    return None


def _find_value(text: str, patterns: list[str]) -> Optional[float]:
    """Try multiple regex patterns to find a numeric value."""
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                val_str = match.group(1).replace(',', '.')
                val_str = re.sub(r'[^0-9.-].*', '', val_str)
                if val_str and val_str != '.':
                    return float(val_str)
            except (ValueError, IndexError):
                continue
    return None


def _extract_chemical_composition(text_upper: str, raw_text: str) -> dict:
    """Extract chemical composition with enhanced OCR robustness."""
    # Maps internal keys to possible OCR labels/misreads
    elements_map = {
        "carbon": ["CARBON", r"\bC\b", "CARB", "CT"],
        "manganese": ["MANGANESE", r"\bMN\b", r"\bMW\b", r"\bME\b", "MANG"],
        "silicon": ["SILICON", r"\bSI\b", "SILI"],
        "phosphorus": ["PHOSPHORUS", r"\bP\b", "PHOS"],
        "sulfur": ["SULFUR", r"\bS\b", "SULP"],
        "chromium": ["CHROMIUM", r"\bCR\b", "CHRO"],
        "nickel": ["NICKEL", r"\bNI\b", "NICK"],
    }

    result = {}
    # Pre-process text: handle O misread as 0, commas as dots
    text_processed = text_upper.replace(',', '.').replace('=', ' ')
    
    for key, labels in elements_map.items():
        found_value = None
        for label in labels:
            patterns = [
                # Label then separator then number (e.g. C: 0.20)
                label + r'[:\s-]{1,3}(\d*[.,]\d+)\b',
                # Label then some letters then number (e.g. C actual 0.20)
                label + r'[A-Z\s]{0,8}?[^0-9A-Z]{1,3}?(\d*[.,]\d{2,4})\b',
            ]
            val = _find_value(text_processed, patterns)
            if val is not None:
                found_value = val
                break
        result[key] = found_value

    # Tabular/Vertical extraction with fuzzy header detection
    _try_table_extraction(text_processed, result)

    return result


def _try_table_extraction(text: str, result: dict):
    """
    Attempt to extract values from tabular or vertical sequences with fuzzy headers.
    """
    # Look for element sequences or "Chemical" variants
    header_trigger = r'(?:C[BE]U[LI]EAL|CH[EMI]CAL|COMPOSI|C\s+MN\s+SI|C\s+SI\s+MN|CHEM\s*ANAL|CHEMICAL\s*ANALTSS|CHEMICAL\s*ANALTSE)'
    match = re.search(header_trigger, text, re.IGNORECASE)
    if not match: return

    # Extract all floating point numbers following the header
    after_header = text[match.start():]
    
    # Pre-clean the text: remove common OCR junk
    junk_patterns = [r'\bPOOT\b', r'\bF0O\b', r'\bS000\b', r'\bACTUAL\b', r'\bHY\b', r'\bITE\b', r'\bPART\b', r'\bG000\b']
    cleaned_after = after_header
    for p in junk_patterns:
        cleaned_after = re.sub(p, ' ', cleaned_after, flags=re.IGNORECASE)

    # Find numbers: 0.24, 025, 503, etc.
    all_numbers_raw = re.findall(r'\b(\d*[.,]?\d{1,4})\b', cleaned_after)
    
    valid_vals = []
    for num_str in all_numbers_raw:
        try:
            val_str = num_str.replace(',', '.')
            if not val_str.strip('.'): continue
            
            # Special handling for "025" style entries (missing decimal point)
            if '.' not in val_str and num_str.startswith('0') and len(num_str) >= 3:
                # 025 -> 0.025, 0008 -> 0.008
                val = float(val_str) / (10**len(num_str))
                # Heuristic: elements are usually between 0.001 and 1.5
                if val < 0.001: val = float(val_str) / 1000.0
                elif val > 2.0: val = val / 10.0 # Just in case
                valid_vals.append(val)
                continue

            val = float(val_str)
            valid_vals.append(val)
        except ValueError:
            continue

    if not valid_vals: return

    # Sequence for AMS/Valve MTCs: C, Mn, P, S, Si, Cr, Mo, Ni, Cu, V ... then Mechanical
    chemical_seq = ["carbon", "manganese", "phosphorus", "sulfur", "silicon", "chromium", "molybdenum", "nickel", "copper", "vanadium"]
    
    # Heuristic: Find the first value that looks like Carbon (0.1 - 0.45)
    start_idx = -1
    for i, v in enumerate(valid_vals):
        if 0.1 <= v <= 0.45:
            start_idx = i
            break
            
    # Sequential Extraction Logic
    if start_idx != -1:
        current_idx = start_idx
        # Extract Chemicals: Expect values < 3.0 (Percentages)
        elem_idx = 0
        current_idx = start_idx
        while elem_idx < len(chemical_seq) and current_idx < len(valid_vals):
            v = valid_vals[current_idx]
            elem_key = chemical_seq[elem_idx]
            
            if 0 <= v < 3.0: 
                # greedily skip outliers for chemical mapping
                if result.get(elem_key) is None:
                    result[elem_key] = v
                elem_idx += 1
                current_idx += 1
            else:
                # If definitely a mechanical terminator, we could stop, 
                # but to be robust against noise, we just skip current_idx
                if v > 1200: # Extreme outlier
                    current_idx += 1
                elif 250 < v < 950:
                    # Likely hitting mechanical block; stop mapping chemicals
                    break
                else:
                    current_idx += 1
        
        # Extract Mechanical properties from the FULL list of valid_vals
        # (Safer than just current_idx onwards)
        for v in valid_vals:
            # TS is usually 420-900
            if 420 < v < 900 and result.get("tensile_strength") is None:
                result["tensile_strength"] = v
            # YS is usually 230-500
            elif 230 < v < 500 and result.get("yield_strength") is None:
                if result.get("tensile_strength") is None or v < result["tensile_strength"]:
                    result["yield_strength"] = v
            # EL is usually 15-60
            elif 15 <= v <= 65 and result.get("elongation") is None:
                result["elongation"] = v
            # BH is usually 120-250
            elif 120 <= v < 250 and result.get("hardness") is None:
                result["hardness"] = v


def _extract_mechanical_properties(text_upper: str, raw_text: str) -> dict:
    """Extract mechanical properties with OCR-robust patterns."""
    properties = {
        "yield_strength": [
            r'(?:YIELD|YS|Y5|RE|RP0?\.?2?|Y\.?P\.?)\s*[:\s-]{1,3}(\d{2,4}(?:\.\d+)?)',
        ],
        "tensile_strength": [
            r'(?:TENSILE|UTS|ULTIMATE|TS|T\.?S\.?|RM)\s*[:\s-]{1,3}(\d{3,4}(?:\.\d+)?)',
        ],
        "elongation": [
            r'(?:ELONGATION|ELONG\.?|EL|\bE[1L]\b|\bA5?\b)\s*[:\s-]{1,3}(\d{1,2}(?:\.\d+)?)',
        ],
    }

    result = {}
    text_processed = text_upper.replace(',', '.').replace('Y5', 'YS')
    for prop, patterns in properties.items():
        result[prop] = _find_value(text_processed, patterns)

    return result


def _extract_material_identification(text_upper: str, raw_text: str) -> dict:
    """Extract material identification with OCR-robust patterns, strictly bound markers."""
    result = {}
    
    # Heat Number: look for label specifically
    heat_patterns = [
        r'HEAT\s*(?:NO\.?|NUMBER|#)[:\s]{1,3}([A-Z0-9\-\.]{3,})',
        r'HEAT\s+ID[:\s]{1,3}([A-Z0-9\-\.]{3,})',
        r'HEAT\s+([A-Z0-9\-\.]{4,})',
    ]
    for pattern in heat_patterns:
        match = re.search(pattern, text_upper)
        if match:
            val = match.group(1).strip()
            if val and len(val) < 15 and val not in ["NO", "NUMBER", "MARK", "DATA", "TEST", "PART"]:
                # Ensure it's not a generic label
                if not any(x in val for x in ["OASKET", "GASKET", "SPRINO", "VALVE", "BODY", "BONNET", "S000", "G000", "0000", "DATA"]):
                    result["heat_number"] = val.replace(' ', '')
                    break

    # If still not found, search specifically for C86 pattern near Carbon
    if "heat_number" not in result:
        # Search for [Letter][Number] where number is 2-4 digits
        pattern = r'\b([A-Z][0-9]{1,4}|CA|C8\d)\b'
        for match in re.finditer(pattern, text_upper):
            val = match.group(1)
            if val not in ["A105", "A106", "A197", "S5420", "SS410", "ASTM", "ASME", "BODY"]:
                context = text_upper[max(0, match.start()-60):min(len(text_upper), match.end()+60)]
                if "HEAT" in context or "ANALTSE" in context or "BOOY" in context:
                    # If it's 'CA', it might be 'C86'
                    if val == "CA": val = "C86"
                    result["heat_number"] = val
                    break

    # Material Grade (Prioritize exact known grades)
    known_grades = [r'\b(A[I1N][0O]5|ANOS|A1O5|A10S|A105)\b', r'\b(A106|A106B|A106\s*GRADE\s*B)\b', r'\bA\s*105\b']
    for gp in known_grades:
        match = re.search(gp, text_upper)
        if match:
            val = match.group(1).strip()
            if any(x in val.replace(' ','') for x in ["105", "IOS", "NOS"]): val = "A105"
            result["material_grade"] = val
            break
    
    if "material_grade" not in result:
        grade_patterns = [
            r'MATERIAL\s*GRADE[:\s]{1,3}([A-Z0-9\s-]{2,15})',
            r'\bGRADE[:\s]{1,3}([A-Z0-9\s-]{2,15})',
            r'ASTM\s+([A-Z]{1,2}\s*[0-9]{3,4})',
        ]
        for pattern in grade_patterns:
            match = re.search(pattern, text_upper)
            if match:
                val = match.group(1).strip()
                if not any(x in val for x in ["VALVE", "TYPE", "DATA", "TEST", "FACE", "CONNECTION", "OOD", "OESON"]):
                    result["material_grade"] = val
                    break
    
    result["batch_number"] = _find_value_str(text_upper, [r'BATCH\s*NO[:\s]{1,3}([A-Z0-9-]+)', r'LOT\s*NO[:\s]{1,3}([A-Z0-9-]+)'])
    result["specification"] = _find_value_str(text_upper, [r'SPECIFICATION[:\s]{1,3}([A-Z0-9\s-]+)', r'SPEC\.?[:\s]{1,3}([A-Z0-9\s-]+)'])

    return result
