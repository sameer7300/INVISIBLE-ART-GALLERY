import base64
import os
import hashlib
import logging

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from django.conf import settings

logger = logging.getLogger(__name__)

class EncryptionService:
    """Service for encrypting and decrypting artwork content."""
    
    def __init__(self):
        """Initialize the encryption service."""
        self.backend = default_backend()
    
    def _derive_key_iv(self, key):
        """
        Derive a key and IV from the master key.
        
        Uses a key derivation function to derive a key and IV from the master key.
        For simplicity, we're using a basic approach here, but in production
        a proper KDF like PBKDF2 should be used.
        """
        # Use a hash of the key for simplicity
        # In production, use a proper KDF
        
        # Convert string key to bytes if necessary
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        # Ensure we have a key to derive from
        if not key:
            print("No encryption key provided")
            key = os.urandom(32)  # Generate random key if none is provided
        
        print(f"Deriving key from input of length: {len(key)} bytes")
        
        try:
            # Derive key material
            digest = hashlib.sha256(key).digest()
            
            # Split into key and IV
            # AES key size: 256 bits (32 bytes)
            # IV size: 128 bits (16 bytes) for CBC mode
            derived_key = digest[:32]  # First 32 bytes for the key
            
            # Generate a new random IV for each encryption
            # This is more secure than deriving it from the key
            iv = os.urandom(16)  # Always use a fresh 16-byte IV
            
            print(f"Generated derived key length: {len(derived_key)}, IV length: {len(iv)}")
            
            return derived_key, iv
        except Exception as e:
            print(f"Key derivation error: {str(e)}")
            raise
    
    def encrypt(self, data, key=None):
        """
        Encrypt data using AES-256-CBC.
        
        Args:
            data: The binary data to encrypt
            key: The encryption key (defaults to settings.ENCRYPTION_KEY)
            
        Returns:
            bytes: The encrypted data
        """
        if key is None:
            key = settings.ENCRYPTION_KEY
        
        # Convert bytes-like objects to bytes if needed
        if hasattr(data, 'read'):
            # Handle file-like objects
            try:
                data = data.read()
            except Exception as e:
                print(f"Error reading data from file-like object: {e}")
                raise ValueError(f"Failed to read data: {str(e)}")
        
        # Ensure data is bytes
        if not isinstance(data, bytes):
            try:
                data = bytes(data)
            except Exception as e:
                print(f"Error converting data to bytes: {e}")
                raise ValueError(f"Data must be convertible to bytes: {str(e)}")
        
        # Ensure we have data to encrypt
        if not data:
            print("No data to encrypt, received empty data")
            raise ValueError("Cannot encrypt empty data")
        
        print(f"Encrypting data of length: {len(data)} bytes")
        
        try:
            # Derive key and IV
            derived_key, iv = self._derive_key_iv(key)
            
            # Debug
            print(f"Derived key length: {len(derived_key)}, IV length: {len(iv)}")
            
            # Create a padder
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(data) + padder.finalize()
            
            # Create the cipher
            cipher = Cipher(
                algorithms.AES(derived_key),
                modes.CBC(iv),
                backend=self.backend
            )
            
            # Encrypt the data
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # Prepend IV to the ciphertext for decryption
            result = iv + encrypted_data
            print(f"Encryption successful, result length: {len(result)} bytes")
            return result
            
        except Exception as e:
            print(f"Encryption error: {str(e)}")
            raise
    
    def decrypt(self, data, key=None):
        """
        Decrypt data using AES-256-CBC.
        
        Args:
            data: The encrypted data (with IV prepended)
            key: The encryption key (defaults to settings.ENCRYPTION_KEY)
            
        Returns:
            bytes: The decrypted data
        """
        if key is None:
            key = settings.ENCRYPTION_KEY
        
        # Validate data
        if not data or len(data) < 16:
            print(f"Invalid data length for decryption: {len(data) if data else 0}")
            raise ValueError("Data is too short to contain an IV")
        
        try:
            # Extract IV from the beginning of the data
            iv = data[:16]
            ciphertext = data[16:]
            
            print(f"Decrypting data - IV length: {len(iv)}, ciphertext length: {len(ciphertext)}")
            
            # Derive key
            derived_key, _ = self._derive_key_iv(key)
            
            # Create the cipher
            cipher = Cipher(
                algorithms.AES(derived_key),
                modes.CBC(iv),
                backend=self.backend
            )
            
            # Decrypt the data
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remove padding
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            original_data = unpadder.update(padded_data) + unpadder.finalize()
            
            print(f"Decryption successful, result length: {len(original_data)} bytes")
            return original_data
            
        except Exception as e:
            print(f"Decryption error: {str(e)}")
            raise
    
    def generate_key(self):
        """
        Generate a new random encryption key.
        
        Returns:
            str: A base64-encoded random key suitable for encryption
        """
        # Generate a random 256-bit key
        key = os.urandom(32)
        # Return as base64 for storage
        return base64.b64encode(key).decode('utf-8') 