from bittrade_luno.models import endpoints
from bittrade_luno.models.request_message import RequestMessage
from bittrade_luno.models.rest.order_book import ListOrderBookResponse, OrderBookRequest
from bittrade_luno.rest.http_factory_decorator import http_factory


@http_factory(ListOrderBookResponse)
def list_top_orderbook_http_factory(
    params: OrderBookRequest,
):
    return RequestMessage(
        method="GET",
        endpoint=endpoints.LunoEndpoints.TOP_ORDER_BOOK,
        params=params.to_dict(),
    )