from .wsgibase import WSGIBase
from .urlmap import Resource

from functools import wraps, partial

class Kessel(WSGIBase):

    """WSGI-compliant Application Class"""

    def __init__(self, err_log=None):

        if err_log is not None:
            super().__init__(err_log=err_log)
        else:
            super().__init__(err_log=logging.getLogger('kessel.error'))

    def add_recipe(self, recipe):

        self.url_map.routes.update(recipe.routes)
        self.url_map.secure_routes += recipe.secure_routes

    def route(self, path, methods=["GET"]):
        """
        use this decorator to register function to url_map
        under path. methods can be "POST" or "GET".
        returns Resource for further consumption by decorators,
        which is not to be called directly; kessel.dispatch_request()
        performs lookup based on route in kessel.url_map instead.
        """
        def wrapper(view_fn):
            resource = Resource(path, view_fn, methods)
            self.url_map.add(path, resource)
            return resource
        return wrapper

    def secured(self, resource=None, roles=['user']):
        """
        use this decorator to register as restricted and assign roles.
        looks up resource in url_map, adds it to url_map.secure_routes.
        returns Resource as in kessel.route. Omit braces when using
        without arguments, e.g. just '@app.secure'.
        """
        def wrapper(resource):
            resource.roles = roles
            return resource
        if resource:
            return wrapper(resource)
        return wrapper


