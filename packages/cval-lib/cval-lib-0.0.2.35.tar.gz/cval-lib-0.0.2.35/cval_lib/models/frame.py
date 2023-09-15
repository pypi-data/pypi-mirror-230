from typing import Optional

from pydantic import BaseModel


class FrameModel(BaseModel):
    img_external_id: str
    img_raw: Optional[bytes]
    img_link: Optional[str]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.img_raw is None and self.img_link is None:
            raise ValueError('img_raw and img_link can\'t be None together.')
