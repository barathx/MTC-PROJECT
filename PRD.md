# AI-Based Material Test Certificate (MTC) Verification System

## 1. Overview

The AI-Based Material Test Certificate (MTC) Verification System is designed to automate the reading, extraction, interpretation, and validation of Mill Test Certificates (MTCs) provided by multiple suppliers.

MTC documents often vary in format, layout, and quality (PDFs, scanned images). Manual verification is slow and error-prone. This system uses AI-powered OCR and structured validation to automatically extract material data and compare it against international standards or user-defined specifications.

The system will:
- Extract data from MTC documents
- Interpret chemical and mechanical properties
- Validate results against material standards
- Flag compliance and non-compliance
- Maintain digital traceability

---

## 2. Objectives

Primary objectives:

1. Automate MTC document reading
2. Extract critical material properties
3. Validate extracted values against standards
4. Reduce manual verification effort
5. Provide an audit trail for traceability

---

## 3. Target Users

- Quality Control Engineers
- Procurement Engineers
- Manufacturing Engineers
- Material Inspectors
- Compliance Officers

---

## 4. Key Features

### 4.1 User Authentication
Users must log in before accessing the system.

Features:
- User registration
- Login authentication
- Role-based access

Technologies:
- JWT Authentication
- Secure password hashing

---

### 4.2 Document Upload Interface

Users can upload:

- PDF files
- Scanned images
- Photographed documents

Supported formats:

- PDF
- PNG
- JPG
- JPEG
- TIFF

The UI provides:

- Drag-and-drop upload
- Upload progress
- Document preview

---

### 4.3 AI-Based Document Processing

Uploaded documents are processed using AI.

Processing pipeline:

1. Document Upload
2. OCR Extraction
3. Text Parsing
4. Data Structuring
5. Validation

Technologies:

OCR Engines:

- PaddleOCR
- Tesseract
- Layout-aware OCR

AI Models:

- LLM for structured extraction
- NLP for table interpretation

---

### 4.4 Data Extraction

The system extracts the following fields:

### Chemical Composition

Example fields:

- Carbon (C)
- Manganese (Mn)
- Silicon (Si)
- Chromium (Cr)
- Nickel (Ni)
- Phosphorus (P)
- Sulfur (S)

---

### Mechanical Properties

Example fields:

- Yield Strength
- Tensile Strength
- Elongation
- Hardness
- Impact Energy

---

### Material Identification

- Heat Number
- Batch Number
- Material Grade
- Standard Specification

---

### Supplier Details

- Mill name
- Manufacturer
- Certificate number

---

## 5. Multi-Format Document Interpretation

The system must support:

- Structured tables
- Unstructured text
- Scanned documents
- Different layouts

AI techniques used:

- Layout detection
- Table extraction
- Named Entity Recognition (NER)

---

## 6. Material Standard Validation

The extracted data is compared against:

### International Standards

Examples include:

- ASME
- ASTM
- MIL specifications

Standards stored in database.

Validation logic:

Example:

Carbon Range: 0.18 – 0.23 %

Extracted Value: 0.20 %

Result: COMPLIANT

If outside range:

Result: NON-COMPLIANT

---

## 7. Compliance Result

Output dashboard shows:

### Compliance Status

- PASS
- FAIL
- WARNING

### Highlighted Issues

Example:

Carbon: OK  
Manganese: OK  
Silicon: OUT OF RANGE

---

## 8. Audit Trail

Every verification creates a record.

Stored data:

- Uploaded document
- Extracted data
- Validation result
- Timestamp
- User ID

This ensures:

- Traceability
- Compliance audits
- Historical analysis

---

## 9. System Architecture

### Frontend

Technology:

- Next.js
- React
- TailwindCSS

Responsibilities:

- Login UI
- Upload interface
- Result visualization
- Compliance report

---

### Backend

Technology:

- FastAPI (Python)

Responsibilities:

- API management
- AI processing
- Validation logic
- Database communication

---

### AI Processing Layer

Technologies:

- PaddleOCR
- LayoutParser
- LangChain
- LLM extraction

Functions:

- OCR
- Table detection
- Data extraction

---

### Database

Technology:

- PostgreSQL

Tables:

Users  
Documents  
ExtractedData  
ValidationResults  
Standards

---

### Storage

Document storage:

- AWS S3 or local storage

---

## 10. System Workflow

Step 1  
User logs in.

Step 2  
User uploads MTC document.

Step 3  
Document sent to backend.

Step 4  
OCR extracts text.

Step 5  
AI extracts structured fields.

Step 6  
Validation engine compares with standards.

Step 7  
Compliance result generated.

Step 8  
Results displayed on dashboard.

Step 9  
Data stored in database.

---

## 11. APIs

### Authentication API

POST /register  
POST /login

---

### Document API

POST /upload-mtc

---

### Extraction API

POST /extract-data

---

### Validation API

POST /validate

---

### Results API

GET /results/{document_id}

---

## 12. Security

Security features:

- JWT authentication
- Role-based access
- Encrypted passwords
- Secure document storage

---

## 13. Performance Goals

Document processing time:

Less than 10 seconds

Accuracy target:

Above 90% extraction accuracy

System uptime:

99.9%

---

## 14. Future Enhancements

- Supplier document scoring
- AI anomaly detection
- Automatic supplier feedback
- ERP integration
- Real-time standard updates

---

## 15. Success Metrics

Success measured by:

- Reduction in manual verification time
- Extraction accuracy
- Compliance detection accuracy
- User adoption