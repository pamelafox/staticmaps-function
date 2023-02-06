import os

import azure.functions
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .fastapi_app import create_app

fastapi_app = create_app()


@fastapi_app.on_event("startup")
async def startup_event():
    if conn_str := os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        exporter = AzureMonitorTraceExporter.from_connection_string(conn_str)
        tracer = TracerProvider(resource=Resource({SERVICE_NAME: "api"}))
        tracer.add_span_processor(BatchSpanProcessor(exporter))
        FastAPIInstrumentor.instrument_app(fastapi_app, tracer_provider=tracer)


async def main(req: azure.functions.HttpRequest, context: azure.functions.Context) -> azure.functions.HttpResponse:
    return await azure.functions.AsgiMiddleware(fastapi_app).handle_async(req, context)
