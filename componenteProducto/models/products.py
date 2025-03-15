from db import db
import sqlparse
from pathlib import Path

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)  # Nuevo campo
    stock = db.Column(db.Integer, nullable=False)  # Nuevo campo
    description = db.Column(db.String(255))  # Nuevo campo opcional

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "description": self.description
        }
    
    def __init__(self, name, price, stock, description=None):
        self.name = name
        self.price = price
        self.stock = stock
        self.description = description