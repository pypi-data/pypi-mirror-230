import logging
import random
import string
from typing import Optional
from typing import Tuple

import flask
from flask import _app_ctx_stack
from flask import current_app
from flask import g
from flask import request
from py_zipkin import zipkin
from py_zipkin.zipkin import zipkin_span
from py_zipkin.util import ZipkinAttrs
from py_zipkin.util import create_attrs_for_span
from py_zipkin.util import generate_random_64bit_string
from py_zipkin.transport import SimpleHTTPTransport
from py_zipkin.encoding import Encoding

class hennry_zipkin_span(zipkin_span):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_current_context(self) -> Tuple[bool, Optional[ZipkinAttrs]]:
        """
        _get_current_context overrided by hennry

        Returns the current ZipkinAttrs and generates new ones if needed.

        :returns: (report_root_timestamp, zipkin_attrs)
        :rtype: (bool, ZipkinAttrs)
        """
        # This check is technically not necessary since only root spans will have
        # sample_rate, zipkin_attrs or a transport set. But it helps making the
        # code clearer by separating the logic for a root span from the one for a
        # child span.
        if self._is_local_root_span:

            # If sample_rate is set, we need to (re)generate a trace context.
            # If zipkin_attrs (trace context) were passed in as argument there are
            # 2 possibilities:
            # is_sampled = False --> we keep the same trace_id but re-roll the dice
            #                        for is_sampled.
            # is_sampled = True  --> we don't want to stop sampling halfway through
            #                        a sampled trace, so we do nothing.
            # If no zipkin_attrs were passed in, we generate new ones and start a
            # new trace.
            if self.sample_rate is not None:

                # If this trace is not sampled, we re-roll the dice.
                if (
                    self.zipkin_attrs_override
                    and not self.zipkin_attrs_override.is_sampled
                ):
                    # This will be the root span of the trace, so we should
                    # set timestamp and duration.
                    return (
                        True,
                        create_attrs_for_span(
                            sample_rate=self.sample_rate,
                            trace_id=self.zipkin_attrs_override.trace_id,
                        ),
                    )

                # If zipkin_attrs_override was not passed in, we simply generate
                # new zipkin_attrs to start a new trace.
                elif not self.zipkin_attrs_override:
                    return (
                        True,
                        create_attrs_for_span(
                            sample_rate=self.sample_rate,
                            use_128bit_trace_id=self.use_128bit_trace_id,
                        ),
                    )

            if self.firehose_handler and not self.zipkin_attrs_override:
                # If it has gotten here, the only thing that is
                # causing a trace is the firehose. So we force a trace
                # with sample rate of 0
                return (
                    True,
                    create_attrs_for_span(
                        sample_rate=0.0,
                        use_128bit_trace_id=self.use_128bit_trace_id,
                    ),
                )

            # If we arrive here it means the sample_rate was not set while
            # zipkin_attrs_override was, so let's simply return that.
            #return False, self.zipkin_attrs_override
            return True, self.zipkin_attrs_override

        else:
            # Check if there's already a trace context in _context_stack.
            existing_zipkin_attrs = self.get_tracer().get_zipkin_attrs()
            
            # If there's an existing context, let's create new zipkin_attrs
            # with that context as parent.
            if existing_zipkin_attrs:
                return (
                    False,
                    ZipkinAttrs(
                        trace_id=existing_zipkin_attrs.trace_id,
                        span_id=generate_random_64bit_string(),
                        parent_span_id=existing_zipkin_attrs.span_id,
                        flags=existing_zipkin_attrs.flags,
                        is_sampled=existing_zipkin_attrs.is_sampled,
                    ),
                )

        return False, None

class Zipkin(object):

    def _gen_random_id(self):
        return ''.join(
            random.choice(
                string.digits) for i in range(16))

    def __init__(self, app=None, sample_rate=100, timeout=1):
        self._exempt_views = set()
        self._sample_rate = sample_rate
        if app is not None:
            self.init_app(app)
        self._timeout = timeout
        self._zipkin_attrs = None

    def init_app(self, app):

        self.app = app
        
        if hasattr(app, 'before_request'):
            app.before_request(self._before_request)
        
        if hasattr(app, 'after_request'):
            app.after_request(self._after_request)
        
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self._teardown)
        else:
            app.teardown_request(self._teardown)

        self.zipkin_address = self.app.config.get('ZIPKIN_ADDRESS') \
            if self.app.config.get('ZIPKIN_ADDRESS') else ('localhost',9411)
        
        self._transport_handler = SimpleHTTPTransport(*self.zipkin_address)

        self._disable = app.config.get(
            'ZIPKIN_DISABLE', app.config.get('TESTING', False))

        return self

    def _should_use_token(self, view_func):
        return (view_func not in self._exempt_views)

    def _safe_headers(self, headers):
        
        self._headers = dict((k.lower(), v) for k, v in headers.__iter__())
        return self._headers

    def create_span(self, span_name, trace_id=None, parent_span_id=None, flags=None, is_sampled=False):

        self._zipkin_attrs = zipkin.ZipkinAttrs(
            trace_id=trace_id if trace_id else self._gen_random_id(),
            span_id=self._gen_random_id(),
            parent_span_id=parent_span_id,
            flags=flags,
            is_sampled=is_sampled,
        )
        
        span = hennry_zipkin_span(
            service_name=self.app.name,
            span_name=span_name,
            transport_handler=self._transport_handler,
            sample_rate=self._sample_rate,
            zipkin_attrs=self._zipkin_attrs
        )

        g._zipkin_span = span
        g._zipkin_span.start()

    def send_child_span(self, span_name):
        pass

    def get_zipkin_attrs(self):
        return self._zipkin_attrs
    
    def _before_request(self):

        if self._disable:
            return

        _app_ctx_stack.top._view_func = \
            current_app.view_functions.get(request.endpoint)

        if not self._should_use_token(_app_ctx_stack.top._view_func):
            return

        safe_headers = self._safe_headers(request.headers)

        parent_span_id = safe_headers.get('x-b3-spanid')
        trace_id = safe_headers.get('x-b3-traceid') or self._gen_random_id()

        is_sampled = str(safe_headers.get('x-b3-sampled') or '0') == '1'
        flags = safe_headers.get('x-b3-flags')

        self._zipkin_attrs = zipkin.ZipkinAttrs(
            trace_id=trace_id,
            span_id=self._gen_random_id(),
            parent_span_id=parent_span_id,
            flags=flags,
            is_sampled=is_sampled,
        )

        span = hennry_zipkin_span(
            service_name=self.app.name,
            span_name='rest.{0}.{1}'.format(request.endpoint, request.method),
            transport_handler=self._transport_handler,
            sample_rate=self._sample_rate,
            zipkin_attrs=self._zipkin_attrs
        )
        g._zipkin_span = span
        g._zipkin_span.start()

        self._zipkin_attrs = g._zipkin_span.zipkin_attrs
        
        self.update_tags(
            request_param=request.url,
            request_data=request.data
        )

    def exempt(self, view):
        view_location = '{0}.{1}'.format(view.__module__, view.__name__)
        self._exempt_views.add(view_location)
        return view

    def _after_request(self, response):

        if self._disable:
            return response
        if not hasattr(g, '_zipkin_span'):
            return response
        try:
            g._zipkin_span.stop()
                        
        except Exception as e:
          logging.warning('Unable to stop zipkin span:{}'.format(e))

        return response

    def _teardown(self, exception):

        if self._disable:
            return
        if not hasattr(g, '_zipkin_span'):
            return
        try:
            g._zipkin_span.stop()
                        
        except Exception as e:
          logging.warning('Unable to stop zipkin span:{}'.format(e))

        return

    def create_http_headers_for_new_span(self):
        if self._disable:
            return dict()
        return zipkin.create_http_headers_for_new_span(
            tracer = g._zipkin_span.get_tracer()
            )

    def logging(self, **kwargs):
        logging.warning('This method has been depreated, '
                        'please call `update_tags` instead.')
        self.update_tags(**kwargs)

    def update_tags(self, **kwargs):
        if all([hasattr(g, '_zipkin_span'),
                g._zipkin_span,
                g._zipkin_span.logging_context]):
            g._zipkin_span.logging_context.tags.update(kwargs)

def child_span(f):
    def decorated(*args, **kwargs):
        span = hennry_zipkin_span(
            service_name=flask.current_app.name,
            span_name=f.__name__,
        )
        #kwargs['span'] = span
        with span:
            val = f(*args, **kwargs)
            span.update_binary_annotations({
                'function_args': args,
                'function_returns': val,
            })
            return val

    return decorated

class child_zipkin_span(zipkin_span):

    def __init__(self, span_name: str):

        from . import zipkin

        if zipkin._disable:
            return

        """
        zipkin_attrs =  ZipkinAttrs(
                        trace_id      =zipkin.get_zipkin_attrs().trace_id,
                        span_id       =generate_random_64bit_string(),
                        parent_span_id=zipkin.get_zipkin_attrs().span_id,
                        #flags         =zipkin.get_zipkin_attrs().flags,
                        flags         =None,
                        #is_sampled    =zipkin.get_zipkin_attrs().is_sampled,
                        is_sampled=True,
                    )
        """
        kwargs = dict(
            service_name     =zipkin.app.name,
            span_name        =span_name,
            #transport_handler=zipkin._transport_handler,
            #transport_handler=SimpleHTTPTransport('localhost', 9411),
            #encoding=Encoding.V2_JSON,
            #zipkin_attrs     =zipkin_attrs,
        )

        super().__init__(**kwargs)

    def update_tags(self, **kwargs):

        """
        if self.logging_context:
            self.logging_context.tags.update(kwargs)
        else:
            tmp = dict(kwargs)
            self.update_binary_annotations(tmp)
        """
        self.update_binary_annotations(dict(kwargs))

    def create_http_headers_for_new_span(self):
        return zipkin.create_http_headers_for_new_span(
            tracer = self.get_tracer()
            )
