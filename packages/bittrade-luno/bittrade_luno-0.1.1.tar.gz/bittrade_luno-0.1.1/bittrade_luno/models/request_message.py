import dataclasses
import time
from typing import Any, Literal

from bittrade_luno.models import endpoints


@dataclasses.dataclass(frozen=True)
class RequestMessage:
    method: Literal["GET", "POST", "PUT", "DELETE"]
    endpoint: endpoints.LunoEndpoints
    params: dict[str, Any] = dataclasses.field(default_factory=dict)
    client_order_id: int = 0
