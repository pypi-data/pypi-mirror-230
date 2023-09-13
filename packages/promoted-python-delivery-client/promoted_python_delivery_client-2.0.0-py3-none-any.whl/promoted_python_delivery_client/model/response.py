from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase
from typing import List, Optional

from promoted_python_delivery_client.model.insertion import Insertion
from promoted_python_delivery_client.model.paging_info import PagingInfo


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Response:
    request_id: str
    # Delivery API can omit the `insertion` field if the list is empty.
    insertion: List[Insertion] = field(default_factory=list)  # type: ignore
    paging_info: Optional[PagingInfo] = None
    introspection_data: Optional[str] = None
