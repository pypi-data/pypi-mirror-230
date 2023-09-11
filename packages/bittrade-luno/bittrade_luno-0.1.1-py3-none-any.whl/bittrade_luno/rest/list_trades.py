from bittrade_luno.models import endpoints
from bittrade_luno.models.request_message import RequestMessage
from bittrade_luno.models.rest.list_trade import ListTradeRequest, ListTradeResponse
from bittrade_luno.rest.http_factory_decorator import http_factory


@http_factory(ListTradeResponse)
def list_trade_http_factory(
    params: ListTradeRequest,
):
    return RequestMessage(
        method="GET",
        endpoint=endpoints.LunoEndpoints.LIST_RECENT_TRADES,
        params=params.to_dict(),
    )