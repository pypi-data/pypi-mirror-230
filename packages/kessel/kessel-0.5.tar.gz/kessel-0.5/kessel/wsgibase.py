import sys
import os
import io
import logging
import datetime
from traceback import print_tb
from io import BufferedReader
from http import HTTPStatus
from urllib.parse import (
    SplitResult,
    urlunsplit,
    quote_plus,
)
from .request import Request
from .response import Redirect
from .headers import (
    Headers,
    get_file_headers,
    get_text_headers,
    send_http_status,
)
from .session import SessionService
from .urlmap import URLMap
from .helpers import (
    strip_query_of_next_page,
    get_next_page,
)

class WSGIBase:
    """WSGI compliant application class"""

    def __init__(self, err_log=None):

        self.err_log = err_log
        self.environ = None
        self.sitename = 'example.com'
        self.session_service = SessionService(self)
        self.urlmap = URLMap()


    def __call__(self, environ, start_response):
        """
        Arguments:
            wsgi Environment: dict()
            start_response: Callable with Arguments:
                status: str()
                response_headers: list(tuple(Name: str(), Value: str()))
        returns:
            response: bytes
        """

        try:
            self.environ = environ
            request = Request(self.environ)

            # TODO: refactor request passing -> app_context usage
            self.app_context.request = request

            # creates session, either new or from token
            self.session_service.check_authentication(request)

            #____everything from here on can assume a session____

            pspec, resource = self.urlmap.route_for_path(request.path)
            if early_result := self.pre_dispatch_checks(request,
                                                        pspec,
                                                        resource):
                status, headers, response = early_result
            else:
                # hit route
                status, headers, response = self.dispatch_request(request,
                                                                  pspec,
                                                                  resource)
            # login attaches the path of the requested restricted resource,
            # or 'next=/' to query, therefore we need to catch the redirect early
            if self.needs_after_login_redirect(request):
                status, headers, response = self.after_login_redirect(request)

            # attach session cookie
            self.attach_session_cookie(headers)

            # pop request
            self.app_context.request = None

            start_response(status, headers.to_wsgi_list())
        except Exception as e:
            status, headers, response, exc_info = self.handle_exception(e)
            start_response(status, headers, exc_info)

        return response

    def handle_exception(self, e):

        s, h, r = send_http_status(HTTPStatus.INTERNAL_SERVER_ERROR)
        exc, val, tr = sys.exc_info()
        self.err_log.exception(f"{exc}, {e}")
        self.err_log.exception(f"{print_tb(tr)}")

        return s, h, [str(s).encode('utf-8')], str(exc).encode('utf-8')

    def pre_dispatch_checks(self, request, pspec, resource):
        # 404
        # TODO: Custom Error pages
        if pspec is None:
            return send_http_status(HTTPStatus.NOT_FOUND)
        # 405
        if not request.method in resource.methods:
            return send_http_status(HTTPStatus.METHOD_NOT_ALLOWED)


        # authorisation
        if self.needs_authorisation(request, resource):
            # no user logged in
            if self.session_service.user is None:
                return self.redirect_to_login(request)
            # insufficient access rights
            if not self.session_service.check_authorisation(resource):
                return send_http_status(HTTPStatus.FORBIDDEN,
                                        'Authorisation failed: No access rights.')

        # csrf protection
        if request.method in ['POST', 'PUT', 'DELETE']:
            if not self.session_service.check_csrf(request):
                return send_http_status(HTTPStatus.FORBIDDEN,
                                        'CSRF failed: Token missing or incorrect.')

    def dispatch_request(self, request, pspec, resource):

        if groups := pspec.groups(request.path):
            group_values = [v for v in groups.values()]
            response = resource.view_fn(request, *group_values)
        else:
            response = resource.view_fn(request)

        if isinstance(response, Redirect):
            return self.redirect_to_route(response.request,
                                          response.route,
                                          response.status_code)

        return self.finalize_response(response, request)

    def finalize_response(self, response, request):

        if isinstance(response, tuple) and isinstance(response[0], int):
            status = f'{response[0]}'
            response = response[1]
        else:
            s = HTTPStatus.OK
            status = f'{s.value} {s.phrase}'

        # set header based on response type
        if isinstance(response, str):
            encoded = response.encode('utf-8')
            headers = get_text_headers(encoded)

            return status, headers, [encoded]

        elif isinstance(response, BufferedReader):
            headers = get_file_headers(request, response)

            return status, headers, response

        else:
            try:
                encoded = str(response).encode('utf-8')
                headers = get_text_headers(encoded)

                return status, headers, [encoded]
            except Exception:
                raise

    def needs_authorisation(self, request, resource):
        if resource.roles and request.path != self.session_service.login_route:
            return True
        return False

    def redirect_to_login(self, request):

        request.query = (f"next={request.path}",)

        return self.redirect_to_route(request, self.session_service.login_route)

    def redirect_to_route(self, request, route, status_code=307):

        u = SplitResult(scheme=request.scheme,
                        netloc=request.host,
                        path=f"{route}",
                        query='&'.join(request.query),
                        fragment="")
        newpath = urlunsplit(u)

        headers = Headers()
        headers.add("Location", f"{newpath}")
        headers.add("Content-Length", '0')
        headers.add("Cache-Control", "no-store")

        # 307 reuses method and body of request
        # TODO: return discards body. refactor to ensure compliance
        if status_code == 307:
            s = HTTPStatus.TEMPORARY_REDIRECT
        # 303 indicates change of resource and always changes method to GET
        elif status_code == 303:
            s = HTTPStatus.SEE_OTHER

        status = f"{s.value} {s.phrase}"

        return status, headers, b''

    def attach_session_cookie(self, headers):
        """final preparation for next round trip. after headers are
        set, user and session must be invalidated."""

        if self.session_service.session: # not set for 404
            headers.add('Set-Cookie', self.session_service.session_cookie())

        self.session_service.reset_session()
        self.session_service.reset_user()

    def needs_after_login_redirect(self, request):

        # user present and '?next=' query set

        if self.session_service.user and get_next_page(request.query):
            return True
        return False

    def after_login_redirect(self, request):

        next_page = get_next_page(request.query)
        request.query = strip_query_of_next_page(request.query)

        return self.redirect_to_route(request, next_page, status_code=303)
