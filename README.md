# PII (Personally Identifiable Information) Detection & Redaction Tool

### Built by **Team Aventra**:
- [Harihar Jeevan](https://github.com/hariharjeevan)
- [Arya H R](https://github.com/Arya-1-HR)
- [Armaan Sameer Jena](https://github.com/jenaarmaan)
- [Parinith R](https://github.com/parinith-png)

---

## Overview

The PII Redaction Tool is a Python application designed to help users detect and redact Personally Identifiable Information (PII) from PDF documents.  
This tool supports various PII types, including AADHAAR numbers, PAN numbers, email addresses, phone numbers and is further customizable.

## Features

- **Detection of PII Types**: The tool can detect various PII types using regex patterns and natural language processing techniques.
- **Redaction of PII**: Detected PII can be redacted from the original document, ensuring sensitive information is protected.
- **Searchable PDF Creation**: Converts scanned PDFs into searchable documents using Optical Character Recognition (OCR).
- **Accuracy Reporting**: Calculates and visualizes the accuracy of detected PII against expected counts.
- **Customizable**: Easily extendable to support additional PII types or customize existing patterns.

## Requirements

- Python 3.11 or higher
- Libraries:
  - `fitz` (PyMuPDF)
  - `pdfplumber`
  - `cv2` (OpenCV)
  - `pytesseract`
  - `pdf2image`
  - `matplotlib`
  - `presidio-analyzer`

## Achievements

🏆 **First Runner-Up** at [KODiKON 4.0](https://www.embrionepes.com/kodikon-4), a 24-hour national-level hackathon sponsored by [SentinelOne®](https://www.sentinelone.com/?ad_id=644475838448&gad_campaignid=19538119170), hosted at **PES University, Bangalore** on **26th–27th October 2024**.
