import re
from typing import Optional, Tuple

class Validators:
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validate email format"""
        if not email:
            return True, None  # Empty email is okay
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, None
        return False, "Invalid email format"
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """Validate Irish phone number"""
        if not phone:
            return True, None  # Empty phone is okay
        
        # Remove spaces and common separators
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Irish phone patterns
        patterns = [
            r'^(\+353|0353|353)?[0-9]{8,9}$',  # Standard Irish format
            r'^(\+353|0353|353)?[1-9][0-9]{7,8}$',  # More specific
        ]
        
        for pattern in patterns:
            if re.match(pattern, clean_phone):
                return True, None
        
        return False, "Invalid Irish phone number format"
    
    @staticmethod
    def validate_vat_number(vat: str) -> Tuple[bool, Optional[str]]:
        """Validate Irish VAT number"""
        if not vat:
            return True, None  # Empty VAT is okay
        
        # Irish VAT format: IE + 7 digits + 1 or 2 letters
        # or IE + 1 digit + letter + 5 digits + letter
        pattern = r'^IE[0-9]{7}[A-Z]{1,2}$|^IE[0-9][A-Z][0-9]{5}[A-Z]$'
        
        if re.match(pattern, vat.upper()):
            return True, None
        return False, "Invalid Irish VAT number format (e.g., IE1234567T)"
    
    @staticmethod
    def validate_iban(iban: str) -> Tuple[bool, Optional[str]]:
        """Validate IBAN format"""
        if not iban:
            return True, None
        
        # Remove spaces
        clean_iban = iban.replace(' ', '')
        
        # Irish IBAN: IE + 2 check digits + 4 bank code + 6 account number + 8 digits
        if clean_iban.startswith('IE') and len(clean_iban) == 22:
            if re.match(r'^IE[0-9]{20}$', clean_iban):
                return True, None
        
        return False, "Invalid Irish IBAN format"
    
    @staticmethod
    def validate_positive_number(value: str) -> Tuple[bool, Optional[str]]:
        """Validate positive number"""
        try:
            num = float(value)
            if num >= 0:
                return True, None
            return False, "Value must be positive"
        except ValueError:
            return False, "Invalid number format"
    
    @staticmethod
    def validate_required_field(value: str, field_name: str) -> Tuple[bool, Optional[str]]:
        """Validate required field"""
        if not value or not value.strip():
            return False, f"{field_name} is required"
        return True, None
    
    @staticmethod
    def validate_postal_code(postal_code: str) -> Tuple[bool, Optional[str]]:
        """Validate Irish postal code (Eircode)"""
        if not postal_code:
            return True, None
        
        # Eircode format: 7 characters (3 digits + 4 alphanumeric)
        pattern = r'^[A-Z0-9]{3}\s?[A-Z0-9]{4}$'
        
        if re.match(pattern, postal_code.upper()):
            return True, None
        return False, "Invalid Eircode format (e.g., D02 XY45)"
