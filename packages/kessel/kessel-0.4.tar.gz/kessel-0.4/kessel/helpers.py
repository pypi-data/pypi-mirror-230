import os
import shutil
import mimetypes
import email
import urllib
import html
from functools import wraps
from jinja2 import Environment, FileSystemLoader

class HTTPMethodError(Exception):
    pass

def setup_jinja2_environment(templates_path='templates'):

    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, templates_path)
    env = Environment( loader = FileSystemLoader(templates_dir) )

    def render_template(template_name, **kwargs):

        template = env.get_template(template_name)
        return template.render(**kwargs)
    return render_template

def urlencoded_safe_string(urlencoded):
    return html.escape(urllib.parse.unquote_plus(urlencoded))

def get_urlencoded_data(form_string):
    out = dict()
    for kv_pairs in form_string.split('&'):
        try:
            k,v = kv_pairs.split('=')
        except ValueError:
            k = kv_pairs.split('=')
            v = ''
        key = urlencoded_safe_string(k)
        value = urlencoded_safe_string(v)
        out[key] = value
    return out

def make_multipart_message(header, form_string):
    message_string = (
        'MIME-Version: 1.0\n'
        f'Content-Type: {header}\n'
        f'{form_string}'
    )
    msg = email.message_from_string(message_string)
    if msg.is_multipart():
        return msg

def get_multipart_data(message):
    out = dict()
    for part in message.get_payload():
        name = part.get_param('name',
                              header='content-disposition')
        filename = part.get_param('filename',
                                  header='content-disposition')
        data = part.get_payload()
        if filename:
            out[html.escape(name)] = (html.escape(filename), data)
        else:
            out[html.escape(name)] = html.escape(data)
    return out

def decode_value(value):

    if isinstance(value, bytes):
        value = value.decode('latin-1')
    return str(value)

def dump_options_header(value, kwarg):

    segments = [value]
    for k,v in kwarg.items():
        if v is None:
            segments.append(k)
        else:
            # decode, then quote value
            v = decode_value(v) \
                    .replace("\\", "\\\\") \
                    .replace('"', '\\"')
            segments.append(f'{k}={v}')
    return '; '.join(segments)

def to_header_string(envstring):

    return envstring.replace('_','-').lower()

def date_time_string(timestamp=None):
    """Return the current date and time
    formatted for a message header."""
    if timestamp is None:
        timestamp = time.time()
    return email.utils.formatdate(timestamp, usegmt=True)

def get_host_from_environ(environ):

    return environ.get("HTTP_HOST") or \
            f'{environ.get("SERVER_NAME")}:{environ.get("SERVER_PORT")}'

def guess_type(path):
    """Guess the type of a file.
    Argument is a PATH (a filename).
    Return value is a string of the form type/subtype,
    usable for a MIME Content-type header.
    """
    guess, _ = mimetypes.guess_type(path)
    if guess:
        return guess
    return 'application/octet-stream'

def copy_file(source, outputfile):
    """Copy all data between two file objects.
    The SOURCE argument is a file object open for reading
    (or anything with a read() method) and the DESTINATION
    argument is a file object open for writing (or
    anything with a write() method).
    The only reason for overriding this would be to change
    the block size or perhaps to replace newlines by CRLF
    -- note however that this the default server uses this
    to copy binary data as well.
    """
    shutil.copyfileobj(source, outputfile)

def get_next_page(query_tuple):

    for query in query_tuple:
        if query.startswith("next="):
            return f"{query.replace('next=','')}"

    return None

def strip_query_of_next_page(query_tuple):

    query_list = list(query_tuple)
    for query in query_list:
        if query.startswith("next="):
            query_list.remove(query)
            break
    return tuple(query_list)

def doublewrap(f):
    '''
    a decorator decorator, allowing the decorator to be used as:
    @decorator(with, arguments, and=kwargs)
    or
    @decorator
    '''
    @wraps(f)
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # actual decorated function
            return f(args[0])
        else:
            # decorator arguments
            return lambda realf: f(realf, *args, **kwargs)

    return new_dec
