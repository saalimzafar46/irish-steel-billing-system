from typing import Any, Optional
import locale
from decimal import Decimal, ROUND_HALF_UP

class Formatters:
    @staticmethod
    def format_currency(amount: float, currency: str = "EUR") -> str:
        """Format currency amount"""
        try:
            if currency == "EUR":
                return f"€{amount:,.2f}"
            else:
                return f"{amount:,.2f} {currency}"
        except:
            return f"€0.00"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Format percentage"""
        return f"{value:.1f}%"
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Format Irish phone number for display"""
        if not phone:
            return ""
        
        # Remove all non-digit characters except +
        clean = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Format based on length and pattern
        if clean.startswith('+353'):
            # International format
            number = clean[4:]
            if len(number) == 9:
                return f"+353 {number[0]} {number[1:4]} {number[4:8]}"
            elif len(number) == 8:
                return f"+353 {number[0:2]} {number[2:5]} {number[5:8]}"
        elif clean.startswith('0'):
            # National format
            if len(clean) == 10:
                return f"{clean[0:3]} {clean[3:6]} {clean[6:10]}"
            elif len(clean) == 9:
                return f"{clean[0:2]} {clean[2:5]} {clean[5:9]}"
        
        return phone  # Return as-is if no pattern matches
    
    @staticmethod
    def format_vat_number(vat: str) -> str:
        """Format VAT number for display"""
        if not vat:
            return ""
        
        clean = vat.upper().replace(' ', '')
        if clean.startswith('IE') and len(clean) >= 9:
            return f"IE {clean[2:9]} {clean[9:]}"
        
        return vat
    
    @staticmethod
    def format_iban(iban: str) -> str:
        """Format IBAN for display"""
        if not iban:
            return ""
        
        clean = iban.replace(' ', '').upper()
        # Add spaces every 4 characters
        formatted = ' '.join([clean[i:i+4] for i in range(0, len(clean), 4)])
        return formatted
    
    @staticmethod
    def parse_currency(currency_str: str) -> float:
        """Parse currency string to float"""
        if not currency_str:
            return 0.0
        
        # Remove currency symbols and whitespace
        clean = currency_str.replace('€', '').replace(',', '').strip()
        
        try:
            return float(clean)
        except ValueError:
            return 0.0
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 50) -> str:
        """Truncate text with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @staticmethod
    def format_date(date_str: str) -> str:
        """Format date for display"""
        try:
            from datetime import datetime
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime("%d/%m/%Y")
        except:
            return date_str
    
    @staticmethod
    def format_dimensions(dimensions: str) -> str:
        """Format steel dimensions for display"""
        if not dimensions:
            return ""
        
        # Common formatting for steel dimensions
        # e.g., "20x20x6000" -> "20mm × 20mm × 6000mm"
        if 'x' in dimensions.lower():
            parts = dimensions.lower().split('x')
            formatted_parts = []
            for part in parts:
                part = part.strip()
                if not part.endswith('mm'):
                    part += 'mm'
                formatted_parts.append(part)
            return ' × '.join(formatted_parts)
        
        return dimensions
