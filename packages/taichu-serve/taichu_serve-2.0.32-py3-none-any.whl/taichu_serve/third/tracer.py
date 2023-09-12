import logging
import typing

from opentelemetry import trace
from opentelemetry.trace.span import Span
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.util import types
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer
from opentelemetry.instrumentation.grpc import GrpcAioInstrumentorServer

from taichu_serve.settings import parse_args

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

args = parse_args()


def init_opentelemetry(jaeger_url=args.jaeger_url, app=None):
    if args.env == "prod":
        # 设置服务名、主机名
        resource = Resource(attributes={
            SERVICE_NAME: "taichu_serve",
            SERVICE_VERSION: "1.0.0"
        })
        # 使用GRPC协议上报
        span_processor = BatchSpanProcessor(OTLPSpanExporter(
            endpoint=jaeger_url,
        ))
        trace_provider = TracerProvider(resource=resource, active_span_processor=span_processor)
        trace.set_tracer_provider(trace_provider)

        if app:
            FlaskInstrumentor().instrument_app(app)

        GrpcInstrumentorServer().instrument()
        GrpcAioInstrumentorServer().instrument()

        logger.info("init opentelemetry finish")
        return True
    else:
        return None


def set_attribute(span: Span, key: str, value: types.AttributeValue):
    if args.env == "prod":
        return span.set_attribute(key, value)
    else:
        return None


def add_event(span: Span,
              name: str,
              attributes: types.Attributes = None,
              timestamp: typing.Optional[int] = None):
    if args.env == "prod":
        return span.add_event(name, attributes, timestamp)
    else:
        return None


def set_status(span: Span,
               status: typing.Union[Status, StatusCode],
               description: typing.Optional[str] = None):
    if args.env == "prod":
        return span.set_status(status, description)
    else:
        return None


def record_exception(span: Span,
                     exception: Exception,
                     attributes: types.Attributes = None,
                     timestamp: typing.Optional[int] = None,
                     escaped: bool = False):
    if args.env == "prod":
        return span.record_exception(exception, attributes, timestamp, escaped)
    else:
        return None


def print_span_info(name):
    span_ctx = trace.get_current_span().get_span_context()
    logger.info("[{}] trace_id:{}, span_id:{}, trace_state:{}, trace_flags:{}".format(
        name, span_ctx.trace_id, span_ctx.span_id, span_ctx.trace_state, span_ctx.trace_flags))