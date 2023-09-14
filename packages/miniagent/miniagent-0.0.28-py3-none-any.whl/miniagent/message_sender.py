from kafka import KafkaProducer
import json
from . import configure
from .flask_zipkin import child_zipkin_span

class TracingKafkaProducer(KafkaProducer):

    def __init__(self, *args, **kwargs):

        if not kwargs.get('bootstrap_servers'):
            kwargs.update(dict(
                bootstrap_servers=configure['KAFKA_BOOTSTRAP_SERVERS']
            ))
        super().__init__(*args, **kwargs)

    def send(self, topic, value=None, key=None, headers=None, partition=None, timestamp_ms=None):

        with child_zipkin_span('kafka_producer.topic='+topic) as span:
            header = dict(
                        trace_id = span.zipkin_attrs.trace_id,
                        span_id = span.zipkin_attrs.span_id,
                        parent_span_id = span.zipkin_attrs.parent_span_id,
                        flags = span.zipkin_attrs.flags,
                        is_sampled = span.zipkin_attrs.is_sampled
                    )
            
            value.update({'header':header})
            span.update_tags(
                message=value
            )
            return super().send(topic, value=json.dumps(value).encode('utf-8'), key=key,\
                                headers=headers, partition=partition, timestamp_ms=timestamp_ms)
