from pydantic import BaseModel, HttpUrl
from typing import Optional, Literal


class QrBasicRequest(BaseModel):
    data: str
    size: int = 512


class QrScanResult(BaseModel):
    decoded_value: str
    source: str
