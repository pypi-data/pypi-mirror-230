# setup


```bash
mkdir test-app && \
openssl genrsa -out test-app/private.pem 2048
```

# usage

```python
import sys
import json
import time
import logging
import argparse
import gunicorn.app.base

from configparser import ConfigParser

from kessel import Kessel
from kessel import Redirect
from kessel import setup_jinja2_environment

from kessel.logger import GunicornLogger, MockGunicornConfig

from kessel import current_app
from kessel import current_user
from kessel import current_request

from foo import foo_app

log = GunicornLogger(cfg=MockGunicornConfig())

app = Kessel(err_log=log)

app.add_recipe(foo_app)

render_template = setup_jinja2_environment()

config = ConfigParser()
config.read('project.cfg')

@app.route("/", methods=["GET"])
def home(request):

    request = current_request()
    log.info(f"{request.path}")
    return 'hello, world!'

# test precedence rules
@app.route("/retest/123")
def retest_static(req):
    return 'static'

import re
@app.route(re.compile(r"/retest/(?P<re_id>\d+$)"))
def retest(request, re_id):
    return f"{re_id}"

@app.route(re.compile(r"/retest/\w+$"))
def retest(request):
    return "generic"

@app.route("/redirect", methods=["GET"])
def redirect(request):

    return Redirect(request, "/")

@app.secured
@app.route("/secure", methods=["GET"])
def secure(request):

    request = current_request()
    log.info(f"{request.path}")

    return render_template('home.html', user=current_user().uid)

@app.secured(roles=["admin"])
@app.route("/admin", methods=["GET"])
def admin(request):

    return render_template('home.html', user=current_user().uid)

class HttpServer(gunicorn.app.base.BaseApplication):
   def __init__(self, app, options=None):
       self.options = options or {}
       self.application = app
       super().__init__()

   def load_config(self):
       for key, value in self.options.items():
           if key in self.cfg.settings and value is not None:
               self.cfg.set(key.lower(), value)

   def load(self):
       return self.application


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-workers', type=int, default=1)
    parser.add_argument('--port', type=str, default='8080')
    args = parser.parse_args()
    options = {
        'bind': '%s:%s' % ('0.0.0.0', args.port),
        # 'worker_class' : 'gthread',
        'logger_class' : 'kessel.logger.GunicornLogger',
        'workers': args.num_workers,
        'accesslog' : '-',
        'print_config': True,
    }
    HttpServer(app, options).run()
```

# recipes

```python
from kessel.recipe import Recipe


foo_app = Recipe()

@foo_app.route("/foo")
def foo_home(request):
    return 'foo!'


@foo_app.secured
@foo_app.route("/foo/bar")
def foo_bar(request):
    return 'bar!'
```
