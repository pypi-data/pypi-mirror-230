from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import json
import logging
import threading
from time import sleep

from .executer import ExecuterCaller
from .common import intersect

class MessageReceiver:

    def __init__(self, 
                 bootstrap_servers: list, 
                 group_id: str, 
                 executers_by_topic: list, 
                 agent_roles: list,
                 event: threading.Event) -> None:

        self.event = event
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer = None

        self.topics, self.executers = \
            self._parse_config(executers_by_topic, agent_roles)

        if not self.topics:
            logging.warning('There is no topic to consume.')
            return

        try:
            consumer = KafkaConsumer(
                                bootstrap_servers=bootstrap_servers,
                                auto_offset_reset='earliest',
                                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                                group_id=group_id,
                                max_poll_records=1,
                            )
            self.consumer = consumer
        except NoBrokersAvailable as e:
            logging.warning('No Kafka Brokers Available.')
            pass
        except ValueError as e:
            logging.warning('ValueError : ' + e.__str__())
            pass
        
        #self.topics = list(map(lambda x: x[0], executers_by_topic.items()))
        #self.executers = executers_by_topic
        #self.consumer.subscribe(self.topics)

        self._start_polling()

    def get_thread(self):
        return self.thread

    def _parse_config(self, executers_by_topic:list, agent_roles:list):

        topics = []
        executers = {}

        for t in executers_by_topic:

            if t.get('agent_roles') \
                and not intersect(agent_roles, t.get('agent_roles')):
                continue

            topics.append(t['topic'])
            executers[t['topic']] = t['executer']
        
        return topics, executers
    
    def _get_consumer_handle(self):
        try:
            consumer = KafkaConsumer(
                                bootstrap_servers=self.bootstrap_servers,
                                auto_offset_reset='earliest',
                                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                                group_id=self.group_id,
                            )
        except NoBrokersAvailable as e:
            logging.warning('No Kafka Brokers Available.')
            return None
        except ValueError as e:
            logging.warning('ValueError : ' + e.__str__())
            return None
        
        logging.info('KafkaConsumer is alive.')

        return consumer        

    def _polling(self):

        while not self.consumer:
            self.consumer = self._get_consumer_handle()
            sleep(10)
        
        self.consumer.subscribe(self.topics)

        while True:

            if self.event.is_set():
                logging.warning('MessageReceiver is broken.')
                break

            try:
                results = self.consumer.poll(10.0)
            except Exception as e:
                sleep(10)
                continue

            if not results:
                sleep(5)
            
            for topic_partition, messages in results.items():
                for message in messages:
                    result_dict = self.parse_message(topic_partition.topic, message.value)

                    from . import app, zipkin
                    with app.app_context():

                        if zipkin:

                            header = result_dict['header']
                            trace_id = header.get('trace_id')
                            parent_span_id = header.get('span_id')

                            if header.get('is_sampled') and (header['is_sampled'] in ['1', 'True']\
                                  or header['is_sampled']==True):
                                is_sampled = True
                            else:
                                is_sampled = False

                            zipkin.create_span('Kafka_consumer.topic='+ topic_partition.topic,
                                               trace_id = trace_id,
                                               parent_span_id = parent_span_id,
                                               is_sampled = is_sampled,
                                               )
                            zipkin.update_tags(param=message.value)

                        rtn, comment = ExecuterCaller.instance().execute_command(result_dict)

                        if zipkin:
                            zipkin.update_tags(
                                param  = message.value,
                                result = comment,
                                )

    def _start_polling(self):

        self.thread = threading.Thread(target=self._polling)
        self.thread.name = '_kafka_consumer'
        self.thread.start()

    def parse_message(self, topic: str, message: dict):
        
        header = message.pop('header') if message.get('header') else {}

        result_dict =\
            dict(
                executer = self.executers[topic],
                initial_param = message,
                header = header
            )
        
        return result_dict
    
    def __del__(self):
        #if self.consumer:
        #    self.consumer.close()
        try:
            self.consumer.close()
        except Exception as e:
            pass