# Zenvora

**All Your PDF Tools. One Powerful Platform.**

Zenvora is a web-based document utility platform designed to make working with PDF and office documents easier. It provides a collection of tools for converting, compressing, repairing, and managing documents through a simple, user-friendly interface.

## Features

### PDF Tools
- **Compress PDF** – Reduce PDF file size.
- **Repair PDF** – Attempt to repair damaged PDF files.
- **PDF to Images** – Convert PDF pages into image files.
- **PDF to Word** – Convert PDF documents into editable Word files.
- **PDF to Excel** – Extract tabular data from PDF documents into Excel spreadsheets.
- **OCR** – Extract text from scanned documents.
- **PDF to PowerPoint** – Convert PDF documents into PowerPoint presentations.

### Document Conversion
- **Word to PDF** – Convert Word documents into PDF.
- **PowerPoint to PDF** – Convert presentations into PDF.
- **Excel to PDF** – Convert spreadsheets into PDF.
- **HTML to PDF** – Convert HTML content into PDF.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| PDF Processing | PyMuPDF, pdf2docx, pdfplumber |
| Excel Processing | openpyxl |
| Office Conversion | LibreOffice |
| Deployment | Render |
| Containerization | Docker |

## Project Structure

```text
Zenvora/
│
├── static/
│   └── index.html
│
├── main.py
├── requirements.txt
├── Dockerfile
├── render.yaml
└── README.md
```

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/deeveshnemade2007/Zenvora.git
cd Zenvora
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the application

```bash
uvicorn main:app --reload
```

Open your browser:

```text
http://127.0.0.1:8000
```

**Note:** Office-to-PDF conversion requires LibreOffice. The Docker deployment includes LibreOffice and its required system dependencies.

## Deployment

Zenvora is deployed on **Render** using Docker.

- Runtime: Docker
- Backend server: Uvicorn
- Framework: FastAPI
- Health check: `/api/health`

## Important Notes

- Conversion results may vary depending on document formatting, fonts, and compatibility between Microsoft Office and LibreOffice.
- Complex layouts, tables, images, page breaks, and custom fonts may not be reproduced identically during Office-to-PDF conversion.
- Conversion accuracy is an ongoing improvement area.
- Some tools may require additional dependencies or implementation before becoming available.

## Future Improvements

- Improve formatting preservation during Word, PowerPoint, and Excel conversions.
- Improve OCR accuracy.
- Enhance PDF compression and repair.
- Add batch document processing.
- Improve conversion speed and reliability.
- Introduce additional document management tools.

## Developer

**Deevesh Nemade**

Electronics and Computer Engineering Student

---

*Zenvora – Simplifying Documents, One Tool at a Time.*