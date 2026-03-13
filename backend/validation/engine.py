"""
Validation engine that compares extracted values against material standards.
Returns PASS/FAIL/WARNING per field and overall compliance status.
"""
from typing import Optional
from sqlalchemy.orm import Session
from models import MaterialStandard, ExtractedData


def validate_extracted_data(extracted: ExtractedData, db: Session) -> dict:
    """
    Validate extracted data against the best matching standard.
    Returns validation results dict.
    """
    # Find the best matching standard
    standard = _find_matching_standard(extracted, db)

    if standard is None:
        # Use a default standard (ASTM A106 Grade B) for demo purposes
        standard = db.query(MaterialStandard).first()

    if standard is None:
        return {
            "overall_status": "WARNING",
            "standard_used": "No standard available",
            "chemical_results": {},
            "mechanical_results": {},
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "warning_checks": 1,
        }

    chemical_results = _validate_chemical(extracted, standard)
    mechanical_results = _validate_mechanical(extracted, standard)

    # Aggregate results
    all_results = list(chemical_results.values()) + list(mechanical_results.values())
    total = len(all_results)
    passed = sum(1 for r in all_results if r["status"] == "PASS")
    failed = sum(1 for r in all_results if r["status"] == "FAIL")
    warnings = sum(1 for r in all_results if r["status"] == "WARNING")

    # Overall status
    if failed > 0:
        overall = "FAIL"
    elif warnings > 0:
        overall = "WARNING"
    elif passed > 0:
        overall = "PASS"
    else:
        overall = "PENDING"

    return {
        "overall_status": overall,
        "standard_used": f"{standard.standard_name} {standard.grade}",
        "chemical_results": chemical_results,
        "mechanical_results": mechanical_results,
        "total_checks": total,
        "passed_checks": passed,
        "failed_checks": failed,
        "warning_checks": warnings,
    }


def _find_matching_standard(extracted: ExtractedData, db: Session) -> Optional[MaterialStandard]:
    """Try to match the extracted specification to a known standard."""
    if extracted.specification:
        spec_upper = extracted.specification.upper()
        standards = db.query(MaterialStandard).all()
        for std in standards:
            if std.standard_name.upper() in spec_upper:
                return std

    if extracted.material_grade:
        grade_upper = extracted.material_grade.upper()
        standards = db.query(MaterialStandard).all()
        for std in standards:
            if std.standard_name.upper() in grade_upper or std.grade.upper() in grade_upper:
                return std

    return None


def _check_range(value: Optional[float], min_val: Optional[float], max_val: Optional[float]) -> dict:
    """Check if a value is within the specified range."""
    if value is None:
        return {"status": "NOT FOUND", "value": None, "min": min_val, "max": max_val}

    if min_val is None and max_val is None:
        return {"status": "N/A", "value": value, "min": None, "max": None}

    in_range = True
    if min_val is not None and value < min_val:
        in_range = False
    if max_val is not None and value > max_val:
        in_range = False

    return {
        "status": "PASS" if in_range else "FAIL",
        "value": value,
        "min": min_val,
        "max": max_val,
    }


def _validate_chemical(extracted: ExtractedData, standard: MaterialStandard) -> dict:
    """Validate chemical composition fields."""
    return {
        "Carbon (C)": {
            **_check_range(extracted.carbon, standard.carbon_min, standard.carbon_max),
            "unit": "%",
        },
        "Manganese (Mn)": {
            **_check_range(extracted.manganese, standard.manganese_min, standard.manganese_max),
            "unit": "%",
        },
        "Silicon (Si)": {
            **_check_range(extracted.silicon, standard.silicon_min, standard.silicon_max),
            "unit": "%",
        },
        "Chromium (Cr)": {
            **_check_range(extracted.chromium, standard.chromium_min, standard.chromium_max),
            "unit": "%",
        },
        "Nickel (Ni)": {
            **_check_range(extracted.nickel, standard.nickel_min, standard.nickel_max),
            "unit": "%",
        },
        "Phosphorus (P)": {
            **_check_range(extracted.phosphorus, standard.phosphorus_min, standard.phosphorus_max),
            "unit": "%",
        },
        "Sulfur (S)": {
            **_check_range(extracted.sulfur, standard.sulfur_min, standard.sulfur_max),
            "unit": "%",
        },
    }


def _validate_mechanical(extracted: ExtractedData, standard: MaterialStandard) -> dict:
    """Validate mechanical property fields."""
    return {
        "Yield Strength": {
            **_check_range(extracted.yield_strength, standard.yield_strength_min, standard.yield_strength_max),
            "unit": "MPa",
        },
        "Tensile Strength": {
            **_check_range(extracted.tensile_strength, standard.tensile_strength_min, standard.tensile_strength_max),
            "unit": "MPa",
        },
        "Elongation": {
            **_check_range(extracted.elongation, standard.elongation_min, standard.elongation_max),
            "unit": "%",
        },
        "Hardness": {
            **_check_range(extracted.hardness, standard.hardness_min, standard.hardness_max),
            "unit": "HB",
        },
        "Impact Energy": {
            **_check_range(extracted.impact_energy, standard.impact_energy_min, standard.impact_energy_max),
            "unit": "J",
        },
    }
