from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase
from typing import Optional
from promoted_python_delivery_client.model.client_hints import ClientHints
from promoted_python_delivery_client.model.size import Size


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Browser:
    client_hints: Optional[ClientHints] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    user_agent: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    viewport_size: Optional[Size] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
