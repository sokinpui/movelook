from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class BaseData:
    id: str
    timestamp: str

    def to_dict(self):
        return asdict(self)

@dataclass
class UserData(BaseData):
    name: str
    age: int
    email: str

@dataclass
class ProductData(BaseData):
    name: str
    price: float
    category: str

# Example usage
user = UserData(id="1", timestamp="2023-10-01", name="John Doe", age=30, email="john@example.com")
product = ProductData(id="2", timestamp="2023-10-01", name="Laptop", price=999.99, category="Electronics")

# Convert to dictionary for Elasticsearch
user_dict = user.to_dict()
product_dict = product.to_dict()

print(type(user_dict))
print(product_dict)
