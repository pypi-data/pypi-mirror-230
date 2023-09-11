import requests
from typing import Callable, cast
from ccxt import luno
from reactivex import Observable, operators
from reactivex.disposable import CompositeDisposable
from reactivex.scheduler import ThreadPoolScheduler
from reactivex.subject import BehaviorSubject
from elm_framework_helpers.websockets.operators import connection_operators
from elm_framework_helpers.websockets.models.bundle import WebsocketBundle

from bittrade_luno.connection.private import private_websocket_connection
from bittrade_luno.connection.public import public_websocket_connection
from bittrade_luno.models.enhanced_websocket import EnhancedWebsocket
from bittrade_luno.models.framework import FrameworkContext
from bittrade_luno.rest.cancel_order import cancel_order_http_factory
from bittrade_luno.rest.create_order import create_order_http_factory
from bittrade_luno.rest.list_trades import list_trade_http_factory
from bittrade_luno.rest.top_orderbook import list_top_orderbook_http_factory

def get_framework(
    *,
    pair: str,
    authenticate_signer: Callable[
        [EnhancedWebsocket], EnhancedWebsocket
    ] = None, 
    trade_signer_http: Callable[
        [requests.models.Request], requests.models.Request
    ] = None,
    load_markets=True,
) -> FrameworkContext:
    exchange = luno()
    if load_markets:
        exchange.load_markets()

    details = exchange.market(pair)
    pair = details.get("id")

    pool_scheduler = ThreadPoolScheduler(200)
    all_subscriptions = CompositeDisposable()

    stream_bundles = public_websocket_connection(
        pair=pair
    )
    stream_sockets = stream_bundles.pipe(
        connection_operators.keep_new_socket_only(),
        operators.share(),
    )
    stream_socket_messages = stream_bundles.pipe(
        connection_operators.keep_messages_only(), operators.share()
    )
    stream_sockets.subscribe(authenticate_signer)

    private_stream_bundles = private_websocket_connection()
    private_stream_sockets = private_stream_bundles.pipe(
        connection_operators.keep_new_socket_only(),
        operators.share(),
    )
    private_stream_socket_messages = private_stream_bundles.pipe(
        connection_operators.keep_messages_only(), operators.share()
    )
    private_stream_sockets.subscribe(authenticate_signer)

    list_trade_http = list_trade_http_factory(trade_signer_http)
    list_top_orderbook_http = list_top_orderbook_http_factory(trade_signer_http)
    create_order_http = create_order_http_factory(trade_signer_http)
    cancel_order_http = cancel_order_http_factory(trade_signer_http)

    return FrameworkContext(
        all_subscriptions=all_subscriptions,
        exchange=exchange,
        scheduler=pool_scheduler,
        stream_bundles=stream_bundles,
        stream_sockets=stream_sockets,
        stream_socket_messages=stream_socket_messages,
        private_stream_bundles=private_stream_bundles,
        private_stream_sockets=private_stream_sockets,
        private_stream_socket_messages=private_stream_socket_messages,
        list_trade_http=list_trade_http,
        list_top_orderbook_http=list_top_orderbook_http,
        create_order_http=create_order_http,
        cancel_order_http=cancel_order_http,
    )


