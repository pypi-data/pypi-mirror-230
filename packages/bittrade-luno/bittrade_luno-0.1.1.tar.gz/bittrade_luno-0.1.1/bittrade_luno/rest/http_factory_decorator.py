import functools
from typing import Any, Callable, ParamSpec, Type, TypeVar, TypedDict, cast
import requests
from reactivex import Observable
from bittrade_luno.connection import http

from bittrade_luno.models.request_message import RequestMessage

P = ParamSpec("P")


# TODO this typing does not work, it does not allow us to define the sub type of the response's result
R = TypeVar("R")


def http_factory(return_type: Type):
    def factory_wrapper(
        fn: Callable[P, RequestMessage]
    ) -> Callable[
        [Callable[[requests.models.Request], requests.models.Request]],
        Callable[P, Observable[return_type]],
    ]:
        @functools.wraps(fn)
        def factory(
            add_token: Callable[[requests.models.Request], requests.models.Request]
        ):
            def inner(*args: P.args, **kwargs: P.kwargs) -> Observable[return_type]:
                request = fn(*args, **kwargs)
                return cast(
                    Observable[return_type],
                    http.send_request(add_token(http.prepare_request(request))),
                )

            return inner

        return factory

    return factory_wrapper
