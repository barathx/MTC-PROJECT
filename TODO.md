# AI MTC Verification System - Development TODO

## Phase 1: Project Setup

- Create project repository
- Setup backend framework (FastAPI)
- Setup frontend (Next.js)
- Setup PostgreSQL database
- Configure environment variables

---

## Phase 2: User Authentication

Tasks:

- Create user table
- Implement user registration API
- Implement login API
- Add JWT authentication
- Connect frontend login page

---

## Phase 3: File Upload System

Tasks:

- Create upload endpoint
- Support PDF upload
- Support image upload
- Implement file storage
- Add upload UI

Frontend:

- Upload component
- Drag-and-drop UI
- File preview

---

## Phase 4: OCR Pipeline

Tasks:

- Integrate PaddleOCR
- Convert PDF pages to images
- Extract text from images
- Store raw text

Libraries:

- PaddleOCR
- pdf2image
- OpenCV

---

## Phase 5: AI Data Extraction

Tasks:

- Build extraction prompts
- Extract structured data

Fields:

Chemical Composition

- Carbon
- Manganese
- Silicon
- Chromium

Mechanical Properties

- Yield Strength
- Tensile Strength
- Hardness

Material Identification

- Heat Number
- Batch Number
- Grade

Tools:

- LangChain
- LLM API

---

## Phase 6: Table Detection

Tasks:

- Detect chemical tables
- Detect mechanical tables
- Extract numeric values

Tools:

- LayoutParser
- Camelot

---

## Phase 7: Standards Database

Tasks:

Create standards table.

Store:

- Material grade
- Element ranges
- Mechanical ranges

Example:

ASTM A106

Carbon: 0.18 - 0.23

---

## Phase 8: Validation Engine

Tasks:

- Compare extracted values
- Identify compliance
- Identify non-compliance

Output:

PASS  
FAIL  
WARNING

---

## Phase 9: Result Dashboard

Frontend tasks:

- Display extracted data
- Show validation status
- Highlight failures
- Show material tables

---

## Phase 10: Audit Trail

Tasks:

- Store verification history
- Track uploaded documents
- Store timestamps

---

## Phase 11: Performance Optimization

Tasks:

- Cache OCR results
- Optimize API responses
- Improve AI prompt efficiency

---

## Phase 12: Testing

Testing types:

- OCR accuracy testing
- Extraction accuracy
- API testing
- UI testing

Tools:

- Pytest
- Postman
- Playwright

---

## Phase 13: Deployment

Deployment stack:

Backend

- Docker
- FastAPI
- Nginx

Frontend

- Vercel

Database

- PostgreSQL

Storage

- AWS S3

---

## Phase 14: Monitoring

Add monitoring tools:

- Prometheus
- Grafana
- Logging system

---

## Phase 15: Documentation

Create:

- API documentation
- System architecture diagrams
- User manual