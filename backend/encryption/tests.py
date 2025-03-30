from django.test import TestCase
from django.conf import settings

from .services import EncryptionService


class EncryptionServiceTests(TestCase):
    """Tests for the EncryptionService."""
    
    def setUp(self):
        """Set up the encryption service for testing."""
        self.encryption_service = EncryptionService()
        self.test_data = b'This is some test data to encrypt and decrypt.'
        self.test_key = 'test-encryption-key-for-testing-purposes-only'
    
    def test_encrypt_decrypt_cycle(self):
        """Test that data can be encrypted and then successfully decrypted."""
        # Encrypt the data
        encrypted_data = self.encryption_service.encrypt(self.test_data, self.test_key)
        
        # Check that the encrypted data is different from the original
        self.assertNotEqual(encrypted_data, self.test_data)
        
        # Decrypt the data
        decrypted_data = self.encryption_service.decrypt(encrypted_data, self.test_key)
        
        # Check that the decrypted data matches the original
        self.assertEqual(decrypted_data, self.test_data)
    
    def test_key_derivation(self):
        """Test that the same key consistently produces the same derived key and IV."""
        key1, iv1 = self.encryption_service._derive_key_iv(self.test_key)
        key2, iv2 = self.encryption_service._derive_key_iv(self.test_key)
        
        # Check that the derived keys and IVs are the same
        self.assertEqual(key1, key2)
        self.assertEqual(iv1, iv2)
        
        # Check that different keys produce different derived keys and IVs
        key3, iv3 = self.encryption_service._derive_key_iv('different-key')
        self.assertNotEqual(key1, key3)
        self.assertNotEqual(iv1, iv3)
    
    def test_generate_key(self):
        """Test that the key generation creates valid keys."""
        key = self.encryption_service.generate_key()
        
        # Check that the key is a string and not empty
        self.assertIsInstance(key, str)
        self.assertTrue(len(key) > 0)
        
        # Test that the generated key can be used for encryption and decryption
        encrypted_data = self.encryption_service.encrypt(self.test_data, key)
        decrypted_data = self.encryption_service.decrypt(encrypted_data, key)
        self.assertEqual(decrypted_data, self.test_data)
    
    def test_default_key_from_settings(self):
        """Test that the default key from settings works for encryption and decryption."""
        encrypted_data = self.encryption_service.encrypt(self.test_data)
        decrypted_data = self.encryption_service.decrypt(encrypted_data)
        self.assertEqual(decrypted_data, self.test_data) 