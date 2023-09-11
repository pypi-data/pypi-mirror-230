from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import List, TypedDict


@dataclass
class ListTradeRequest:
    pair: str
    since: int

    def to_dict(self):
        as_dict = asdict(self)
        return as_dict

@dataclass
class Trade:
    is_buy: bool
    price: str
    sequence: int
    timestamp: int
    volume: str

class TradeResponse(TypedDict):
    is_buy: bool
    price: str
    sequence: int
    timestamp: int
    volume: str
    
class ListTradeResponse(TypedDict):
    trades: List[TradeResponse]