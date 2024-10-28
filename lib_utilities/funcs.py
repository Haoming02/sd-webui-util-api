from base64 import b64encode, b64decode
from pydantic import BaseModel, Field
from io import BytesIO
from PIL import Image


class SingleImageResponse(BaseModel):
    image: str = Field(title="Image", default="base64")


def decode(b64: str) -> Image.Image:
    return Image.open(BytesIO(b64decode(b64)))


def encode(img: Image.Image) -> str:
    with BytesIO() as buffer:
        img.save(buffer, format="PNG", optimize=True)
        return b64encode(buffer.getvalue()).decode("utf-8")
