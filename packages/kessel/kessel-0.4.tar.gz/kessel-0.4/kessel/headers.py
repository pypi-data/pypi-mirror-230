import os
import email
import datetime

from kessel.helpers import (
    decode_value,
    dump_options_header,
    to_header_string,
    guess_type,
    date_time_string,
)

def make_headers_from_environ(environ):

    h = Headers()
    h.from_environ(environ)

    return h

def send_http_status(httpstatus, msg=''):

    status = f'{httpstatus.value} {httpstatus.phrase}'
    headers = Headers()
    headers.add("Content-Type", "text/plain; charset=utf=8")

    if msg and isinstance(msg, str):
        response = msg
    else:
        response = httpstatus.description

    return status, headers, [response.encode('utf-8')]

def get_file_headers(request, response):
    """
    This sends the response code and MIME headers.
    Return value is either a file object (which has to be copied
    to the outputfile by the caller and must be closed by the
    caller under all circumstances), or None, in which case the
    caller has nothing further to do.
    """
    ctype = guess_type(request.path)
    try:
        fs = os.fstat(response.fileno())
        # Use browser cache if possible
        if ("If-Modified-Since" in request.headers \
                and "If-None-Match" not in request.headers):
            # compare If-Modified-Since and time of last file modification
            try:
                ims = email.utils.parsedate_to_datetime(
                    request.headers["If-Modified-Since"])
            except (TypeError, IndexError, OverflowError, ValueError):
                # ignore ill-formed values
                pass
            else:
                if ims.tzinfo is None:
                    # obsolete format with no timezone, cf.
                    # https://tools.ietf.org/html/rfc7231#section-7.1.1.1
                    ims = ims.replace(tzinfo=datetime.timezone.utc)
                if ims.tzinfo is datetime.timezone.utc:
                    # compare to UTC datetime of last modification
                    last_modif = datetime.datetime.fromtimestamp(
                        fs.st_mtime, datetime.timezone.utc)
                    # remove microseconds, like in If-Modified-Since
                    last_modif = last_modif.replace(microsecond=0)

                    if last_modif <= ims:
                        response.close()
                        return send_http_status(HTTPStatus.NOT_MODIFIED)
        headers = Headers()
        headers.add("Content-type", ctype)
        headers.add("Content-Length", str(fs[6]))
        headers.add("Last-Modified", date_time_string(fs.st_mtime))

        return headers

    except Exception:
        raise

def get_text_headers(response_bytes):

    headers = Headers()
    headers.add("Content-Type", "text/html", charset='utf-8')
    headers.add("Content-length", str(len(response_bytes)))

    return headers

class Headers:
    """An object that stores some headers. It has a dict-like interface,
    but is ordered, can store the same key multiple times, and iterating
    yields ``(key, value)`` pairs instead of only keys.
    This data structure is useful if you want a nicer way to handle WSGI
    headers which are stored as tuples in a list.

    Patched version of werkzeug's Headers Class.
    """

    def __init__(self):
        self._list = []

    def __getitem__(self, key):

        if isinstance(key, int):
            return self._list[key]
        elif isinstance(key, slice):
            return self.__class__(self._list[key])
        if not isinstance(key, str):
            raise KeyError()
        ikey = key.lower()
        for k, v in self._list:
            if k.lower() == ikey:
                return v


    def get(self, key, type=None):
        """Return the default value if the requested data doesn't exist.
        If `type` is provided and is a callable it should convert the value,
        return it or raise a `ValueError` if that is not possible.
        """
        try:
            rv = self.__getitem__(key)
        except KeyError:
            raise
        if type is None:
            return rv
        try:
            return type(rv)
        except ValueError:
            raise

    def getlist(self, key, type=None):
        """Return the list of items for a given key. If that key is not in the
        `Headers`, the return value will be an empty list.  Just like
        `get`, `getlist` accepts a `type` parameter.  All items will
        be converted with the callable defined there.
        """
        ikey = key.lower()
        result = []
        for k, v in self:
            if k.lower() == ikey:
                if type is not None:
                    try:
                        v = type(v)
                    except ValueError:
                        continue
                result.append(v)
        return result

    def get_all(self, name):
        """Return a list of all the values for the named field.
        This method is compatible with the `wsgiref`
        `~wsgiref.headers.Headers.get_all` method.
        """
        return self.getlist(name)

    def items(self, lower=False):
        for key, value in self:
            if lower:
                key = key.lower()
            yield key, value

    def keys(self, lower=False):
        for key, _ in self.items(lower):
            yield key

    def values(self):
        for _, value in self.items():
            yield value

    def __delitem__(self, key, _index_operation=True):
        if _index_operation and isinstance(key, (int, slice)):
            del self._list[key]
            return
        key = key.lower()
        new = []
        for k, v in self._list:
            if k.lower() != key:
                new.append((k, v))
        self._list[:] = new

    def remove(self, key):

        return self.__delitem__(key, _index_operation=False)

    def pop(self, key=None):
        """Removes and returns a key or index."""
        if key is None:
            return self._list.pop()
        if isinstance(key, int):
            return self._list.pop(key)
        try:
            rv = self[key]
            self.remove(key)
        except KeyError:
            raise
        return rv

    def __contains__(self, key):
        """Check if a key is present."""
        try:
            self.__getitem__(key)
        except KeyError:
            return False
        return True

    def __iter__(self):
        """Yield ``(key, value)`` tuples."""
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def add(self, _key, _value, **kw):
        """Add a new header tuple to the list.
        Keyword arguments can specify additional parameters for the header
        value, with underscores converted to dashes::
        """
        if kw:
            _value = dump_options_header(_value, kw)
        _key = to_header_string(_key)
        _value = decode_value(_value)
        self._validate_value(_value)
        self._list.append((_key, _value))

    def _validate_value(self, value):
        if not isinstance(value, str):
            raise TypeError("Value should be a string.")
        if "\n" in value or "\r" in value:
            raise ValueError(
                "Detected newline in header value.  This is "
                "a potential security problem"
            )

    def from_environ(self, environ):

        for k,v in environ.items():
            if k.startswith("HTTP_") and k not in (
                    "HTTP_CONTENT_TYPE",
                    "HTTP_CONTENT_LENGTH"
                    ):
                self.add(k[5:], v)
            elif k in ("CONTENT_TYPE", "CONTENT_LENGTH") and v:
                self.add(k, v)

    def add_header(self, _key, _value, **_kw):
        """Add a new header tuple to the list.
        An alias for :meth:`add` for compatibility with the :mod:`wsgiref`
        :meth:`~wsgiref.headers.Headers.add_header` method.
        """
        self.add(_key, _value, **_kw)

    def clear(self):
        """Clears all headers."""
        del self._list[:]

    def to_wsgi_list(self):
        """Convert the headers into a list suitable for WSGI.
        :return: list
        """
        return list(self)

    def __copy__(self):
        return self.__class__(self._list)

    def __str__(self):
        """Returns formatted headers suitable for HTTP transmission."""
        strs = []
        for key, value in self.to_wsgi_list():
            strs.append(f"{key}: {value}")
        strs.append("\r\n")
        return "\r\n".join(strs)

    def __repr__(self):
        return f"{type(self).__name__}({list(self)!r})"

