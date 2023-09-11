from typing import Callable, Optional

from reactivex import ConnectableObservable
from reactivex.operators import publish, map
from reactivex.abc import SchedulerBase
import os
from elm_framework_helpers.websockets.models import WebsocketBundle

from bittrade_luno.connection.generic import raw_websocket_connection
from bittrade_luno.connection.reconnect import retry_with_backoff


LUNO_STREAM_URL = os.getenv('LUNO_USER_STREAM_WEBSOCKET', 'wss://ws.luno.com/api/1/userstream')

def private_websocket_connection(
    *, 
    reconnect: bool = True, 
    scheduler: Optional[SchedulerBase] = None
) -> ConnectableObservable[WebsocketBundle]:
    connection = raw_websocket_connection(LUNO_STREAM_URL, scheduler=scheduler)
    if reconnect:
        connection = connection.pipe(retry_with_backoff)
    return connection.pipe(publish())

__all__ = [
    "private_websocket_connection",
]
