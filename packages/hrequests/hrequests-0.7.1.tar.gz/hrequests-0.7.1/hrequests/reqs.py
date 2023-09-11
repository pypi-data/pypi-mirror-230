import traceback
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import wait as futures_wait
from functools import partial
from threading import Thread
from typing import Dict, Iterable, Optional, Union, overload
from urllib.parse import urlencode

import gevent
from gevent.pool import Pool

import hrequests
from hrequests.response import Response


class TLSRequest:
    '''
    Asynchronous request.
    Accepts the same parameters as ``TLSSession.request`` and some additional parameters:

    Args:
        method (str): Request method.
        url (str): URL to request.
        session (hrequests.session.TLSSession, optional): Associated `TLSSession`. Defaults to None.
        raise_exception (bool, optional): Raise exceptions (default FALSE for async, TRUE for sync). Defaults to False.
        params (Dict[str, str], optional): Parameters to pass to request. Defaults to None.
        callback (function, optional): Callback called on response. Same as passing ``hooks={'response': callback}``. Defaults to None.

    Attributes:
        method (str): Request method.
        raise_exception (bool): Raise exceptions (default FALSE for async, TRUE for sync).
        url (str): URL to request.
        session (hrequests.session.TLSSession): Associated `TLSSession`.
        kwargs (dict): The rest arguments for ``Session.request``.
        response (hrequests.response.Response): Resulting ``Response``.

    Methods:
        send(**kwargs): Prepares request based on parameter passed to constructor and optional ``kwargs```.
                        Then sends request and saves response to :attr:`response`.
                        Returns: ``Response``.
    '''

    session_kwargs = {
        'browser',
        'version',
        'os',
        'ja3_string',
        'h2_settings',
        'additional_decode',
        'pseudo_header_order',
        'priority_frames',
        'header_order',
        'force_http1',
        'catch_panics',
        'debug',
    }

    def __init__(
        self,
        method: str,
        url: str,
        session: Optional['hrequests.session.TLSSession'] = None,
        params: Optional[Dict[str, str]] = None,
        raise_exception: bool = True,
        **kwargs,
    ):
        # Request method
        self.method: str = method
        # Raise exceptions (default FALSE for async, TRUE for sync)
        self.raise_exception: bool = raise_exception
        # URL to request
        if params is None:
            self.url: str = url
        else:
            self.url: str = f'{url}?{urlencode(params, doseq=True)}'

        # Session kwargs
        self.sess_kwargs: Optional[dict] = None
        if kwargs:
            sess_kwargs = set(kwargs.keys()) & TLSRequest.session_kwargs
            if session and sess_kwargs:
                # If session is already provided, raise TypeError if session-only kwargs are passed
                raise TypeError(f'Cannot pass parameter(s) to an existing session: {sess_kwargs}')
            else:
                self.sess_kwargs = {k: kwargs.pop(k) for k in sess_kwargs}

        if callback := kwargs.pop('callback', None):
            kwargs['hooks'] = {'response': callback}

        # The rest of the arguments for `Session.request`
        self.kwargs = kwargs
        # Resulting Response
        self.response = None
        # Create TLSSession if not provided
        self._build_session(session)

    def _build_session(self, session=None):
        if session is None:
            if self.sess_kwargs:
                # if session kwargs are passed, configure a new session with them
                self.session = hrequests.Session(temp=True, **self.sess_kwargs)
            else:
                # else use a preconfigured session
                self.session = hrequests.chrome.Session(temp=True)
            self._close = True
        else:
            # don't close adapters after each request if the user provided the session
            self.session = session
            self._close = False

    def send(self, **kwargs):
        '''
        Prepares request based on parameter passed to constructor and optional ``kwargs```.
        Then sends request and saves response to :attr:`response`
        :returns: ``Response``
        '''
        merged_kwargs = {}
        merged_kwargs.update(self.kwargs)
        merged_kwargs.update(kwargs)
        # rebuild session if it was deleted
        if self.session is None:
            self._build_session()
        try:
            self.response = self.session.request(self.method, self.url, **merged_kwargs)
        except Exception as e:
            if self.raise_exception:
                raise e
            self.exception = e
            self.traceback = traceback.format_exc()
        finally:
            if self._close and self.session is not None:
                # close the session if it was created by this request
                self.session.close()
                self.session = None
        return self


class LazyTLSRequest(TLSRequest):
    '''
    This will send the request immediately, but doesn't wait for the response to be ready
    until an attribute of the response is accessed
    '''

    def __init__(self, *args, **kwargs):
        executor: Optional[ThreadPoolExecutor] = kwargs.pop('executor', None)
        super().__init__(*args, **kwargs)

        self._thread: Union[Thread, Future]
        if executor:
            self._thread = executor.submit(self._send)
        else:
            self._thread = Thread(target=self._send)
            self._thread.start()
        self.complete: bool = False

    def __repr__(self):
        return self.response.__repr__() if self.complete else '<LazyResponse[Pending]>'

    def _send(self):
        super().send()
        self.complete = True

    def join(self):
        if isinstance(self._thread, Future):
            # await future to be ready
            futures_wait((self._thread,))
        else:
            # await thread to be ready
            self._thread.join()

    def __getattr__(self, name: str):
        # if an attribute is called, JOIN the greenlet and continue
        if not self.complete:
            self.join()
        return getattr(self.response, name)


def request_list(
    method: str, url: Iterable[str], *args, **kwargs
) -> Iterable[Union[Response, LazyTLSRequest]]:
    '''
    Concurrently send requests given a list of urls
    '''
    # if wait is False, return a tuple of LazyTLSRequests
    if kwargs.pop('nohup', None):
        executor = ThreadPoolExecutor()
        # return a list of LazyTLSRequests objs
        return [
            LazyTLSRequest(method, u, *args, **kwargs, executor=executor, raise_exception=False)
            for u in url
        ]
    # send requests to urls concurrently with map
    return map([async_request(method, u, *args, **kwargs) for u in url])


@overload
def request(
    method: str, url: Iterable[str], *args, **kwargs
) -> Iterable[Union[Response, LazyTLSRequest]]:
    ...


@overload
def request(method: str, url: str, *args, **kwargs) -> Union[Response, LazyTLSRequest]:
    ...


def request(method: str, url: Union[str, Iterable[str]], *args, **kwargs):
    '''
    Send a request with TLS client

    Args:
        method (str): Method of request (GET, POST, OPTIONS, HEAD, PUT, PATCH, DELETE)
        url (Union[str, Iterable[str]]): URL or list of URLs to request.
        params (dict, optional): Dictionary of URL parameters to append to the URL. Defaults to None.
        data (Union[str, dict], optional): Data to send to request. Defaults to None.
        headers (dict, optional): Dictionary of HTTP headers to send with the request. Defaults to None.
        cookies (Union[dict, RequestsCookieJar], optional): Dict or CookieJar to send. Defaults to None.
        json (dict, optional): Json to send in the request body. Defaults to None.
        allow_redirects (bool, optional): Allow request to redirect. Defaults to True.
        verify (bool, optional): Verify the server's TLS certificate. Defaults to True.
        timeout (int, optional): Timeout in seconds. Defaults to 30.
        proxies (dict, optional): Dictionary of proxies. Defaults to None.
        wait (bool, optional): Wait for response to be ready. Defaults to True.
        threadsafe (bool, optional): Threadsafe support for wait=False. Defaults to False.

    Returns:
        hrequests.response.Response: Response object
    '''
    # if a list of urls is passed, send requests concurrently
    if isinstance(url, (list, tuple)):
        return request_list(method, url, *args, **kwargs)
    # if nohup is True, return a LazyTLSRequest
    if kwargs.pop('nohup', None):
        return LazyTLSRequest(method, url, *args, **kwargs)
    req = TLSRequest(method, url, *args, **kwargs)
    req.send()
    return req.response


def async_request(*args, **kwargs) -> TLSRequest:
    '''
    Return an unsent request to be used with map, imap, and imap_enum.
    Used to send requests concurrently.

    Args:
        method (str): Method of request (GET, POST, OPTIONS, HEAD, PUT, PATCH, DELETE)
        url (str): URL to send request to
        params (dict, optional): Dictionary of URL parameters to append to the URL. Defaults to None.
        data (Union[str, dict], optional): Data to send to request. Defaults to None.
        headers (dict, optional): Dictionary of HTTP headers to send with the request. Defaults to None.
        cookies (Union[dict, RequestsCookieJar], optional): Dict or CookieJar to send. Defaults to None.
        json (dict, optional): Json to send in the request body. Defaults to None.
        allow_redirects (bool, optional): Allow request to redirect. Defaults to True.
        verify (bool, optional): Verify the server's TLS certificate. Defaults to True.
        timeout (int, optional): Timeout in seconds. Defaults to 30.
        proxies (dict, optional): Dictionary of proxies. Defaults to None.

    Returns:
        TLSRequest: Unsent request object
    '''
    return TLSRequest(*args, **kwargs, raise_exception=False)


'''
Requests shortcuts
'''

# Shortcuts for creating synchronous requests
get: partial = partial(request, 'GET')
options: partial = partial(request, 'OPTIONS')
head: partial = partial(request, 'HEAD')
post: partial = partial(request, 'POST')
put: partial = partial(request, 'PUT')
patch: partial = partial(request, 'PATCH')
delete: partial = partial(request, 'DELETE')

'''
Asynchronous requests shortcuts
'''

# Shortcuts for creating an unsent TLSRequest
async_get: partial = partial(async_request, 'GET')
async_post: partial = partial(async_request, 'POST')
async_options: partial = partial(async_request, 'OPTIONS')
async_head: partial = partial(async_request, 'HEAD')
async_put: partial = partial(async_request, 'PUT')
async_patch: partial = partial(async_request, 'PATCH')
async_delete: partial = partial(async_request, 'DELETE')


def send(r, pool: Optional[Pool] = None):
    '''
    Sends the request object using the specified pool. If a pool isn't
    specified this method blocks. Pools are useful because you can specify size
    and can hence limit concurrency.
    '''
    return gevent.spawn(r.send) if pool is None else pool.spawn(r.send)


def map(requests, size=None, exception_handler=None, timeout=None):
    '''
    Concurrently converts a list of Requests to Responses.

    Parameters:
        requests - a collection of Request objects.
        size - Specifies the number of requests to make at a time. If None, no throttling occurs.
        exception_handler - Callback function, called when exception occurred. Params: Request, Exception
        timeout - Gevent joinall timeout in seconds. (Note: unrelated to requests timeout)

    Returns:
        A list of Response objects.
    '''

    requests = list(requests)
    if size is None:
        size = len(requests)

    pool = Pool(size)
    jobs = [send(r, pool) for r in requests]
    gevent.joinall(jobs, timeout=timeout)

    ret = []

    for request in requests:
        if request.response is not None:
            ret.append(request.response)
        elif exception_handler and hasattr(request, 'exception'):
            ret.append(exception_handler(request, request.exception))
        elif exception_handler:
            ret.append(exception_handler(request, None))
        else:
            ret.append(None)

    return ret


def imap(requests, size=2, enumerate=False, exception_handler=None):
    '''
    Concurrently converts a generator object of Requests to a generator of Responses.

    Parameters:
        requests - a generator or sequence of Request objects.
        size - Specifies the number of requests to make at a time. default is 2
        exception_handler - Callback function, called when exception occurred. Params: Request, Exception

    Yields:
        Response objects.
    '''
    if enumerate:  # send to imap_enum
        return imap_enum(requests, size, exception_handler)

    def send(r):
        return r.send()

    pool = Pool(size)
    for request in pool.imap_unordered(send, requests):
        if request.response is not None:
            yield request.response
        elif exception_handler:
            ex_result = exception_handler(request, request.exception)
            if ex_result is not None:
                yield ex_result

    pool.join()


def imap_enum(requests, size=2, exception_handler=None):
    '''
    Like imap, but yields tuple of original request index and response object
    Unlike imap, failed results and responses from exception handlers that return None are not ignored. Instead, a
    tuple of (index, None) is yielded.
    Responses are still in arbitrary order.

    Parameters:
        requests - a sequence of Request objects.
        size - Specifies the number of requests to make at a time. default is 2
        exception_handler - Callback function, called when exception occurred. Params: Request, Exception

    Yields:
        (index, Response) tuples.
    '''

    def send(r):
        return r._index, r.send()

    requests = list(requests)
    for index, req in enumerate(requests):
        req._index = index

    pool = Pool(size)
    for index, request in pool.imap_unordered(send, requests):
        if request.response is not None:
            yield index, request.response
        elif exception_handler:
            ex_result = exception_handler(request, request.exception)
            yield index, ex_result
        else:
            yield index, None
