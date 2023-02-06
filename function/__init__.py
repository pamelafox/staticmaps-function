import enum
import io

import azure.functions
import fastapi
import fastapi.responses
import nest_asyncio
import staticmaps

app = fastapi.FastAPI()
nest_asyncio.apply()

tile_provider_names = list(staticmaps.default_tile_providers.keys())
tile_provider_names.remove("none")
TileProvider = enum.Enum('TileProvider', ((x,x) for x in tile_provider_names))

@app.get("/generate_map")
def generate_map(center: str = fastapi.Query(example="40.714728,-73.998672", regex="^-?\d+(\.\d+)?,-?\d+(\.\d+)?$"),
         zoom: int = fastapi.Query(example=12, ge=0, le=30),
         width: int = 400,
         height: int = 400,
         tile_provider: TileProvider = TileProvider.osm
         ) -> fastapi.responses.Response:
    
    # Create the static map context
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.default_tile_providers[tile_provider.value])
    center = center.split(",")
    newyork = staticmaps.create_latlng(float(center[0]), float(center[1]))
    context.set_center(newyork)
    context.set_zoom(zoom)

    # Render to PNG image and return
    image_pil = context.render_pillow(width, height)
    img_byte_arr = io.BytesIO()
    image_pil.save(img_byte_arr, format='PNG')
    return fastapi.responses.Response(img_byte_arr.getvalue(), media_type="image/png")

async def main(
    req: azure.functions.HttpRequest, context: azure.functions.Context
) -> azure.functions.HttpResponse:
    return azure.functions.AsgiMiddleware(app).handle(req, context)