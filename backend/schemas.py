from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime


# ─── Auth Schemas ───

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─── Document Schemas ───

class DocumentResponse(BaseModel):
    id: int
    original_filename: str
    file_type: str
    status: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Extraction Schemas ───

class ChemicalComposition(BaseModel):
    carbon: Optional[float] = None
    manganese: Optional[float] = None
    silicon: Optional[float] = None
    chromium: Optional[float] = None
    nickel: Optional[float] = None
    phosphorus: Optional[float] = None
    sulfur: Optional[float] = None


class MechanicalProperties(BaseModel):
    yield_strength: Optional[float] = None
    tensile_strength: Optional[float] = None
    elongation: Optional[float] = None
    hardness: Optional[float] = None
    impact_energy: Optional[float] = None


class MaterialIdentification(BaseModel):
    heat_number: Optional[str] = None
    batch_number: Optional[str] = None
    material_grade: Optional[str] = None
    specification: Optional[str] = None
    mill_name: Optional[str] = None
    certificate_number: Optional[str] = None


class ExtractedDataResponse(BaseModel):
    chemical_composition: ChemicalComposition
    mechanical_properties: MechanicalProperties
    material_identification: MaterialIdentification

    class Config:
        from_attributes = True


# ─── Validation Schemas ───

class FieldValidation(BaseModel):
    value: Optional[float] = None
    min_limit: Optional[float] = None
    max_limit: Optional[float] = None
    status: str  # PASS, FAIL, WARNING, N/A
    unit: Optional[str] = None


class ValidationResponse(BaseModel):
    overall_status: str
    standard_used: Optional[str] = None
    chemical_results: Optional[Dict[str, Any]] = None
    mechanical_results: Optional[Dict[str, Any]] = None
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int


# ─── Full Results ───

class FullResultsResponse(BaseModel):
    document: DocumentResponse
    extracted_data: Optional[ExtractedDataResponse] = None
    validation: Optional[ValidationResponse] = None


# ─── Audit Schema ───

class AuditLogResponse(BaseModel):
    id: int
    action: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True
