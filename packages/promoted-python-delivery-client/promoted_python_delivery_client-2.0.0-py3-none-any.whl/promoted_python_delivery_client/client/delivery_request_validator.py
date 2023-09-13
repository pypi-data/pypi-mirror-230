
from typing import List, Optional

from promoted_python_delivery_client.client.delivery_request import DeliveryRequest
from promoted_python_delivery_client.model.cohort_membership import CohortMembership
from promoted_python_delivery_client.model.request import Request


class DeliveryRequestValidator():
    def validate(self, request: DeliveryRequest, is_shadow_traffic: bool) -> List[str]:
        validation_errors: List[str] = []

        req = request.request
        if req is None:
            return ["Request must be set"]

        # Check the ids.
        validation_errors.extend(self.validate_ids(request.request))

        validation_errors.extend(self.validate_insertions(request.request))

        # Insertion start should be >= 0
        if request.insertion_start < 0:
            validation_errors.append("Insertion start must be greater or equal to 0")

        return validation_errors

    def validate_ids(self, request: Request) -> List[str]:
        validation_errors: List[str] = []

        if request.request_id:
            validation_errors.append("Request.requestId should not be set")

        if request.user_info is None:
            validation_errors.append("Request.userInfo should be set")
        elif not request.user_info.anon_user_id:
            validation_errors.append("Request.userInfo.anonUserId should be set")

        return validation_errors

    def validate_insertions(self, request: Request) -> List[str]:
        validation_errors: List[str] = []

        has_matrix_headers = request.insertion_matrix_headers is not None
        has_matrix = request.insertion_matrix is not None
        if has_matrix_headers != has_matrix:
            validation_errors.append(
                "Request.insertionMatrixHeaders and Request.insertionMatrix should be used together")
        elif has_matrix_headers:
            if request.insertion and len(request.insertion) > 0:
                validation_errors.append(
                    "Request.insertion will be ignored because Request.insertionMatrix is present")
            # Validate headers.
            content_id_set = False
            for header in request.insertion_matrix_headers:
                if header == "insertionId":
                    validation_errors.append("Request.insertionMatrixHeaders should not specify insertionId")
                elif header == "contentId":
                    content_id_set = True
            if not content_id_set:
                validation_errors.append("Request.insertionMatrixHeaders should specify contentId")
            # Validate matrix.
            for insertion in request.insertion_matrix:
                if len(insertion) != len(request.insertion_matrix_headers):
                    validation_errors.append(
                        "Request.insertionMatrix elements should be equal length to Request.insertionMatrixHeaders")
        else:
            if request.insertion is None:
                validation_errors.append("Request.insertion should be set")
            else:
                for ins in request.insertion:
                    if ins.insertion_id:
                        validation_errors.append("Insertion.insertionId should not be set")
                    if not ins.content_id:
                        validation_errors.append("Insertion.contentId should be set")

        return validation_errors
