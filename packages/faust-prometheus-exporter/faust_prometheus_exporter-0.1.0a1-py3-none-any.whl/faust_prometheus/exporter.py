import faust
from faust.web import Request
from prometheus_client import REGISTRY, CollectorRegistry, Gauge
from prometheus_client.exposition import choose_encoder

_MAX_AVG_HISTORY = Gauge('max_avg_history', 'Max number of total run time values to keep to build average')
_MAX_COMMIT_LATENCY_HISTORY = Gauge('max_commit_latency_history', 'Max number of commit latency numbers to keep')
_MAX_SEND_LATENCY_HISTORY = Gauge('max_send_latency_history', 'Max number of send latency numbers to keep')
_MAX_ASSIGNMENT_LATENCY_HISTORY = Gauge(
    'max_assignment_latency_history', 'Max number of assignment latency numbers to keep'
)
_MESSAGES_ACTIVE = Gauge('messages_active', 'Number of messages currently being processed')
_MESSAGES_RECEIVED = Gauge('messages_received', 'Number of messages processed in total')
_MESSAGES_RECEIVED_BY_TOPIC = Gauge('messages_received_BY_TOPIC', 'Number of messages processed in total', ['topic'])


_MESSAGES_S_METRIC = Gauge('messages_s', 'Number of messages being processed this second.')
_MESSAGES_SENT_METRIC = Gauge('messages_sent', 'Number of messages sent in total.')
_MESSAGES_SENT_BY_TOPIC = Gauge('messages_sent_by_topic', 'Number of messages sent in total by topic', ['topic'])


class FaustPrometheusExporter(object):
    faust_app: faust.App
    registry: CollectorRegistry

    def __init__(self, faust_app: faust.App, registry: CollectorRegistry = REGISTRY) -> None:
        self.faust_app = faust_app
        self.registry = registry

        self.faust_app.page('/metrics')(self._url_metrics_handler)

        self._metrics = [
            _MAX_AVG_HISTORY,
            _MAX_COMMIT_LATENCY_HISTORY,
            _MAX_SEND_LATENCY_HISTORY,
            _MAX_ASSIGNMENT_LATENCY_HISTORY,
            _MESSAGES_ACTIVE,
            _MESSAGES_RECEIVED,
        ]

        if registry is not REGISTRY:
            for metric in self._metrics:
                self.registry.register(metric)

    def _update_registry(self):
        m = self.faust_app.monitor

        _MAX_AVG_HISTORY.set(m.max_avg_history)
        _MAX_COMMIT_LATENCY_HISTORY.set(m.max_commit_latency_history)
        _MAX_SEND_LATENCY_HISTORY.set(m.max_send_latency_history)
        _MAX_ASSIGNMENT_LATENCY_HISTORY.set(m.max_assignment_latency_history)
        _MESSAGES_ACTIVE.set(m.messages_active)
        _MESSAGES_RECEIVED.set(m.messages_received_total)
        _MESSAGES_S_METRIC.set(m.messages_s)
        _MESSAGES_SENT_METRIC.set(m.messages_sent)

        for topic, value in m.messages_sent_by_topic.items():
            _MESSAGES_SENT_BY_TOPIC.labels(topic=topic).set(value)

        for topic, value in m.messages_received_by_topic.items():
            _MESSAGES_RECEIVED_BY_TOPIC.labels(topic=topic).set(value)

        # TODO: Выглядит плохо. не все поля.

    async def _url_metrics_handler(self, request: Request):
        self._update_registry()

        accept_header = request.headers.get('Accept')
        request.headers.get('Accept-Encoding')
        encoder, content_type = choose_encoder(accept_header)
        response = self.faust_app.web.bytes(encoder(self.registry))
        response.content_type = content_type
        return response
