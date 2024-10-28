from modules.script_callbacks import on_app_started
from fastapi.exceptions import HTTPException
from fastapi import FastAPI, Body
from PIL import Image

from lib_utilities.funcs import SingleImageResponse, decode, encode


def register_utils(_, app: FastAPI):

    @app.post(path="/utils/blend", response_model=SingleImageResponse)
    async def blend(
        force: bool = Body(False, title="auto convert"),
        images: list[str] = Body(
            "An array of base64 images, sorted from bottom to top",
            title="input images",
        ),
    ):
        if len(images) < 2:
            raise HTTPException(status_code=500, detail="Invalid Input")

        input_images = [
            (decode(img).convert("RGBA") if force else decode(img)) for img in images
        ]

        bg, *fg = input_images
        size = bg.size
        if not all(img.size == size for img in fg):
            raise HTTPException(status_code=500, detail="Size Unmatched")

        print(f"[API.Utils] Stacking {len(input_images)} images")
        for img in fg:
            bg.paste(img, None, img)
        return {"image": encode(bg)}

    @app.post(path="/utils/resize", response_model=SingleImageResponse)
    async def resize(
        image: str = Body("base64", title="input image"),
        width: int = Body(1024, title="target width"),
        height: int = Body(1024, title="target height"),
    ):
        if not image:
            raise HTTPException(status_code=500, detail="No Input")

        input_image = decode(image)
        print(f"[API.Utils] Resizing {input_image.size} to {(width, height)}")
        resized_image = input_image.resize((width, height), Image.LANCZOS)
        return {"image": encode(resized_image)}

    @app.post(path="/utils/tint", response_model=SingleImageResponse)
    async def tint(
        image: str = Body("base64", title="input image"),
        color: list[int] = Body([255, 255, 255, 128], title="Color32"),
    ):
        if not image:
            raise HTTPException(status_code=500, detail="No Input")
        if len(color) != 4:
            raise HTTPException(status_code=500, detail="Invalid Color")

        input_image = decode(image)
        r, g, b, alpha = input_image.split()
        overlay = Image.new("RGBA", input_image.size, tuple(color))
        print(f"[API.Utils] Tinting to {color}")
        tinted_image = Image.alpha_composite(input_image, overlay)
        composite = Image.composite(tinted_image, input_image, alpha)
        return {"image": encode(composite)}

    @app.post(path="/utils/crop", response_model=SingleImageResponse)
    async def crop(
        image: str = Body("base64", title="input image"),
        width: int = Body(512, title="target width"),
        height: int = Body(512, title="target height"),
    ):
        if not image:
            raise HTTPException(status_code=500, detail="No Input")

        input_image = decode(image)
        og_w, og_h = input_image.size

        if og_w < width or og_h < height:
            raise HTTPException(status_code=500, detail="Target is larger than Input")
        else:
            print(f"[API.Utils] Cropping {(og_w, og_h)} to {(width, height)}")

        left = (og_w - width) / 2
        top = (og_h - height) / 2
        right = (og_w + width) / 2
        bottom = (og_h + height) / 2

        cropped_image = input_image.crop((left, top, right, bottom))
        return {"image": encode(cropped_image)}


on_app_started(register_utils)
