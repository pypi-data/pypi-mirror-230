from enum import Enum


class LunoEndpoints(Enum):
    POST_LIMIT_ORDER = "/api/1/postorder"
    CANCEL_ORDER = "/api/1/stoporder"
    LIST_RECENT_TRADES = "/api/1/trades"
    TOP_ORDER_BOOK = "/api/1/orderbook_top"
