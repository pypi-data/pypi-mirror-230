from logging import getLogger

from wrapt import wrap_function_wrapper
from opentelemetry.propagate import extract
from opentelemetry.context import attach, detach, get_current
from opentelemetry.trace import get_tracer_provider, set_span_in_context
from opentelemetry.semconv.trace import (
    MessagingOperationValues,
)

from helios.instrumentation.base import HeliosBaseInstrumentor

_LOG = getLogger(__name__)


def _is_robust_channel(channel):
    return channel.__class__.__name__ == 'RobustChannel' and hasattr(channel, 'channel')


class HeliosAioPikaInstrumentor(HeliosBaseInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.aio_pika'
    INSTRUMENTOR_NAME = 'AioPikaInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None, **kwargs):
        if self.get_instrumentor() is None:
            return

        def wrap_set_channel(wrapped, instance, args, kwargs):
            if len(args) == 1 and _is_robust_channel(args[0]):
                return wrapped(args[0].channel)  # Unwrap the internal channel, happens in v9 of aio-pika
            return wrapped(*args, **kwargs)

        wrap_function_wrapper(self.MODULE_NAME + ".span_builder", 'SpanBuilder.set_channel', wrap_set_channel)

        self.get_instrumentor().instrument(tracer_provider=tracer_provider)


class AioPikaMessageContext:
    def __init__(self, message, queue=None):
        self._message = message
        self._queue = queue
        self._span = None
        self._token = None

    def __enter__(self):
        from opentelemetry.instrumentation import aio_pika
        from opentelemetry.instrumentation.aio_pika.span_builder import SpanBuilder

        headers = self._message.headers or {}
        ctx = extract(headers)
        if not ctx:
            ctx = get_current()

        tracer = get_tracer_provider().get_tracer(aio_pika.__name__)
        builder = SpanBuilder(tracer)
        builder.set_as_consumer()
        builder.set_operation(MessagingOperationValues.RECEIVE)
        builder.set_destination(self._message.exchange or self._message.routing_key)
        if self._queue:
            channel = self._queue.channel
            if _is_robust_channel(channel):
                channel = channel.channel
            builder.set_channel(channel)
        builder.set_message(self._message)
        token = attach(ctx)
        try:
            span = builder.build()
        finally:
            detach(token)

        if not span or not span.is_recording():
            return

        self._span = span
        self._token = attach(set_span_in_context(self._span))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._span is not None:
            self._span.end()

        if self._token is not None:
            detach(self._token)
