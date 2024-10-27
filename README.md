# PII (Personally Identifiable Information) Detection & Redaction Tool

## Overview

### The PII Redaction Tool is a Python application designed to help users detect and redact Personally Identifiable Information (PII) from PDF documents. 
### This tool supports various PII types, including AADHAAR numbers, PAN numbers, email addresses, phone numbers and is further customizable.

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


