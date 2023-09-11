from dataclasses import asdict, dataclass
from typing import TypedDict


@dataclass
class LimitOrderRequest:
    pair: str
    type: str
    post_only: bool
    volume: str
    price: str
    time_in_force: str = "GTC"
    stop_price: str = None
    stop_direction: str = None
    base_account_id: int = None
    counter_account_id: int = None
    timestamp: int = None
    ttl: int = None
    client_order_id: str = None


    def to_dict(self):
        as_dict = asdict(self)
        return as_dict

class LimitOrderResponse(TypedDict):
    order_id: str