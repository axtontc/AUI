import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# Global tracer instance
_tracer = None

def get_tracer(service_name: str = "AUI_Service") -> trace.Tracer:
    """Retrieves or initializes a globally configured OpenTelemetry tracer."""
    global _tracer
    if _tracer is not None:
        return _tracer

    resource = Resource.create(attributes={"service.name": service_name})
    provider = TracerProvider(resource=resource)

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        try:
            # We dynamically import the OTLP exporter to keep core startup lightweight
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        except Exception:
            # Fallback to console logging if exporter setup fails
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    else:
        # In mock/local unit testing, we default to Console or silent NoOp depending on environment
        if os.getenv("AUI_DEBUG_TELEMETRY"):
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(service_name)
    return _tracer
