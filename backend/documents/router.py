"""Document upload, processing, and results API endpoints."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from PIL import Image

from database import get_db
from models import Document, ExtractedData, ValidationResult, AuditLog, User
from schemas import (
    DocumentResponse, FullResultsResponse, ExtractedDataResponse,
    ChemicalComposition, MechanicalProperties, MaterialIdentification,
    ValidationResponse, AuditLogResponse,
)
from auth.utils import get_current_user
from documents.storage import save_uploaded_file, get_file_type
from ai_pipeline.pdf_processor import pdf_to_images, is_pdf
from ai_pipeline.preprocessor import preprocess_image
from ai_pipeline.ocr_engine import extract_text_from_image, extract_text_from_images
from ai_pipeline.extractor import extract_structured_data
from validation.engine import validate_extracted_data

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=FullResultsResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload an MTC document, process it through the AI pipeline,
    and return extraction + validation results.
    """
    # 1. Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_type = get_file_type(file.filename)
    if file_type == "unknown":
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # 2. Save file
    content = await file.read()
    try:
        unique_filename, file_path = save_uploaded_file(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3. Create document record
    doc = Document(
        user_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_type=file_type,
        file_size=len(content),
        status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 4. Log upload action
    _create_audit_log(db, current_user.id, doc.id, "upload", {
        "filename": file.filename, "size": len(content), "type": file_type
    })

    try:
        # 5. Process document through AI pipeline
        raw_text = _run_ocr_pipeline(file_path, file_type)

        # 6. Extract structured data
        structured = extract_structured_data(raw_text)

        # 7. Save extracted data
        extracted = _save_extracted_data(db, doc.id, raw_text, structured)

        # 8. Validate against standards
        validation_results = validate_extracted_data(extracted, db)

        # 9. Save validation results
        validation = _save_validation(db, doc.id, validation_results)

        # 10. Update document status
        doc.status = "completed"
        doc.processed_at = datetime.now(timezone.utc)
        db.commit()

        # 11. Log extraction and validation
        _create_audit_log(db, current_user.id, doc.id, "extract", {
            "fields_extracted": sum(1 for v in structured["chemical_composition"].values() if v is not None) +
                               sum(1 for v in structured["mechanical_properties"].values() if v is not None)
        })
        _create_audit_log(db, current_user.id, doc.id, "validate", {
            "overall_status": validation_results["overall_status"],
            "total_checks": validation_results["total_checks"],
        })

        return _build_full_response(doc, extracted, validation, validation_results)

    except Exception as e:
        doc.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/results/{document_id}", response_model=FullResultsResponse)
def get_results(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get extraction and validation results for a document."""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    extracted = db.query(ExtractedData).filter(ExtractedData.document_id == doc.id).first()
    validation = db.query(ValidationResult).filter(ValidationResult.document_id == doc.id).first()

    validation_results = None
    if validation:
        validation_results = {
            "overall_status": validation.overall_status,
            "standard_used": validation.standard_used,
            "chemical_results": validation.chemical_results,
            "mechanical_results": validation.mechanical_results,
            "total_checks": validation.total_checks,
            "passed_checks": validation.passed_checks,
            "failed_checks": validation.failed_checks,
            "warning_checks": validation.warning_checks,
        }

    # Log view action
    _create_audit_log(db, current_user.id, doc.id, "view", None)

    return _build_full_response(doc, extracted, validation, validation_results)


@router.get("/history", response_model=list[DocumentResponse])
def get_document_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the user's document upload history."""
    docs = db.query(Document).filter(
        Document.user_id == current_user.id
    ).order_by(Document.uploaded_at.desc()).all()

    return [DocumentResponse.model_validate(d) for d in docs]


@router.get("/audit/{document_id}", response_model=list[AuditLogResponse])
def get_audit_trail(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get audit trail for a specific document."""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    logs = db.query(AuditLog).filter(
        AuditLog.document_id == document_id
    ).order_by(AuditLog.timestamp.desc()).all()

    return [AuditLogResponse.model_validate(log) for log in logs]


# ─── Helper Functions ───

def _run_ocr_pipeline(file_path: str, file_type: str) -> str:
    """Run the full OCR pipeline on a document."""
    try:
        if file_type == "pdf":
            if is_pdf(file_path):
                images = pdf_to_images(file_path)
                if images:
                    processed = [preprocess_image(img) for img in images]
                    text = extract_text_from_images(processed)
                    if text and "[OCR Error" not in text:
                        return text
                    return text # Return the error message if OCR failed

            # Fallback: try to open as image
            try:
                img = Image.open(file_path)
                processed = preprocess_image(img)
                return extract_text_from_image(processed)
            except Exception as e:
                return f"[Could not process PDF as image: {str(e)}]"
        else:
            # Image file
            img = Image.open(file_path)
            processed = preprocess_image(img)
            return extract_text_from_image(processed)
    except Exception as e:
        return f"[OCR Pipeline Error: {str(e)}]"


def _save_extracted_data(db: Session, doc_id: int, raw_text: str, structured: dict) -> ExtractedData:
    """Save extracted data to database."""
    chem = structured.get("chemical_composition", {})
    mech = structured.get("mechanical_properties", {})
    
    # Symbols mapping for Step 2
    extracted = ExtractedData(
        document_id=doc_id,
        raw_text=raw_text[:20000],  # Increased limit
        carbon=chem.get("C"),
        manganese=chem.get("Mn"),
        silicon=chem.get("Si"),
        chromium=chem.get("Cr"),
        nickel=chem.get("Ni"),
        phosphorus=chem.get("P"),
        sulfur=chem.get("S"),
        yield_strength=mech.get("yield_strength"),
        tensile_strength=mech.get("tensile_strength"),
        elongation=mech.get("elongation"),
        heat_number=structured.get("heat_number"),
        batch_number=structured.get("batch_number"),
        material_grade=structured.get("material_grade"),
        specification=structured.get("specification"),
    )
    db.add(extracted)
    db.commit()
    db.refresh(extracted)
    return extracted


def _save_validation(db: Session, doc_id: int, results: dict) -> ValidationResult:
    """Save validation results to database."""
    validation = ValidationResult(
        document_id=doc_id,
        standard_used=results.get("standard_used"),
        overall_status=results.get("overall_status", "PENDING"),
        chemical_results=results.get("chemical_results"),
        mechanical_results=results.get("mechanical_results"),
        total_checks=results.get("total_checks", 0),
        passed_checks=results.get("passed_checks", 0),
        failed_checks=results.get("failed_checks", 0),
        warning_checks=results.get("warning_checks", 0),
    )
    db.add(validation)
    db.commit()
    db.refresh(validation)
    return validation


def _build_full_response(doc, extracted, validation, validation_results):
    """Build the full results response."""
    extracted_response = None
    if extracted:
        extracted_response = ExtractedDataResponse(
            chemical_composition=ChemicalComposition(
                carbon=extracted.carbon,
                manganese=extracted.manganese,
                silicon=extracted.silicon,
                chromium=extracted.chromium,
                nickel=extracted.nickel,
                phosphorus=extracted.phosphorus,
                sulfur=extracted.sulfur,
            ),
            mechanical_properties=MechanicalProperties(
                yield_strength=extracted.yield_strength,
                tensile_strength=extracted.tensile_strength,
                elongation=extracted.elongation,
                hardness=extracted.hardness,
                impact_energy=extracted.impact_energy,
            ),
            material_identification=MaterialIdentification(
                heat_number=extracted.heat_number,
                batch_number=extracted.batch_number,
                material_grade=extracted.material_grade,
                specification=extracted.specification,
                mill_name=extracted.mill_name,
                certificate_number=extracted.certificate_number,
            ),
        )

    validation_response = None
    if validation_results:
        validation_response = ValidationResponse(
            overall_status=validation_results.get("overall_status", "PENDING"),
            standard_used=validation_results.get("standard_used"),
            chemical_results=validation_results.get("chemical_results"),
            mechanical_results=validation_results.get("mechanical_results"),
            total_checks=validation_results.get("total_checks", 0),
            passed_checks=validation_results.get("passed_checks", 0),
            failed_checks=validation_results.get("failed_checks", 0),
            warning_checks=validation_results.get("warning_checks", 0),
        )

    return FullResultsResponse(
        document=DocumentResponse.model_validate(doc),
        extracted_data=extracted_response,
        validation=validation_response,
    )


def _create_audit_log(db: Session, user_id: int, doc_id: int, action: str, details: dict):
    """Create an audit log entry."""
    log = AuditLog(
        user_id=user_id,
        document_id=doc_id,
        action=action,
        details=details,
    )
    db.add(log)
    db.commit()
