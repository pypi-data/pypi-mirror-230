import os
import re
from functools import wraps
from pathlib import Path
from .helpers import HTTPMethodError
from .views import AssetView, HomeView

class URLMap:

    def __init__(self):
        self.routes = dict()
        self.secure_routes = []

    def update(self, other):
        if isinstance(other, dict):
            self.routes.update(other)
        elif isinstance(other, URLMap):
            self.secure_routes += other.secure_routes
            self.routes.update(other.routes)

    def add(self, spec, resource):
        if isinstance(spec, PathSpec):
            new_spec = spec
        else:
            new_spec = PathSpec(spec)
        return self.routes.update({new_spec : resource})

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

    def assemble_asset_routes(self, assetDir):
        for root, dirs, names in os.walk(assetDir):
            for name in names:
                abs_path = os.path.join(root, name)
                prefix = str(Path(Path(__file__).parent.resolve()))
                path = abs_path.replace(prefix, '')
                self.add(path, Resource(AssetView(abs_path),
                                        ["GET"]))

class Resource:

    def __init__(self,
                 view_fn=None,
                 methods=["GET"],
                 roles=[]
                 ):
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

    def __add__(self, other):

        if self.is_regex:
            spec = re.compile(str(self), str(other))
        else:
            spec = self.spec + str(other)
        return PathSpec(spec)

    def __radd__(self, other):

        if self.is_regex:
            spec = re.compile(str(other), str(self))
        else:
            spec = str(other) + self.spec
        return PathSpec(spec)

    def matches(self, path):
        if self.is_regex:
            return re.match(self.spec, path)
        else:
            return self.spec == path

    def groups(self, path):
        """retrieves groups from given path matching self.spec"""
        if self.is_regex and self.has_groups:
            return re.match(self.spec, path).groupdict()

