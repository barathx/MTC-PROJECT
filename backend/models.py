from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="engineer")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    documents = relationship("Document", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)
    file_size = Column(Integer, nullable=True)
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="documents")
    extracted_data = relationship("ExtractedData", back_populates="document", uselist=False)
    validation_result = relationship("ValidationResult", back_populates="document", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="document")


class ExtractedData(Base):
    __tablename__ = "extracted_data"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)

    # Raw OCR text
    raw_text = Column(Text, nullable=True)

    # Chemical Composition (stored as percentages)
    carbon = Column(Float, nullable=True)
    manganese = Column(Float, nullable=True)
    silicon = Column(Float, nullable=True)
    chromium = Column(Float, nullable=True)
    nickel = Column(Float, nullable=True)
    phosphorus = Column(Float, nullable=True)
    sulfur = Column(Float, nullable=True)

    # Mechanical Properties
    yield_strength = Column(Float, nullable=True)       # MPa
    tensile_strength = Column(Float, nullable=True)      # MPa
    elongation = Column(Float, nullable=True)            # %
    hardness = Column(Float, nullable=True)              # HB/HRC
    impact_energy = Column(Float, nullable=True)         # Joules

    # Material Identification
    heat_number = Column(String(100), nullable=True)
    batch_number = Column(String(100), nullable=True)
    material_grade = Column(String(100), nullable=True)
    specification = Column(String(200), nullable=True)

    # Supplier Info
    mill_name = Column(String(255), nullable=True)
    certificate_number = Column(String(100), nullable=True)

    extracted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="extracted_data")


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)
    standard_used = Column(String(100), nullable=True)
    overall_status = Column(String(20), default="PENDING")  # PASS, FAIL, WARNING, PENDING

    # Per-field results stored as JSON: {"field": {"value": x, "min": y, "max": z, "status": "PASS/FAIL"}}
    chemical_results = Column(JSON, nullable=True)
    mechanical_results = Column(JSON, nullable=True)

    total_checks = Column(Integer, default=0)
    passed_checks = Column(Integer, default=0)
    failed_checks = Column(Integer, default=0)
    warning_checks = Column(Integer, default=0)

    validated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="validation_result")


class MaterialStandard(Base):
    __tablename__ = "material_standards"

    id = Column(Integer, primary_key=True, index=True)
    standard_name = Column(String(100), nullable=False)    # e.g., "ASTM A106"
    grade = Column(String(50), nullable=False)             # e.g., "Grade B"

    # Chemical composition ranges (min/max percentages)
    carbon_min = Column(Float, nullable=True)
    carbon_max = Column(Float, nullable=True)
    manganese_min = Column(Float, nullable=True)
    manganese_max = Column(Float, nullable=True)
    silicon_min = Column(Float, nullable=True)
    silicon_max = Column(Float, nullable=True)
    chromium_min = Column(Float, nullable=True)
    chromium_max = Column(Float, nullable=True)
    nickel_min = Column(Float, nullable=True)
    nickel_max = Column(Float, nullable=True)
    phosphorus_min = Column(Float, nullable=True)
    phosphorus_max = Column(Float, nullable=True)
    sulfur_min = Column(Float, nullable=True)
    sulfur_max = Column(Float, nullable=True)

    # Mechanical property ranges
    yield_strength_min = Column(Float, nullable=True)      # MPa
    yield_strength_max = Column(Float, nullable=True)
    tensile_strength_min = Column(Float, nullable=True)    # MPa
    tensile_strength_max = Column(Float, nullable=True)
    elongation_min = Column(Float, nullable=True)          # %
    elongation_max = Column(Float, nullable=True)
    hardness_min = Column(Float, nullable=True)
    hardness_max = Column(Float, nullable=True)
    impact_energy_min = Column(Float, nullable=True)       # Joules
    impact_energy_max = Column(Float, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    action = Column(String(100), nullable=False)  # upload, extract, validate, view
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="audit_logs")
    document = relationship("Document", back_populates="audit_logs")
