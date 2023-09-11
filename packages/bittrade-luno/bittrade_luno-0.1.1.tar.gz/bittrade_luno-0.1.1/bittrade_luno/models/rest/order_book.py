from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import List, TypedDict


@dataclass
class OrderBookRequest:
    pair: str

    def to_dict(self):
        as_dict = asdict(self)
        return as_dict

class OrderBookResponse(TypedDict):
    price: str
    volume: str
    
class ListOrderBookResponse(TypedDict):
    asks: List[OrderBookResponse]
    bids: List[OrderBookResponse]
    timestamp: int