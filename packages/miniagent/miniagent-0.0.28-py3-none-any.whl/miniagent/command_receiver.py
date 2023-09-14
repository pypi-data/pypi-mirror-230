import json
import requests
import threading
import logging
from time import sleep
from polling2 import *
from .executer import ExecuterCaller
from .common import get_callable_object

class CommandsReceiver:

    def __init__(self, url: str, event: threading.Event) -> None:
        self.event = event
        self._start_polling(url)

    def get_thread(self):
        return self.thread
    
    def _get_response(self, response):
        return response.status_code == 200

    def _polling(self, url):

        while True:

            if self.event.is_set():
                break

            try:
                result = poll(lambda: requests.get(url), 
                                step=10, 
                                poll_forever=True,
                                check_success=self._get_response)
            except requests.exceptions.ConnectionError as e:
                logging.error("{} is not connected.".format(url))
                sleep(10)
                continue
            
            try:
                result_dict = json.loads(result.text)
            except json.decoder.JSONDecodeError as e:
                logging.error("The result is not JSON parsable. result.text\
                               : {}".format(result.text))
                continue

            from . import app, zipkin, configure
            with app.app_context():

                if zipkin:

                    header = result.headers
                    trace_id = header.get('x-b3-traceid')
                    parent_span_id = header.get('x-b3-spanid')

                    if header.get('is_sampled') and (header['is_sampled'] in ['1', 'True']\
                        or header['is_sampled']==True):
                        is_sampled = True
                    else:
                        is_sampled = False

                    zipkin.create_span('command_receiver.url='+ url,
                                        trace_id = trace_id,
                                        parent_span_id = parent_span_id,
                                        is_sampled = is_sampled,
                                      )

                callback = None
                if configure.get('COMMANDER_RESPONSE_CONVERTER'):
                    function_path = configure.get('COMMANDER_RESPONSE_CONVERTER')
                    callback = get_callable_object(function_path)

                rtn, comment = ExecuterCaller.instance().execute_command(result_dict, callback)

                if zipkin:
                    zipkin.update_tags(
                        param  = result_dict,
                        result = comment,
                        )

    def _start_polling(self, url):

        self.thread = threading.Thread(target=self._polling, args=(url,))
        self.thread.name = '_polling'
        self.thread.start()
        #self.thread.join()