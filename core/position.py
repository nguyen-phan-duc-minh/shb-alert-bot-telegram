from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Layer: # lop layer de luu tru thong tin tung lop trong vi tri
    price: float
    quantity: int
    time: str

class Position: # lop vi tri de luu tru thong tin vi tri cua mot co phieu
    def __init__(self, symbol: str, layers: List[Layer] = None):
        self.symbol = symbol
        self.layers = layers or []

    def add_layer(self, price: float, quantity: int):
        self.layers.append(
            Layer(price=price, quantity=quantity, time=datetime.now().isoformat())
        ) # gia hien tai va so luong mua them vao layer moi

    def total_quantity(self):
        return sum(l.quantity for l in self.layers) # tinh tong so luong co phieu trong vi tri

    def average_price(self): # tinh gia trung binh cua vi tri
        if not self.layers:
            return 0
        total = sum(l.price * l.quantity for l in self.layers)
        return total / self.total_quantity()
