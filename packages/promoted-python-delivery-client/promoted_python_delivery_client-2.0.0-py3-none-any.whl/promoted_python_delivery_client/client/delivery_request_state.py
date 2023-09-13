
from dataclasses import dataclass
from promoted_python_delivery_client.client.delivery_request import DeliveryRequest
from promoted_python_delivery_client.model.request import Request
from promoted_python_delivery_client.model.response import Response


@dataclass
class DeliveryRequestState:
    delivery_request: DeliveryRequest

    def get_response_to_return(self, resp: Response) -> Response:
        return _validate_response(resp)

    def get_request_to_send(self, max_request_insertions: int) -> Request:
        req = self.delivery_request.request
        if req.insertion and len(req.insertion) > max_request_insertions:
            req.insertion = req.insertion[0:max_request_insertions]
        if req.insertion_matrix and len(req.insertion_matrix) > max_request_insertions:
            req.insertion_matrix = req.insertion_matrix[0:max_request_insertions]
        return req


def _validate_response(response: Response) -> Response:
    if not response.request_id:
        raise ValueError(f"Delivery Response must have request_id; response={response}")
    return response
