from dataclasses import asdict, dataclass
from typing import TypedDict


@dataclass
class CancelOrderRequest:
    order_id: str

    def to_dict(self):
        as_dict = asdict(self)
        return as_dict

class CancelOrderResponse(TypedDict):
    success: bool