import os

import fastapi
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from . import fastapi_routes


def create_app():
    app = fastapi.FastAPI(docs_url="/")
    if conn_str := os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        exporter = AzureMonitorTraceExporter.from_connection_string(conn_str)
        tracer = TracerProvider(resource=Resource({SERVICE_NAME: "api"}))
        tracer.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(tracer)

        # Use the newer instrumentation pattern
        FastAPIInstrumentor().instrument()

    app.include_router(fastapi_routes.router)

    return app
