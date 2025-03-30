#!/usr/bin/env python
"""
Utility script to generate secure encryption keys for the Invisible Art Gallery platform.

This script generates the following keys:
1. Django Secret Key
2. JWT Secret Key
3. AES Encryption Key

Usage:
    python scripts/generate_keys.py [--env-file=.env]
"""

import os
import sys
import base64
import secrets
import argparse
from pathlib import Path

def generate_django_secret_key():
    """Generate a secure random key suitable for Django's SECRET_KEY setting."""
    # Generate a 50-character key using the secrets module
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(50))

def generate_jwt_secret_key():
    """Generate a secure random key suitable for JWT signing."""
    # Generate a 32-byte key and encode as base64
    key = secrets.token_bytes(32)
    return base64.b64encode(key).decode('utf-8')

def generate_encryption_key():
    """Generate a secure random key suitable for AES encryption."""
    # Generate a 32-byte key (256 bits) and encode as base64
    key = secrets.token_bytes(32)
    return base64.b64encode(key).decode('utf-8')

def update_env_file(env_file, keys):
    """Update the .env file with the generated keys."""
    if os.path.exists(env_file):
        # Read existing file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Create a dictionary of existing key-value pairs
        env_vars = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
        
        # Update with new keys
        env_vars.update(keys)
        
        # Write back to file
        with open(env_file, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        print(f"Updated existing .env file: {env_file}")
    else:
        # Create new file
        with open(env_file, 'w') as f:
            for key, value in keys.items():
                f.write(f"{key}={value}\n")
        
        print(f"Created new .env file: {env_file}")

def display_keys(keys):
    """Display the generated keys to the console."""
    print("\nGenerated Keys:")
    print("==============")
    for key, value in keys.items():
        print(f"{key}: {value}")
    print("\nWARNING: Store these keys securely and don't share them!")

def main():
    parser = argparse.ArgumentParser(description="Generate secure keys for the Invisible Art Gallery.")
    parser.add_argument('--env-file', default='.env', help='Path to the .env file to update (default: .env)')
    args = parser.parse_args()
    
    # Generate keys
    keys = {
        'SECRET_KEY': generate_django_secret_key(),
        'JWT_SECRET_KEY': generate_jwt_secret_key(),
        'ENCRYPTION_KEY': generate_encryption_key()
    }
    
    # Display keys
    display_keys(keys)
    
    # Ask if user wants to update .env file
    env_file = args.env_file
    update = input(f"\nDo you want to update the {env_file} file with these keys? (y/n): ")
    
    if update.lower() == 'y':
        update_env_file(env_file, keys)
        print("\nKeys have been saved. Make sure to keep your .env file secure!")
    else:
        print("\nKeys were not saved to file. Make sure to save them securely elsewhere.")

if __name__ == '__main__':
    main() 