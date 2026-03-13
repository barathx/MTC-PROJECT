"""
Material standards data for validation.
Contains specification ranges for common steel grades.
"""
from sqlalchemy.orm import Session
from models import MaterialStandard


def seed_standards(db: Session):
    """Populate material_standards table with common steel specifications."""
    # Check if already seeded
    if db.query(MaterialStandard).count() > 0:
        return

    standards = [
        # ASTM A106 Grade B - Seamless Carbon Steel Pipe
        MaterialStandard(
            standard_name="ASTM A106", grade="Grade B",
            carbon_min=0.0, carbon_max=0.30,
            manganese_min=0.29, manganese_max=1.06,
            silicon_min=0.10, silicon_max=None,
            chromium_min=0.0, chromium_max=0.40,
            nickel_min=0.0, nickel_max=0.40,
            phosphorus_min=0.0, phosphorus_max=0.035,
            sulfur_min=0.0, sulfur_max=0.035,
            yield_strength_min=240, yield_strength_max=None,
            tensile_strength_min=415, tensile_strength_max=None,
            elongation_min=30.0, elongation_max=None,
            hardness_min=None, hardness_max=None,
            impact_energy_min=None, impact_energy_max=None,
        ),
        # ASTM A516 Grade 70 - Pressure Vessel Plates
        MaterialStandard(
            standard_name="ASTM A516", grade="Grade 70",
            carbon_min=0.0, carbon_max=0.28,
            manganese_min=0.85, manganese_max=1.20,
            silicon_min=0.15, silicon_max=0.40,
            chromium_min=None, chromium_max=None,
            nickel_min=None, nickel_max=None,
            phosphorus_min=0.0, phosphorus_max=0.035,
            sulfur_min=0.0, sulfur_max=0.035,
            yield_strength_min=260, yield_strength_max=None,
            tensile_strength_min=485, tensile_strength_max=620,
            elongation_min=21.0, elongation_max=None,
            hardness_min=None, hardness_max=None,
            impact_energy_min=None, impact_energy_max=None,
        ),
        # ASTM A105 - Forging Carbon Steel
        MaterialStandard(
            standard_name="ASTM A105", grade="Standard",
            carbon_min=0.0, carbon_max=0.35,
            manganese_min=0.60, manganese_max=1.05,
            silicon_min=0.10, silicon_max=0.35,
            chromium_min=0.0, chromium_max=0.30,
            nickel_min=0.0, nickel_max=0.40,
            phosphorus_min=0.0, phosphorus_max=0.035,
            sulfur_min=0.0, sulfur_max=0.040,
            yield_strength_min=250, yield_strength_max=None,
            tensile_strength_min=485, tensile_strength_max=None,
            elongation_min=22.0, elongation_max=None,
            hardness_min=None, hardness_max=187,
            impact_energy_min=None, impact_energy_max=None,
        ),
        # ASTM A333 Grade 6 - Low-Temperature Pipe
        MaterialStandard(
            standard_name="ASTM A333", grade="Grade 6",
            carbon_min=0.0, carbon_max=0.30,
            manganese_min=0.29, manganese_max=1.06,
            silicon_min=0.10, silicon_max=None,
            chromium_min=None, chromium_max=None,
            nickel_min=None, nickel_max=None,
            phosphorus_min=0.0, phosphorus_max=0.025,
            sulfur_min=0.0, sulfur_max=0.025,
            yield_strength_min=240, yield_strength_max=None,
            tensile_strength_min=415, tensile_strength_max=None,
            elongation_min=30.0, elongation_max=None,
            hardness_min=None, hardness_max=None,
            impact_energy_min=18, impact_energy_max=None,
        ),
        # ASTM A182 F316 - Stainless Steel Forging
        MaterialStandard(
            standard_name="ASTM A182", grade="F316",
            carbon_min=0.0, carbon_max=0.08,
            manganese_min=0.0, manganese_max=2.00,
            silicon_min=0.0, silicon_max=1.00,
            chromium_min=16.0, chromium_max=18.0,
            nickel_min=10.0, nickel_max=14.0,
            phosphorus_min=0.0, phosphorus_max=0.045,
            sulfur_min=0.0, sulfur_max=0.030,
            yield_strength_min=205, yield_strength_max=None,
            tensile_strength_min=515, tensile_strength_max=None,
            elongation_min=30.0, elongation_max=None,
            hardness_min=None, hardness_max=217,
            impact_energy_min=None, impact_energy_max=None,
        ),
    ]

    db.add_all(standards)
    db.commit()
