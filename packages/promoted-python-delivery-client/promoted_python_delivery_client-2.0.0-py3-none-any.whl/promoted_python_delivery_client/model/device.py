from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json, LetterCase
from typing import Optional
from promoted_python_delivery_client.model.browser import Browser
from promoted_python_delivery_client.model.locale import Locale
from promoted_python_delivery_client.model.location import Location
from promoted_python_delivery_client.model.screen import Screen


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Device:
    brand: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    browser: Optional[Browser] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    device_type: Optional[int] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    identifier: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    ip_address: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    locale: Optional[Locale] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    location: Optional[Location] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    manufacturer: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    os_version: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    platform_app_version: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    promoted_mobile_sdk_version: Optional[str] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
    screen: Optional[Screen] = field(default=None, metadata=config(exclude=lambda v: v is None))  # type: ignore
