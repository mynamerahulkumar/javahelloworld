"""
Client authentication module for validating client credentials
"""
import csv
import os
from pathlib import Path
from typing import Dict, Tuple, Optional

# Path to client credentials CSV file
# Go up 4 levels from backend/src/auth/client_auth.py to reach project root
CSV_FILE_PATH = Path(__file__).parent.parent.parent.parent / "privatedata" / "srp_client_trading.csv"


class ClientAuth:
    """Client authentication handler"""
    
    def __init__(self, csv_path: Optional[Path] = None):
        """
        Initialize client authentication
        
        Args:
            csv_path: Optional path to CSV file. Defaults to privatedata/srp_client_trading.csv
        """
        self.csv_path = csv_path or CSV_FILE_PATH
        self.clients: Dict[str, Dict[str, str]] = {}
        self._load_clients()
    
    def _load_clients(self):
        """Load client credentials from CSV file"""
        if not self.csv_path.exists():
            return
        
        # Try multiple encodings to handle different CSV formats
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(self.csv_path, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        email = row.get('srp_client_emailid', '').strip()
                        client_id = row.get('srp_client_id', '').strip()
                        password = row.get('srp_client_password', '').strip()
                        
                        # Skip empty rows
                        if not email or not client_id:
                            continue
                        
                        # Store client by email (primary key)
                        self.clients[email] = {
                            'client_id': client_id,
                            'email': email,
                            'password': password
                        }
                break  # Successfully loaded, exit loop
            except UnicodeDecodeError:
                continue
            except Exception as e:
                # If all encodings fail, log and continue
                print(f"Error loading clients CSV: {e}")
                break
    
    def validate_client(self, client_id: str, email: str, password: Optional[str] = None) -> Tuple[bool, str]:
        """
        Validate client credentials
        
        Args:
            client_id: Client ID to validate
            email: Client email to validate
            password: Client password to validate (optional)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not client_id or not email:
            return False, "Client ID and email are required"
        
        email = email.strip().lower()
        client_id = client_id.strip()
        
        # Check if email exists in clients
        if email not in self.clients:
            return False, "Invalid or unauthorized client email"
        
        # Check if client_id matches
        stored_client_id = self.clients[email].get('client_id', '').strip()
        if stored_client_id != client_id:
            return False, "Invalid or unauthorized client ID"
        
        # If password is provided, validate it
        if password is not None:
            stored_password = self.clients[email].get('password', '').strip()
            if stored_password != password.strip():
                return False, "Invalid password"
        
        return True, "Valid client"
    
    def reload_clients(self):
        """Reload client credentials from CSV file"""
        self.clients.clear()
        self._load_clients()


# Create singleton instance
client_auth = ClientAuth()

