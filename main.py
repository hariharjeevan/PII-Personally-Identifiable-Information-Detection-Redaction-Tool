'''
File: main.py
Title: A Personally Identifiable Information (PII) Detection and Redaction Tool
Author: Aventra
Python Version: ^3.11
Dependency Manager: Poetry

'''
import os
import fitz
import pdfplumber
import re
import shutil
import cv2
import pytesseract
import pdf2image
import matplotlib.pyplot as plt
import re
from encryption import encrypt_pii
from encryption import attach_each_line_to_pdf
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

# Set the Tesseract executable path
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Check if Tesseract executable exists
if not os.path.exists(TESSERACT_PATH):
    raise RuntimeError(f"Tesseract executable not found at {TESSERACT_PATH}")

# Set the tesseract command path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Define PII regex patterns
AADHAAR_PATTERN = r'\b(?:\d{4}[-\s]?){2}\d{4}|\b\d{12}\b'
PAN_PATTERN = r"\b[A-Z]{5}\d{4}[A-Z]{1}\b"
EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
#DOB_PATTERN = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{2,4}[/-]\d{1,2}[/-]\d{1,2})\b'
PHONE_PATTERN = r'(?:(?:\+\d{1,3})?\s?\(?\d{1,4}?\)?[\s.-]?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,9})'


# Initialize Presidio analyzer
def create_analyzer():
    nlp_provider = NlpEngineProvider().create_engine()
    analyzer = AnalyzerEngine(nlp_engine=nlp_provider)
    return analyzer

def normalize_text(text):
    return re.sub(r'\s+', ' ', text).strip()

# Load PII counts from a text file
def load_pii_counts(pii_count_file):
    pii_counts = {}
    try:
        with open(pii_count_file, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                document = parts[0].strip()
                counts = {p.split('=')[0]: int(p.split('=')[1]) for p in parts[1:]}
                pii_counts[document] = counts
    except FileNotFoundError:
        print(f"PII count file {pii_count_file} not found.")
    except Exception as e:
        print(f"Error reading PII count file: {e}")
    return pii_counts

# Calculate accuracy and false positives based on expected and detected counts
# Calculate accuracy and false positives based on expected and detected counts
def calculate_accuracy_and_false_positives(detected_counts, expected_counts):
    # Map expected PII types to detected PII types
    pii_mapping = {
        "EMAIL": "EMAIL_ADDRESS",
        "PHONE": "PHONE_NUMBER",
        "PAN": "PAN"
        # "DOB": "DOB"
    }
    
    accuracies = {}
    false_positives = {}

    for expected_pii_type in expected_counts:
        cleaned_expected_pii_type = expected_pii_type.strip()
        detected_pii_type = pii_mapping.get(cleaned_expected_pii_type, cleaned_expected_pii_type)
        
        expected = expected_counts.get(cleaned_expected_pii_type, 0)
        detected = detected_counts.get(detected_pii_type, 0)

        # Calculate accuracy
        if expected > 0:
            if detected == 0:
                accuracies[cleaned_expected_pii_type] = 0  # 0% accuracy when expected but none detected
            else:
                accuracies[cleaned_expected_pii_type] = min(100, (detected / expected) * 100)
        else:
            accuracies[cleaned_expected_pii_type] = 0  # Assign 0% accuracy if there's no expected count

        # Calculate false positives
        false_positives[cleaned_expected_pii_type] = max(0, detected - expected)

    return accuracies, false_positives

# Plot accuracy results
def plot_accuracy_and_false_positives(accuracies, false_positives, document_name):
    # Prepare data for plotting
    labels = list(accuracies.keys())
    accuracy_values = list(accuracies.values())
    false_positive_values = list(false_positives.values())

    # Check if there are values to plot
    if not accuracy_values or not false_positive_values:
        print("No data to plot.")
        return

    x = range(len(labels))  # Positions for the bars

    plt.figure(figsize=(10, 6))
    
    # Plot accuracy
    plt.bar(x, accuracy_values, width=0.4, label='Accuracy (%)', color='skyblue', align='center')
    
    # Plot false positives
    plt.bar([p + 0.4 for p in x], false_positive_values, width=0.4, label='False Positives', color='salmon', align='center')

    max_value = max(100, max(accuracy_values + false_positive_values)) if accuracy_values or false_positive_values else 100  # Adjust y-axis limit
    plt.ylim(0, max_value + 5)
    plt.title(f"PII Detection Accuracy and False Positives for {document_name}")
    plt.ylabel("Count / Percentage")
    plt.xticks([p + 0.2 for p in x], labels)  # Center the labels
    plt.legend()
    plt.grid(axis='y')
    plt.show()

def image_conversion(inpath, image_path):
    print("Converting PDF to images")
    
    OUTPUT_FOLDER = image_path
    FIRST_PAGE = None
    LAST_PAGE = None
    FORMAT = 'jpeg'
    USERPWD = None
    USE_CROPBOX = False
    STRICT = False

    pil_images = pdf2image.convert_from_path(
        inpath,
        output_folder=OUTPUT_FOLDER,
        first_page=FIRST_PAGE,
        last_page=LAST_PAGE,
        fmt=FORMAT,
        userpw=USERPWD,
        use_cropbox=USE_CROPBOX,
        strict=STRICT
    )

    for i, image in enumerate(pil_images):
        image.save(f'{image_path}image_converted_{i + 1}.jpg', 'JPEG')

    return len(pil_images)  # Return the number of images generated

def images_to_searchable_pdf(input_image_path, output_pdf_path):
    # Read the image using OpenCV
    img = cv2.imread(input_image_path)

    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Use Tesseract to convert the RGB image to PDF
    result = pytesseract.image_to_pdf_or_hocr(img_rgb)

    with open(output_pdf_path, "wb") as f:
        f.write(bytearray(result))

def merge_pdfs(pdf_list, output_pdf_path):
    """Merge multiple PDF files into a single PDF."""
    pdf_writer = fitz.open()
    
    for pdf in pdf_list:
        pdf_reader = fitz.open(pdf)
        pdf_writer.insert_pdf(pdf_reader)
    
    pdf_writer.save(output_pdf_path)
    pdf_writer.close()

def is_pdf_searchable(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    return True
        return False
    except Exception as e:
        print(f"Error checking PDF searchability: {e}")
        return False

def make_pdf_searchable(pdf_path, searchable_pdf_path):
    image_path = os.path.dirname(searchable_pdf_path) + '/'
    num_images = image_conversion(pdf_path, image_path)
    pdf_paths = []

    for i in range(num_images):
        input_image = f"{image_path}image_converted_{i + 1}.jpg"
        output_pdf_path = f"{searchable_pdf_path}_{i + 1}.pdf"
        images_to_searchable_pdf(input_image, output_pdf_path)
        pdf_paths.append(output_pdf_path)

    # Merge all individual PDFs into one
    merged_pdf_path = f"{searchable_pdf_path}_merged.pdf"
    merge_pdfs(pdf_paths, merged_pdf_path)

    # Clean up temporary images and individual PDFs
    for img in os.listdir(image_path):
        if img.endswith('.jpg'):
            os.remove(os.path.join(image_path, img))
    for pdf in pdf_paths:
        if os.path.exists(pdf):
            os.remove(pdf)

    print(f"Merged searchable PDF saved to {os.path.normpath(merged_pdf_path)}")
    return merged_pdf_path

def is_valid_pii(detected_text, entity_type):
    password='hello'
    if entity_type == "AADHAR":
        return re.match(AADHAAR_PATTERN, detected_text) is not None
    elif entity_type == "PAN":
        return re.match(PAN_PATTERN, detected_text) is not None
    elif entity_type == "EMAIL_ADDRESS":
        return re.match(EMAIL_PATTERN, detected_text) is not None
    elif entity_type == "PHONE_NUMBER":
        return re.match(PHONE_PATTERN, detected_text) is not None
    
    print(f"Encrypting PII: {detected_text}")
    encrypt_pii(detected_text, password)
    return False  # Default case if no match is found

def redact_text_in_pdf(pdf_path, redacted_pdf_path, detected_counts):
    password = 'hello'
    output_dir = r'C:\Users\HP\Downloads\Harihar Jeevan\Sem 3\Sample\Encrypted PII'
    try:
        analyzer = create_analyzer()
        pdf_document = fitz.open(pdf_path)
        pii_found = False

        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            page_text = page.get_text()
            normalized_page_text = normalize_text(page_text)

            # Custom PII detection for AADHAR
            custom_pii_results = []
            for match in re.finditer(AADHAAR_PATTERN, normalized_page_text):
                custom_pii_results.append((match.group(), match.start(), match.end(), "AADHAR"))
            
            for match in re.finditer(PAN_PATTERN, normalized_page_text):
                custom_pii_results.append((match.group(), match.start(), match.end(), "PAN"))
                
            # Analyze for PHONE_NUMBER, EMAIL_ADDRESS, PAN, and DOB
            results = analyzer.analyze(text=normalized_page_text, entities=["PHONE_NUMBER", "EMAIL_ADDRESS", "PAN"], language='en')

            # Combine results, prioritizing AADHAR
            all_results = custom_pii_results + results

            if not all_results:
                print(f"No PII detected on page {page_num + 1}; skipping redaction.")
                continue

            for result in all_results:
                if isinstance(result, tuple):
                    detected_text, start, end, entity_type = result
                else:
                    detected_text = normalized_page_text[result.start:result.end].strip()
                    entity_type = result.entity_type

                if is_valid_pii(detected_text, entity_type):
                    detected_counts[entity_type] = detected_counts.get(entity_type, 0) + 1
                    pii_found = True
                    print(f"Redacting PII of type '{entity_type}' on page {page_num + 1}")
                    rects = page.search_for(detected_text)
                    for rect in rects:
                        page.draw_rect(rect, color=(0, 0, 0), fill=(0, 0, 0))
                        
                        # Append encrypted PII to the same file
                        encrypted_file_path = encrypt_pii(detected_text, password, output_dir)

        if pii_found:
            pdf_document.save(redacted_pdf_path)
            print(f"Redacted PDF saved to {os.path.normpath(redacted_pdf_path)}")
        else:
            print(f"No PII found in {os.path.normpath(pdf_path)}; no redacted PDF saved.")
        
        pdf_document.close()
        if encrypted_file_path:
            attach_each_line_to_pdf(redacted_pdf_path, encrypted_file_path)
    except Exception as e:
        print(f"Error redacting PDF: {e}")


def process_pdf(pdf_path, output_directory, redact_pii, pii_count_file):
    output= r'C:\Users\HP\Downloads\Harihar Jeevan\Sem 3'
    print(f"\nProcessing file {os.path.normpath(pdf_path)} with redact_pii={redact_pii}")
    
    redacted_pdf_path = os.path.join(output_directory, f"redacted_{os.path.basename(pdf_path)}")
    
    # Load expected PII counts from the text file
    expected_counts = load_pii_counts(pii_count_file).get(os.path.basename(pdf_path), {})
    
    detected_counts = {"AADHAR": 0, "PAN": 0, "EMAIL_ADDRESS": 0, "PHONE_NUMBER": 0}

    if not is_pdf_searchable(pdf_path):
        searchable_pdf_path = os.path.join(output_directory, f"searchable_{os.path.basename(pdf_path)}")
        merged_pdf_path = make_pdf_searchable(pdf_path, searchable_pdf_path)
        
        # Redact text in the newly created merged PDF
        if redact_pii:
            redact_text_in_pdf(merged_pdf_path, redacted_pdf_path, detected_counts)
        else:
            print(f"Skipping PII redaction for {os.path.normpath(merged_pdf_path)}.")
            try:
                copy_path = os.path.join(output_directory, os.path.basename(merged_pdf_path))
                shutil.copy(merged_pdf_path, copy_path)
                print(f"Copied {os.path.normpath(merged_pdf_path)} to {os.path.normpath(copy_path)}")
            except Exception as e:
                print(f"Error copying file {merged_pdf_path}: {e}")

    elif redact_pii:
        redact_text_in_pdf(pdf_path, redacted_pdf_path, detected_counts)

    # Log counts to verify
    print(f"Detected counts: {detected_counts}")
    print(f"Expected counts: {expected_counts}")

    # Calculate accuracy and false positives based on expected counts and detected counts
    accuracies, false_positives = calculate_accuracy_and_false_positives(detected_counts, expected_counts)
    
    print(f"Calculated accuracies: {accuracies}")
    print(f"False positives: {false_positives}")
    
    # Plot the accuracy and false positives
    plot_accuracy_and_false_positives(accuracies, false_positives, os.path.basename(pdf_path))
    
def process_files_in_directory(directory_path, output_directory, redact_pii, pii_count_file):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if filename.lower().endswith('.pdf'):
            process_pdf(file_path, output_directory, redact_pii, pii_count_file)

def process_directory(input_directory, output_directory, redact_pii, pii_count_file):
    process_files_in_directory(input_directory, output_directory, redact_pii, pii_count_file)
