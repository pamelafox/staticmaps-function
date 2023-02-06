import fastapi

from . import fastapi_routes


def create_app():
    app = fastapi.FastAPI(docs_url="/")
    app.include_router(fastapi_routes.router)
    return app
