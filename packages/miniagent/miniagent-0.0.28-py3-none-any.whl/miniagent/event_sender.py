import requests
from .flask_zipkin import child_zipkin_span

def _set_header(span:child_zipkin_span, kwargs: dict):

    def bool2str(isval):
        if isval==None:
            return 'none'
        elif isval:
            return '1'
        else:
            return '0'

    zipkin_header = {
        'x-b3-parentspanid':span.zipkin_attrs.parent_span_id,
        'x-b3-traceid':span.zipkin_attrs.trace_id,
        'x-b3-spanid':span.zipkin_attrs.span_id,
        'x-b3-sampled':bool2str(span.zipkin_attrs.is_sampled),
        'x-b3-flags':bool2str(span.zipkin_attrs.flags),
    }

    if kwargs.get('headers'):
        headers = kwargs['headers'].copy()
        headers.update(zipkin_header)
    else:
        headers = zipkin_header

    kwargs.update({'headers':headers})
    return kwargs

def get(url, params=None, **kwargs):

    with child_zipkin_span('reqeust_get.url='+url) as span:
        span.update_tags(params=params)
        return requests.get(url, params=params, **_set_header(span, kwargs))

def post(url, data=None, json=None, **kwargs):

    with child_zipkin_span('reqeust_post.url='+url) as span:
        span.update_tags(data=data, json=json)
        return requests.post(url, data=data, json=json, **_set_header(span, kwargs))

def put(url, data=None, json=None, **kwargs):

    with child_zipkin_span('reqeust_put.url='+url) as span:
        span.update_tags(data=data, json=json)
        return requests.put(url, data=data, json=json, **_set_header(span, kwargs))

def delete(url, params=None, **kwargs):

    with child_zipkin_span('reqeust_delete.url='+url) as span:
        span.update_tags(params=params)
        return requests.delete(url, params=params, **_set_header(span, kwargs))
