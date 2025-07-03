from dataclasses import dataclass, asdict
from typing import List, Optional
import json
from datetime import datetime
import uuid

@dataclass
class Client:
    id: str
    name: str
    contact_person: str = ""
    address: str = ""
    city: str = ""
    county: str = ""
    postal_code: str = ""
    country: str = "Ireland"
    phone: str = ""
    email: str = ""
    vat_number: str = ""
    payment_terms: str = "30 days"
    credit_limit: float = 0.0
    notes: str = ""
    created_date: str = ""
    
    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class ClientManager:
    def __init__(self, filepath="data/clients.json"):
        self.filepath = filepath
        self.clients = self.load_clients()
    
    def load_clients(self) -> List[Client]:
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                return [Client.from_dict(client_data) for client_data in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_clients(self):
        with open(self.filepath, 'w') as f:
            json.dump([client.to_dict() for client in self.clients], f, indent=2)
    
    def add_client(self, client: Client):
        client.id = str(uuid.uuid4())
        self.clients.append(client)
        self.save_clients()
        return client.id
    
    def update_client(self, client_id: str, updated_client: Client):
        for i, client in enumerate(self.clients):
            if client.id == client_id:
                updated_client.id = client_id
                updated_client.created_date = client.created_date
                self.clients[i] = updated_client
                self.save_clients()
                return True
        return False
    
    def delete_client(self, client_id: str):
        self.clients = [client for client in self.clients if client.id != client_id]
        self.save_clients()
    
    def get_client(self, client_id: str) -> Optional[Client]:
        for client in self.clients:
            if client.id == client_id:
                return client
        return None
    
    def get_all_clients(self) -> List[Client]:
        return self.clients
