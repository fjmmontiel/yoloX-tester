from typing import List, Optional
from pydantic import Field
from datetime import datetime
from uuid import uuid4
from util.camel_base_model import CamelBaseModel
from datetime import datetime

class Image(CamelBaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    original_file_name: str
    created_on: Optional[str] = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    crops: List
    file_path: str
    image_summary: dict
