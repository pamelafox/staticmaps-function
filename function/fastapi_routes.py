import enum
import io

import fastapi
import fastapi.responses
import staticmaps
from PIL import ImageDraw


def _pillow_textsize_compat(self, text, font=None, *args, **kwargs):
    """
    Compatibility function for Pillow 10.x that provides the old textsize() behavior.

    This function uses the new textbbox() method and converts the result to the
    (width, height) tuple that textsize() used to return.

    The textsize() method was removed in Pillow 10.0.0 and replaced with textbbox().
    See: https://github.com/python-pillow/Pillow/pull/6474
    Migration guide: https://pillow.readthedocs.io/en/stable/releasenotes/10.0.0.html#font-size-and-offset-methods

    Args:
        text: The text to measure
        font: The font to use (optional)
        *args, **kwargs: Additional arguments passed to textbbox

    Returns:
        tuple: (width, height) of the text
    """
    # Use textbbox with anchor point (0, 0) and convert to size
    bbox = self.textbbox((0, 0), text, font=font, *args, **kwargs)
    # bbox is (left, top, right, bottom), so width = right - left, height = bottom - top
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])


def _ensure_pillow_textsize_compatibility():
    """
    Ensure textsize() method is available for py-staticmaps compatibility.
    
    This function patches ImageDraw.ImageDraw to add the textsize() method
    if it doesn't exist (i.e., in Pillow 10.x). This is needed because
    py-staticmaps 0.4.0 uses the deprecated textsize() method.
    """
    if not hasattr(ImageDraw.ImageDraw, "textsize"):
        ImageDraw.ImageDraw.textsize = _pillow_textsize_compat


router = fastapi.APIRouter()

tile_provider_names = list(staticmaps.default_tile_providers.keys())
tile_provider_names.remove("none")
TileProvider = enum.Enum("TileProvider", ((x, x) for x in tile_provider_names))


class ImageResponse(fastapi.responses.Response):
    media_type = "image/png"


@router.get(
    "/generate_map",
    response_class=ImageResponse,
    responses={200: {"content": {"image/png": {"schema": {"type": "string", "format": "binary"}}}}},
)
def generate_map(
    center: str = fastapi.Query(example="40.714728,-73.998672", pattern=r"^-?\d+(\.\d+)?,-?\d+(\.\d+)?$"),
    zoom: int = fastapi.Query(example=12, ge=0, le=30),
    width: int = 400,
    height: int = 400,
    tile_provider: TileProvider = TileProvider.osm,
) -> ImageResponse:
    # Ensure Pillow 10.x compatibility for py-staticmaps
    _ensure_pillow_textsize_compatibility()
    
    # Create the static map context
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.default_tile_providers[tile_provider.value])
    center = center.split(",")
    center_ll = staticmaps.create_latlng(float(center[0]), float(center[1]))
    context.set_center(center_ll)
    context.set_zoom(zoom)

    # Render to PNG image and return
    image_pil = context.render_pillow(width, height)
    img_byte_arr = io.BytesIO()
    image_pil.save(img_byte_arr, format="PNG")
    return ImageResponse(img_byte_arr.getvalue())
