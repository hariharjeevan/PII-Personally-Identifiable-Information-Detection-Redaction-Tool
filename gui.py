'''
File: gui.py
Title: A Personally Identifiable Information (PII) Detection and Redaction Tool
Author: Aventra
Python Version: ^3.11
Dependency Manager: Poetry
'''

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from decryption import decrypt_pii
from main import process_pdf
from pikepdf import Pdf

class PII_Redaction_Tool:
    def __init__(self, master):
        self.master = master
        master.title("PII Redaction Tool")
        master.geometry("650x700")
        master.config(bg="#001219")

        # Title Label
        self.title_label = tk.Label(master, text="PII Redaction Tool", font=("Helvetica", 24, "bold"), fg="#FFD700", bg="#2E2E2E")
        self.title_label.pack(pady=30)

        # Input Directory Section
        self.input_frame = tk.Frame(master, bg="#3E3E3E", bd=2, relief="groove")
        self.input_frame.pack(pady=10, padx=20, fill="x")

        self.input_label = tk.Label(self.input_frame, text="Select Input Directory:", fg="#FFFFFF", bg="#3E3E3E", font=("Helvetica", 12))
        self.input_label.pack(pady=5)
        self.input_button = tk.Button(self.input_frame, text="Browse", command=self.browse_input_directory, bg="#FFD700", fg="#2E2E2E", relief="flat", font=("Helvetica", 10))
        self.input_button.pack(pady=5)

        # Output Directory Section
        self.output_frame = tk.Frame(master, bg="#3E3E3E", bd=2, relief="groove")
        self.output_frame.pack(pady=10, padx=20, fill="x")

        self.output_label = tk.Label(self.output_frame, text="Select Output Directory:", fg="#FFFFFF", bg="#3E3E3E", font=("Helvetica", 12))
        self.output_label.pack(pady=5)
        self.output_button = tk.Button(self.output_frame, text="Browse", command=self.browse_output_directory, bg="#FFD700", fg="#2E2E2E", relief="flat", font=("Helvetica", 10))
        self.output_button.pack(pady=5)

        # Redaction Checkbox
        self.redact_var = tk.BooleanVar(value=False)
        self.redact_checkbox = tk.Checkbutton(master, text="Redact PII", variable=self.redact_var, onvalue=True, offvalue=False, bg="#001219", fg="#FFFFFF", selectcolor="#000000", font=("Helvetica", 12))
        self.redact_checkbox.pack(pady=10)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(master, length=400, mode='determinate')
        self.progress_bar.pack(pady=20)

        # Process Button
        self.process_button = tk.Button(master, text="Process Files", command=self.process_files, bg="#FFD700", fg="#2E2E2E", relief="flat", font=("Helvetica", 14, "bold"))
        self.process_button.pack(pady=20)

        # Menu Bar for Decryption
        self.menu_bar = tk.Menu(master)
        master.config(menu=self.menu_bar)

        # Decrypt Menu
        self.decrypt_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Decrypt", menu=self.decrypt_menu)
        self.decrypt_menu.add_command(label="Decrypt PII", command=self.open_decrypt_dialog)

        self.input_directory = None
        self.output_directory = None
        self.selected_pdf = None

    def browse_input_directory(self):
        self.input_directory = filedialog.askdirectory()
        if self.input_directory:
            self.input_label.config(text=f"Input Directory: {self.input_directory}")

    def browse_output_directory(self):
        self.output_directory = filedialog.askdirectory()
        if self.output_directory:
            self.output_label.config(text=f"Output Directory: {self.output_directory}")

    def process_files(self):
        if not self.input_directory or not self.output_directory:
            messagebox.showwarning("Warning", "Please select both input and output directories.")
            return

        redact_pii = self.redact_var.get()
        
        if not redact_pii:
            messagebox.showwarning("Redaction Required", "You must check 'Redact PII' to proceed with file processing.")
            return

        try:
            pdf_files = [f for f in os.listdir(self.input_directory) if f.lower().endswith('.pdf')]
            total_files = len(pdf_files)
            self.progress_bar['maximum'] = total_files

            pii_count_file = r'C:\Users\HP\Downloads\Harihar Jeevan\Sem 3\Sample\PII Count.txt'  # Ensure this path is correct

            for idx, pdf_file in enumerate(pdf_files):
                file_path = os.path.join(self.input_directory, pdf_file)

                if not os.path.exists(file_path):
                    messagebox.showwarning("File Error", f"The file '{pdf_file}' does not exist.")
                    continue

                try:
                    process_pdf(file_path, self.output_directory, redact_pii, pii_count_file)
                except Exception as e:
                    messagebox.showerror("Processing Error", f"An error occurred while processing '{pdf_file}': {e}")
                    continue

                self.progress_bar['value'] = idx + 1
                self.master.update()

            messagebox.showinfo("Success", "Processing completed successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.progress_bar['value'] = 0
            self.master.update()

    def open_decrypt_dialog(self):
        decrypt_window = tk.Toplevel(self.master)
        decrypt_window.title("Decrypt PII")
        
        pdf_file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if pdf_file_path:
            password = simpledialog.askstring("Password", "Enter the decryption password:", show='*')
            if password:
                self.decrypt_pii_files(pdf_file_path, password)

    def decrypt_pii_files(self, pdf_file_path, password):
        try:
            decrypted_pii = decrypt_pii(pdf_file_path, password)
            messagebox.showinfo("Success", "Decryption completed successfully!")
            # Optionally, display the decrypted PII or save it as needed
        except Exception as e:
            messagebox.showerror("Decryption Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PII_Redaction_Tool(root)
    root.mainloop()

