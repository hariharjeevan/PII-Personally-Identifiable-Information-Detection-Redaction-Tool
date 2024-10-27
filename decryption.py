
'''
File: decryption.py
Title: A Personally Identifiable Information (PII) Detection and Redaction Tool
Author: Aventra
Python Version: ^3.11
Dependency Manager: Poetry
'''

import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


def decrypt_pii(encrypted_data: str, password: str):
    # Decode the base64 encoded data
    decoded_data = base64.b64decode(encrypted_data)
    print(f"Encoded data length: {len(decoded_data)}")
    
    # Extract salt, iv, and encrypted part
    salt = decoded_data[:16]
    iv = decoded_data[16:32]
    encrypted = decoded_data[32:]
    print(f"Salt length: {len(salt)}, IV length: {len(iv)}, Encrypted length: {len(encrypted)}")
    
    # Derive the key using the same method as encryption
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())

    # Create a Cipher object for decryption
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the data
    decrypted_padded_data = decryptor.update(encrypted) + decryptor.finalize()

    # Unpad the data
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
    
    
    return decrypted_data.decode('utf-8')


def decrypt_from_file(encrypted_file_path: str, password: str) -> list:
    decrypted_lines = []
    
    with open(encrypted_file_path, 'r') as encrypted_file:
        for line in encrypted_file:
            line = line.strip()
            try:
                decrypted_data = decrypt_pii(line, password)
                decrypted_lines.append(decrypted_data)
            except Exception as e:
                print(f"Error decrypting line: {e}")

    return decrypted_lines


if __name__ == "__main__":
    pdf_path = input("Enter the path to the PDF file: ")
    password = input("Enter the decryption password: ")
    decrypted_pii = decrypt_pii(pdf_path, password)
    print("Decryption completed successfully.")
