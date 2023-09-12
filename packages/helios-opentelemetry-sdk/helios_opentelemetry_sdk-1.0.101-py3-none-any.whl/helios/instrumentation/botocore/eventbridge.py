import json

from opentelemetry.propagate import inject
from opentelemetry.propagators import textmap
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import set_span_in_context

from helios.instrumentation.botocore.consts import AwsAttribute, AwsService, AwsOperation


class EventBridgeContextSetter(textmap.Setter):
    def set(self, carrier: textmap.CarrierT, key: str, value: str) -> None:
        if type(carrier) == dict and key and value:
            carrier[key] = value


class EventBridgeInstrumentor(object):
    def __init__(self):
        pass

    def request_hook(self, span, operation_name, api_params):
        if api_params is None:
            return

        if operation_name.lower() != 'putevents':
            return

        entries = api_params.get('Entries')
        for entry in entries:
            try:
                detail_str = entry.get('Detail')
                if detail_str:
                    detail = json.loads(detail_str)
                    detail['headers'] = {} if not detail.get('headers', None) else None
                    headers = detail['headers']
                    inject(headers, context=set_span_in_context(span), setter=EventBridgeContextSetter())
                    entry['Detail'] = json.dumps(detail, default=str)
            except:  # noqa: E722 Do not use bare except
                pass

        attributes = {
            SpanAttributes.MESSAGING_SYSTEM: AwsService.EVENT_BRIDGE,
            SpanAttributes.MESSAGING_OPERATION: AwsOperation.SEND,
            AwsAttribute.MESSAGING_PAYLOAD: json.dumps(entries, default=str),
        }
        attributes = {k: v for k, v in attributes.items() if v is not None}
        span.set_attributes(attributes)

    def response_hook(self, span, operation_name, result):
        pass
