from bittrade_luno.models import endpoints
from bittrade_luno.models.request_message import RequestMessage
from bittrade_luno.models.rest.create_order import LimitOrderRequest, LimitOrderResponse
from bittrade_luno.rest.http_factory_decorator import http_factory


@http_factory(LimitOrderResponse)
def create_order_http_factory(
    params: LimitOrderRequest,
):
    return RequestMessage(
        method="POST",
        endpoint=endpoints.LunoEndpoints.POST_LIMIT_ORDER,
        params=params.to_dict(),
    )