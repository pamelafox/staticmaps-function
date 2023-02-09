import enum
import io

import fastapi
import fastapi.responses
import staticmaps

router = fastapi.APIRouter()

tile_provider_names = list(staticmaps.default_tile_providers.keys())
tile_provider_names.remove("none")
TileProvider = enum.Enum("TileProvider", ((x, x) for x in tile_provider_names))


@router.get("/generate_map")
def generate_map(
    center: str = fastapi.Query(example="40.714728,-73.998672", regex=r"^-?\d+(\.\d+)?,-?\d+(\.\d+)?$"),
    zoom: int = fastapi.Query(example=12, ge=0, le=30),
    width: int = 400,
    height: int = 400,
    tile_provider: TileProvider = TileProvider.osm,
) -> fastapi.responses.Response:
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
    return fastapi.responses.Response(img_byte_arr.getvalue(), media_type="image/png")
