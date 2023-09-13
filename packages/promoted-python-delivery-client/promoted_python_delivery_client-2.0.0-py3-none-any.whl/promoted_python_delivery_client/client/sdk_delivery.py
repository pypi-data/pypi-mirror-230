from typing import List
import uuid
from promoted_python_delivery_client.client.delivery_request import DeliveryRequest
from promoted_python_delivery_client.model.insertion import Insertion
from promoted_python_delivery_client.model.paging import Paging
from promoted_python_delivery_client.model.response import Response


class SDKDelivery:
    def __init__(self) -> None:
        pass

    def run_delivery(self, request: DeliveryRequest) -> Response:
        req = request.request
        paging = req.paging

        # Assume validation has already happened.
        use_matrix = req.insertion_matrix_headers is not None;
        content_id_matrix_position = 0
        if use_matrix:
            for idx, header in enumerate(req.insertion_matrix_headers):
                if header == "contentId":
                    content_id_matrix_position = idx
                    break
        num_insertions = len(req.insertion_matrix) if use_matrix else len(req.insertion)

        # Set a request id.
        req.request_id = str(uuid.uuid4())
        if paging is None:
            paging = Paging(offset=0, size=num_insertions)

        # Adjust size and offset.
        offset = max(0, paging.offset) if paging.offset is not None else 0
        if offset < request.insertion_start:
            raise ValueError("offset should be >= insertion start (specifically, the global position)")
        index = offset - request.insertion_start
        size = paging.size if paging.size is not None else 0
        if size <= 0:
            size = num_insertions

        final_insertion_size = min(size, num_insertions - index)
        insertion_page: List[Insertion] = []
        for i in range(0, final_insertion_size):
            if use_matrix:
                content_id = req.insertion_matrix[index][content_id_matrix_position]
            else:
                content_id = req.insertion[index].content_id

            # Delivery response insertions only contain content_id + the fields added in _prepare_response_insertion
            resp_ins = Insertion(content_id=content_id)
            self._prepare_response_insertion(resp_ins, offset)
            insertion_page.append(resp_ins)
            index = index + 1
            offset = offset + 1

        return Response(insertion=insertion_page, request_id=req.request_id)

    def _prepare_response_insertion(self, ins: Insertion, position: int) -> None:
        ins.position = position
        ins.insertion_id = str(uuid.uuid4())
