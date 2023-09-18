from .urlmap import URLMap, PathSpec, Resource

class Recipe:

    def __init__(self, base_path=""):

        self.base_path = base_path
        self.urlmap = URLMap()

    def route(self, spec, methods=["GET"]):
        """
        use this decorator to register function to url_map
        under path. methods can be "POST" or "GET".
        returns Resource for further consumption by decorators.
        To be copied to app by kessel.add_recipe.
        """
        def wrapper(view_fn):
            pspec = PathSpec(spec)
            resource = Resource(view_fn, methods)
            self.urlmap.add(self.base_path + pspec, resource)
            return view_fn
        return wrapper

    def secured(self, view_fn=None, roles=['user']):
        """
        use this decorator to register ressource as restricted and assign
        roles. To be copied to app by kessel.add_recipe. Omit braces when
        using without arguments, e.g. just '@app.secure'.
        """
        def wrapper(view_fn):
            for pspec, resource in self.urlmap.routes.items():
                if view_fn is resource.view_fn:
                   resource.roles = roles
            return view_fn
        if view_fn:
            return wrapper(view_fn)
        return wrapper
