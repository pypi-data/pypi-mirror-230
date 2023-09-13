import logging
import requests
from promoted_python_delivery_client.client.serde import log_request_to_json_3
from promoted_python_delivery_client.model.log_request import LogRequest


class APIMetrics:
    def __init__(self,
                 endpoint: str,
                 api_key: str,
                 timeout: int) -> None:
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers.update({"x-api-key": api_key})
        self.timeout_in_seconds = timeout / 1000

    def run_metrics_logging(self, log_request: LogRequest) -> None:
        payload = log_request_to_json_3(log_request)
        r = self.session.post(url=self.endpoint,
                              data=payload,
                              timeout=self.timeout_in_seconds)
        if r.status_code != 200:
            logging.error(f"Error calling metrics API {r.status_code}")
            raise requests.HTTPError("error calling metrics API")
