import requests
from logging import getLogger
from os import getenv
from reactivex import Observable, abc
from reactivex.disposable import Disposable

from bittrade_luno.models.request_message import RequestMessage

logger = getLogger(__name__)

LUNO_HTTP_URL = getenv("LUNO_HTTP_URL", "https://api.luno.com")
session = requests.Session()

def prepare_request(message: RequestMessage) -> requests.models.Request:
    http_method = message.method
    kwargs = {}
    # check if message params are set, if not, ignores
    if message.params:
        if http_method == "GET":
            kwargs["params"] = message.params
        else:
            kwargs["data"] = message.params

    # There are (few) cases where the endpoint must be a string; "handle" that below
    try:
        endpoint = message.endpoint.value
    except AttributeError:
        endpoint = message.endpoint
    return requests.Request(http_method, f"{LUNO_HTTP_URL}{endpoint}", **kwargs)


def send_request(request: requests.models.Request) -> Observable:
    def subscribe(
        observer: abc.ObserverBase,
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        response = session.send(request.prepare())
        if response.ok:
            try:
                body = response.json()
                observer.on_next(body)
                observer.on_completed()
            except Exception as exc:
                logger.error(
                    "Error parsing request %s; request was %s",
                    response.text,
                    response.request.body
                    if request.method == "POST"
                    else response.request.headers,
                )
                observer.on_error(exc)
        else:
            try:
                logger.error(
                    "Error with request %s; request was %s",
                    response.text,
                    response.request.body
                    if request.method == "POST"
                    else response.request.headers,
                )
                response.raise_for_status()
            except Exception as exc:
                observer.on_error(exc)
        return Disposable()

    return Observable(subscribe)