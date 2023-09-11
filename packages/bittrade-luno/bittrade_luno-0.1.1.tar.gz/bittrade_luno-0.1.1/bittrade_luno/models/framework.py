from dataclasses import dataclass
from typing import Callable
from reactivex import ConnectableObservable, Observable
from reactivex.disposable import CompositeDisposable
from reactivex.scheduler import ThreadPoolScheduler

from ccxt import luno

from elm_framework_helpers.websockets.models import WebsocketBundle

from bittrade_luno.models.enhanced_websocket import EnhancedWebsocket
from bittrade_luno.models.rest.cancel_order import CancelOrderRequest, CancelOrderResponse
from bittrade_luno.models.rest.create_order import LimitOrderRequest, LimitOrderResponse
from bittrade_luno.models.rest.list_trade import ListTradeRequest, ListTradeResponse
from bittrade_luno.models.rest.order_book import ListOrderBookResponse, OrderBookRequest


@dataclass
class FrameworkContext:
    all_subscriptions: CompositeDisposable
    exchange: luno
    scheduler: ThreadPoolScheduler
    stream_bundles: ConnectableObservable[WebsocketBundle]
    stream_sockets: Observable[EnhancedWebsocket]
    stream_socket_messages: Observable[dict]
    private_stream_bundles: ConnectableObservable[WebsocketBundle]
    private_stream_sockets: Observable[EnhancedWebsocket]
    private_stream_socket_messages: Observable[dict]
    list_trade_http: Callable[[ListTradeRequest], Observable[ListTradeResponse]]
    list_top_orderbook_http: Callable[[OrderBookRequest], Observable[ListOrderBookResponse]]
    create_order_http: Callable[[LimitOrderRequest], Observable[LimitOrderResponse]]
    cancel_order_http: Callable[[CancelOrderRequest], Observable[CancelOrderResponse]]
