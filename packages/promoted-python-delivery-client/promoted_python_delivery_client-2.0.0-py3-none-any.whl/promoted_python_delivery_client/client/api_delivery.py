import logging
import requests
from promoted_python_delivery_client.client.delivery_request import DeliveryRequest
from promoted_python_delivery_client.client.delivery_request_state import DeliveryRequestState
from .serde import delivery_request_to_json_3, delivery_reponse_from_json_2
from promoted_python_delivery_client.model.response import Response


class APIDelivery:
    def __init__(self,
                 endpoint: str,
                 api_key: str,
                 timeout: int,
                 max_request_insertions: int,
                 warmup: bool = False) -> None:
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers.update({"x-api-key": api_key})
        self.max_request_insertions = max_request_insertions
        self.timeout_in_seconds = timeout / 1000
        if warmup:
            self._run_warmup()

    def run_delivery(self, delivery_request: DeliveryRequest) -> Response:
        state = DeliveryRequestState(delivery_request)

        request = state.get_request_to_send(self.max_request_insertions)
        payload = delivery_request_to_json_3(request)
        r = self.session.post(url=self.endpoint,
                              data=payload,
                              timeout=self.timeout_in_seconds)
        if r.status_code != 200:
            logging.error(f"Error calling delivery API {r.status_code}")
            raise requests.HTTPError("error calling delivery API")
        return state.get_response_to_return(delivery_reponse_from_json_2(r.content))

    def _run_warmup(self):
        warmup_endpoint = self.endpoint.replace("/deliver", "/healthz")
        for i in range(0, 20):
            r = self.session.get(url=warmup_endpoint)
            if r.status_code != 200:
                logging.warning(f"Error during warmup {r.status_code}")
