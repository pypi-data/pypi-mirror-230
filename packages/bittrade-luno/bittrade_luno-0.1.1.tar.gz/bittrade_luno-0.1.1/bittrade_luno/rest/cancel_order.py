from bittrade_luno.models import endpoints
from bittrade_luno.models.request_message import RequestMessage
from bittrade_luno.models.rest.cancel_order import CancelOrderRequest, CancelOrderResponse
from bittrade_luno.rest.http_factory_decorator import http_factory


@http_factory(CancelOrderResponse)
def cancel_order_http_factory(
    params: CancelOrderRequest,
):
    return RequestMessage(
        method="POST",
        endpoint=endpoints.LunoEndpoints.CANCEL_ORDER,
        params=params.to_dict(),
    )