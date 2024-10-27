
'''
File: encryption.py
Title: A Personally Identifiable Information (PII) Detection and Redaction Tool
Author: Aventra
Python Version: ^3.11
Dependency Manager: Poetry
'''

import os
from pikepdf import Pdf, AttachedFileSpec
from pathlib import Path
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import base64


def encrypt_pii(pii_data: str, password: str, output_dir: str) -> str:
    # Generate a random salt
    salt = os.urandom(16)  # Random salt for KDF
    # Derive key from password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())

    # Generate a random IV
    iv = os.urandom(16)  # Random IV for AES

    # Create a Cipher object
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Pad the data to be a multiple of the block size
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(pii_data.encode()) + padder.finalize()

    # Encrypt the padded data
    encrypted = encryptor.update(padded_data) + encryptor.finalize()

    # Encode the output for storage
    encrypted_data = base64.b64encode(salt + iv + encrypted).decode('utf-8')

    # Create a unique output file name based on the date or PDF name
    encrypted_file_path = os.path.join(output_dir, "all_encrypted_pii.txt")

    # Write encrypted data to the same file
    with open(encrypted_file_path, 'a') as encrypted_file:
        encrypted_file.write(encrypted_data + '\n')
    
    print(f"Encrypted data appended to {encrypted_file_path}")
    
    return encrypted_file_path

def encrypt_pii(pii_data: str, password: str, output_dir: str) -> str:
    # Generate a random salt
    salt = os.urandom(16)  # Random salt for KDF
    # Derive key from password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())

    # Generate a random IV
    iv = os.urandom(16)  # Random IV for AES

    # Create a Cipher object
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Pad the data
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(pii_data.encode()) + padder.finalize()

    # Encrypt the padded data
    encrypted = encryptor.update(padded_data) + encryptor.finalize()

    # Combine the salt, IV, and encrypted data for output
    encrypted_data = salt + iv + encrypted

    # Encode the output for storage
    encoded_data = base64.b64encode(encrypted_data).decode('utf-8')

    # Create a unique output file name
    encrypted_file_path = os.path.join(output_dir, "all_encrypted_pii.txt")

    # Write encrypted data to the file
    with open(encrypted_file_path, 'a') as encrypted_file:
        encrypted_file.write(encoded_data + '\n')
    
    print(f"Encrypted data appended to {encrypted_file_path}")
    
    return encrypted_file_path

def attach_each_line_to_pdf(pdf_path: str, encrypted_file_path: str):
    with Pdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        # Open the encrypted file and read line by line
        with open(encrypted_file_path, 'r') as encrypted_file:
            for index, line in enumerate(encrypted_file, start=1):
                # Naming each attachment uniquely
                attachment_name = f"encrypted_data_line_{index}.txt"
                # Create an AttachedFileSpec from the line data
                temp_file_path = Path(fr'C:\Users\HP\Downloads\Harihar Jeevan\Sem 3\Sample\temp\temp_{index}.txt')
               
                with open(temp_file_path, 'w') as temp_file:
                    temp_file.write(line)

                # Create an AttachedFileSpec from the temporary file
                filespec = AttachedFileSpec.from_filepath(pdf, temp_file_path)
                # Attach to the PDF
                pdf.attachments[attachment_name] = filespec

        pdf.save(pdf_path)
    print(f"All lines from {encrypted_file_path} attached to {pdf_path}")



