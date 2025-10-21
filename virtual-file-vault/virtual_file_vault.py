# Virtual File Vault - Password-Protected File Encryption and Decryption System
#
# Usage Instructions:
# 1. Run this Python script: python virtual_file_vault.py
# 2. Click "Select File" to choose a file to encrypt or a .locked file to decrypt.
# 3. Enter a password in the password field (it will be masked).
# 4. Click "Encrypt" to lock the file or "Decrypt" to unlock it.
# 5. Check the status label for feedback.
#
# Note: Encrypted files are saved as filename.locked. Original files are deleted after encryption.
# Use the same password for decryption.

import os
import sys
import subprocess
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import tkinter as tk
from tkinter import filedialog, messagebox

# Auto-check and install missing libraries
def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError:
        messagebox.showerror("Installation Error", f"Failed to install {package}. Please install it manually.")

try:
    import cryptography
except ImportError:
    install_package("cryptography")

# Function to derive encryption key from password
def derive_key(password, salt=b'static_salt_for_demo'):  # In production, use random salt per file
    password = password.encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

# Function to encrypt a file
def encrypt_file(file_path, password):
    if file_path.endswith('.locked'):
        return "File is already encrypted."
    
    key = derive_key(password)
    fernet = Fernet(key)
    
    with open(file_path, 'rb') as file:
        original = file.read()
    
    encrypted = fernet.encrypt(original)
    
    locked_path = file_path + '.locked'
    with open(locked_path, 'wb') as file:
        file.write(encrypted)
    
    # Optionally delete original file
    os.remove(file_path)
    
    return f"File encrypted successfully as {locked_path}"

# Function to decrypt a file
def decrypt_file(file_path, password):
    if not file_path.endswith('.locked'):
        return "File is not encrypted (does not end with .locked)."
    
    key = derive_key(password)
    fernet = Fernet(key)
    
    with open(file_path, 'rb') as file:
        encrypted = file.read()
    
    try:
        decrypted = fernet.decrypt(encrypted)
    except InvalidToken:
        return "Wrong password. Decryption failed."
    
    original_path = file_path[:-7]  # Remove .locked extension
    with open(original_path, 'wb') as file:
        file.write(decrypted)
    
    os.remove(file_path)
    
    return f"File decrypted successfully as {original_path}"

# GUI Class
class VirtualFileVault:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual File Vault")
        self.root.geometry("400x300")
        
        self.file_path = None
        
        # Select File Button
        self.select_button = tk.Button(root, text="Select File", command=self.select_file)
        self.select_button.pack(pady=10)
        
        # Password Entry (masked)
        self.password_label = tk.Label(root, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)
        
        # Encrypt Button
        self.encrypt_button = tk.Button(root, text="Encrypt", command=self.encrypt)
        self.encrypt_button.pack(pady=5)
        
        # Decrypt Button
        self.decrypt_button = tk.Button(root, text="Decrypt", command=self.decrypt)
        self.decrypt_button.pack(pady=5)
        
        # Status Label
        self.status_label = tk.Label(root, text="")
        self.status_label.pack(pady=10)
    
    def select_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.status_label.config(text=f"Selected: {os.path.basename(self.file_path)}")
        else:
            self.status_label.config(text="No file selected.")
    
    def encrypt(self):
        if not self.file_path:
            self.status_label.config(text="Please select a file first.")
            return
        password = self.password_entry.get()
        if not password:
            self.status_label.config(text="Please enter a password.")
            return
        result = encrypt_file(self.file_path, password)
        self.status_label.config(text=result)
        self.file_path = None  # Reset after operation
    
    def decrypt(self):
        if not self.file_path:
            self.status_label.config(text="Please select a file first.")
            return
        password = self.password_entry.get()
        if not password:
            self.status_label.config(text="Please enter a password.")
            return
        result = decrypt_file(self.file_path, password)
        self.status_label.config(text=result)
        self.file_path = None  # Reset after operation

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualFileVault(root)
    root.mainloop()
