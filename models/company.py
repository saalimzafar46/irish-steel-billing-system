from dataclasses import dataclass, asdict
from typing import Optional
import json

@dataclass
class Company:
    name: str = ""
    address: str = ""
    city: str = ""
    county: str = ""
    postal_code: str = ""
    country: str = "Ireland"
    phone: str = ""
    email: str = ""
    website: str = ""
    vat_number: str = ""
    company_registration: str = ""
    bank_name: str = ""
    bank_account: str = ""
    bank_sort_code: str = ""
    iban: str = ""
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    
    def save(self, filepath="data/company.json"):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath="data/company.json"):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if data:  # If file has data
                    return cls.from_dict(data)
                else:  # If file is empty
                    return cls()
        except (FileNotFoundError, json.JSONDecodeError):
            return cls()
