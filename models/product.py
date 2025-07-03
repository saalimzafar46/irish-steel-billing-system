from dataclasses import dataclass, asdict
from typing import List, Optional
import json
import uuid

@dataclass
class Product:
    id: str
    name: str
    description: str = ""
    category: str = "Steel Bar"  # Steel Bar, Steel Plate, Steel Beam, etc.
    grade: str = ""  # S355, S275, etc.
    dimensions: str = ""  # e.g., "20mm x 20mm x 6000mm"
    weight_per_unit: float = 0.0  # kg
    base_price: float = 0.0  # EUR per unit
    cutting_charge: float = 0.0  # EUR per cut
    unit_of_measure: str = "length"  # length, weight, piece
    finish: str = "Hot Rolled"  # Hot Rolled, Cold Rolled, Galvanized
    stock_quantity: int = 0
    min_order_quantity: int = 1
    is_cuttable: bool = True
    is_active: bool = True
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class ProductManager:
    def __init__(self, filepath="data/products.json"):
        self.filepath = filepath
        self.products = self.load_products()
    
    def load_products(self) -> List[Product]:
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                return [Product.from_dict(product_data) for product_data in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_products(self):
        with open(self.filepath, 'w') as f:
            json.dump([product.to_dict() for product in self.products], f, indent=2)
    
    def add_product(self, product: Product):
        product.id = str(uuid.uuid4())
        self.products.append(product)
        self.save_products()
        return product.id
    
    def update_product(self, product_id: str, updated_product: Product):
        for i, product in enumerate(self.products):
            if product.id == product_id:
                updated_product.id = product_id
                self.products[i] = updated_product
                self.save_products()
                return True
        return False
    
    def delete_product(self, product_id: str):
        self.products = [product for product in self.products if product.id != product_id]
        self.save_products()
    
    def get_product(self, product_id: str) -> Optional[Product]:
        for product in self.products:
            if product.id == product_id:
                return product
        return None
    
    def get_active_products(self) -> List[Product]:
        return [product for product in self.products if product.is_active]
    
    def get_all_products(self) -> List[Product]:
        return self.products
