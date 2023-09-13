import email
import html
from kessel.session import parse_cookies
from kessel.headers import make_headers_from_environ
from kessel.helpers import (
    get_host_from_environ,
    urlencoded_safe_string,
    make_multipart_message,
    get_urlencoded_data,
    get_multipart_data,
)


class Request:

    def __init__(self, environ):

        self.environ = environ
        self.charset = "utf-8"
        self.method = environ.get("REQUEST_METHOD",  "GET")
        self.scheme = environ.get("wsgi.url_scheme", "http")
        self.root_path = environ.get("SCRIPT_NAME", "")
        self.path = environ.get("PATH_INFO", "")
        self.query = environ.get("QUERY_STRING", ""),
        self.headers = make_headers_from_environ(self.environ)
        self.remote_addr = environ.get("REMOTE_ADDR")
        self.host = get_host_from_environ(self.environ)
        self.data = self.get_data()
        self.form = self.extract_form_data()
        self.cookies = parse_cookies(self.headers.get("Cookie"))

    def _load_data(self):
        """since wsgi.input MUST be present following PEP3333,
        we can always assume it"""
        return self.environ.get("wsgi.input")


    def _get_content_length(self):

        c_len = self.environ.get('CONTENT_LENGTH')
        if c_len is not None:
            try:
                return max(0, int(c_len))
            except (ValueError, TypeError):
                pass
        return None

    def get_data(self):

        stream = self._load_data()
        c_len = self._get_content_length()

        # A wsgi extension that tells us if the input is terminated.  In
        # that case we return the stream unchanged as we know we can safely
        # read it until the end.
        if self.environ.get("wsgi.input_terminated"):
            return stream.read()

        elif c_len is not None:
            return stream.read(c_len)

    def extract_form_data(self):

        form = dict()
        if self.data is not None:
            c_type_header = self.headers.get("content-type")
            charset = self.headers.get("charset")
            if c_type_header is not None:
                ct = c_type_header.split('; ')
                if 'application/x-www-form-urlencoded' in ct:
                    _form_str = self.data.decode(
                        charset if charset else'utf-8')
                    data = get_urlencoded_data(_form_str)
                    form.update(data)

                elif 'multipart/form-data' in ct:
                    _form_str = self.data.decode(
                        charset if charset else'utf-8')
                    msg = make_multipart_message(c_type_header, _form_str)
                    if msg is not None:
                        data = get_multipart_data(msg)
                        form.update(data)
        return form
