from .. import configure
from ..adapter import Adapter
from ..message_sender import TracingKafkaProducer

class KafkaProducerAdapter(Adapter):

    producer = None

    def __init__(self):
        self.producer = TracingKafkaProducer(bootstrap_servers=configure['KAFKA_BOOTSTRAP_SERVERS'])

    def produce_message(self, topic: str, message: dict) -> tuple[int, dict]:
        self.producer.send(topic, message)
        return 1, {'message':message}
    
    def __del__(self):
        try:
            self.producer.close()
        except Exception as e:
            pass

    def get_status(self) -> int:
        return 1