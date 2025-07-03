from dataclasses import dataclass, asdict, field
from typing import List, Optional
import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

@dataclass
class InvoiceItem:
    product_id: str
    product_name: str
    description: str
    quantity: float
    unit_price: float
    cuts_required: int = 0
    cutting_charge_per_cut: float = 0.0
    discount_percentage: float = 0.0
    discount_amount: float = 0.0
    
    @property
    def line_total_before_discount(self) -> float:
        base_total = self.quantity * self.unit_price
        cutting_total = self.cuts_required * self.cutting_charge_per_cut
        return base_total + cutting_total
    
    @property
    def total_discount(self) -> float:
        percentage_discount = self.line_total_before_discount * (self.discount_percentage / 100)
        return percentage_discount + self.discount_amount
    
    @property
    def line_total(self) -> float:
        return self.line_total_before_discount - self.total_discount

@dataclass
class Invoice:
    id: str = ""
    invoice_number: str = ""
    client_id: str = ""
    client_name: str = ""
    issue_date: str = ""
    due_date: str = ""
    status: str = "Draft"  # Draft, Sent, Paid, Overdue, Cancelled
    items: List[InvoiceItem] = field(default_factory=list)
    
    # Additional charges
    shipping_cost: float = 0.0
    handling_cost: float = 0.0
    other_charges: float = 0.0
    other_charges_description: str = ""
    
    # Discounts
    global_discount_percentage: float = 0.0
    global_discount_amount: float = 0.0
    
    # Tax settings
    vat_rate: float = 23.0  # Irish VAT rate
    vat_number: str = ""
    
    # Payment details
    payment_terms: str = "30 days"
    notes: str = ""
    
    # Metadata
    created_date: str = ""
    last_modified: str = ""
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.issue_date:
            self.issue_date = datetime.now().strftime("%Y-%m-%d")
        if not self.due_date:
            due = datetime.now() + timedelta(days=30)
            self.due_date = due.strftime("%Y-%m-%d")
        self.last_modified = datetime.now().isoformat()
    
    @property
    def subtotal(self) -> float:
        """Sum of all line items before global discounts and VAT"""
        return sum(item.line_total for item in self.items)
    
    @property
    def additional_charges_total(self) -> float:
        """Sum of shipping, handling, and other charges"""
        return self.shipping_cost + self.handling_cost + self.other_charges
    
    @property
    def total_before_global_discount(self) -> float:
        """Subtotal plus additional charges, before global discount"""
        return self.subtotal + self.additional_charges_total
    
    @property
    def global_discount_total(self) -> float:
        """Total global discount amount"""
        percentage_discount = self.total_before_global_discount * (self.global_discount_percentage / 100)
        return percentage_discount + self.global_discount_amount
    
    @property
    def total_before_vat(self) -> float:
        """Total after global discounts but before VAT"""
        return self.total_before_global_discount - self.global_discount_total
    
    @property
    def vat_amount(self) -> float:
        """VAT amount calculated on total before VAT"""
        return self.total_before_vat * (self.vat_rate / 100)
    
    @property
    def total_amount(self) -> float:
        """Final total including VAT"""
        return self.total_before_vat + self.vat_amount
    
    def add_item(self, item: InvoiceItem):
        self.items.append(item)
        self.last_modified = datetime.now().isoformat()
    
    def remove_item(self, index: int):
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self.last_modified = datetime.now().isoformat()
    
    def to_dict(self):
        data = asdict(self)
        return data
    
    @classmethod
    def from_dict(cls, data):
        # Convert items to InvoiceItem objects
        items_data = data.pop('items', [])
        invoice = cls(**data)
        invoice.items = [InvoiceItem(**item_data) for item_data in items_data]
        return invoice

class InvoiceManager:
    def __init__(self, filepath="data/invoices.json"):
        self.filepath = filepath
        self.invoices = self.load_invoices()
    
    def load_invoices(self) -> List[Invoice]:
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                return [Invoice.from_dict(invoice_data) for invoice_data in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_invoices(self):
        with open(self.filepath, 'w') as f:
            json.dump([invoice.to_dict() for invoice in self.invoices], f, indent=2)
    
    def add_invoice(self, invoice: Invoice):
        if not invoice.invoice_number:
            invoice.invoice_number = self.generate_invoice_number()
        self.invoices.append(invoice)
        self.save_invoices()
        return invoice.id
    
    def update_invoice(self, invoice_id: str, updated_invoice: Invoice):
        for i, invoice in enumerate(self.invoices):
            if invoice.id == invoice_id:
                updated_invoice.id = invoice_id
                updated_invoice.created_date = invoice.created_date
                self.invoices[i] = updated_invoice
                self.save_invoices()
                return True
        return False
    
    def delete_invoice(self, invoice_id: str):
        self.invoices = [invoice for invoice in self.invoices if invoice.id != invoice_id]
        self.save_invoices()
    
    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        for invoice in self.invoices:
            if invoice.id == invoice_id:
                return invoice
        return None
    
    def get_all_invoices(self) -> List[Invoice]:
        return sorted(self.invoices, key=lambda x: x.created_date, reverse=True)
    
    def generate_invoice_number(self) -> str:
        year = datetime.now().year
        existing_numbers = [
            inv.invoice_number for inv in self.invoices 
            if inv.invoice_number.startswith(f"INV-{year}")
        ]
        
        if not existing_numbers:
            return f"INV-{year}-001"
        
        # Extract numbers and find the highest
        numbers = []
        for num in existing_numbers:
            try:
                number_part = int(num.split('-')[-1])
                numbers.append(number_part)
            except (ValueError, IndexError):
                continue
        
        next_number = max(numbers, default=0) + 1
        return f"INV-{year}-{next_number:03d}"
