import os
import re
from functools import wraps
from pathlib import Path
from kessel.helpers import HTTPMethodError
from kessel.views import AssetView, HomeView, LoginView, LogoutView

class Resource:

    def __init__(self,
                 route='',
                 view_fn=None,
                 methods=["GET"],
                 roles=[]
                 ):
        self.route = route
        self.view_fn = view_fn
        self.methods = methods
        self.roles = roles

class PathSpec:

    def __init__(self, path):
        self.spec = path

        self.is_regex = False
        self.has_groups = False
        if isinstance(self.spec, re.Pattern):
            self.is_regex = True
            if self.spec.groups >= 1:
                self.has_groups = True
        elif isinstance(self.spec, str):
            pass
        else:
            raise TypeError('Pathspec.spec must be string or re.Pattern')

    def __hash__(self):
        return hash(self.spec)

    def __str__(self):
        if self.is_regex:
            return self.spec.pattern
        return self.spec

    def __eq__(self, other):
        return str(self.spec) == str(other)

    def __gt__(self, other):
        """predescence rules go from specific to generic:
        str > capture groups > regex"""
        return (
            not self.is_regex and not \
            (not other.is_regex and not other.has_groups)
        ) or (
            self.has_groups and \
            (other.is_regex and not other.has_groups)
        )

    def matches(self, path):
        """abstracts matching given path with spec"""
        if self.is_regex:
            return re.match(self.spec, path)
        else:
            return self.spec == path

    def groups(self, path):
        """retrieves groups from given path, else returns None"""
        if self.is_regex and self.has_groups:
            return re.match(self.spec, path).groupdict()

class URLMap:

    def __init__(self, app):
        self.routes = dict()
        self.secure_routes = []
        self.assetDir = Path(Path(__file__).parent.resolve(), 'static')
        self.add("/login",
                 Resource("/login",
                          LoginView(app.session_service),
                          ["GET", "POST"]))
        self.add("/logout",
                 Resource("/logout",
                          LogoutView(app.session_service),
                          ["GET", "POST"]))
        self.assemble_asset_routes()

    def add(self, path, resource):
        new_spec = PathSpec(path)
        self.routes.update({new_spec : resource})

    def route_for_path(self, path):
        cands = [(k,v) for k,v in self.routes.items() if k.matches(path)]
        if not cands:
            return None, None
        else:
            cur_ps, cur_res = cands[0]
        if len(cands) == 1:
            return cur_ps, cur_res
        for pspec, resource in cands[1:]:
            if pspec > cur_ps:
                cur_ps, cur_res = pspec, resource
        return cur_ps, cur_res

    def assemble_asset_routes(self):
        for root, dirs, names in os.walk(self.assetDir):
            for name in names:
                abs_path = os.path.join(root, name)
                prefix = str(Path(Path(__file__).parent.resolve()))
                path = abs_path.replace(prefix, '')
                self.add(path, Resource(path,
                                        AssetView(abs_path),
                                        ["GET"]))

