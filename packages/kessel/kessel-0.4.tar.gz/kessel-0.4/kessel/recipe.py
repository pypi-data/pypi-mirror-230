from .urlmap import Resource, PathSpec
from kessel import current_app

from functools import wraps

class Recipe:

    def __init__(self):

        self.routes = dict()
        self.secure_routes = []

    def route(self, path, methods=["GET"]):
        """
        use this decorator to register function to url_map
        under path. methods can be "POST" or "GET".
        returns Resource for further consumption by decorators.
        To be copied to app by kessel.add_recipe.
        """
        def wrapper(view_fn):
            resource = Resource(path, view_fn, methods)
            pspec = PathSpec(path)
            self.routes[pspec] = resource
            return resource
        return wrapper

    def secured(self, resource=None, roles=['user']):
        """
        use this decorator to register ressource as restricted and assign
        roles. To be copied to app by kessel.add_recipe. Omit braces when
        using without arguments, e.g. just '@app.secure'.
        """
        def wrapper(resource):
            resource.roles = roles
            return resource
        if resource:
            return wrapper(resource)
        return wrapper
