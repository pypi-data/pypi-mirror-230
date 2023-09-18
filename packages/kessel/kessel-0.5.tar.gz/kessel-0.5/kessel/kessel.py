from pathlib import Path
from .wsgibase import WSGIBase
from .urlmap import Resource
from .views import LoginView, LogoutView
from .context import app_context

class Kessel(WSGIBase):

    """WSGI-compliant Application Class"""

    def __init__(self, err_log=None):

        if err_log is not None:
            super().__init__(err_log=err_log)
        else:
            super().__init__(err_log=logging.getLogger('kessel.error'))

        self.urlmap.add("/login",
                         Resource(LoginView(self.session_service),
                                  ["GET", "POST"]))
        self.urlmap.add("/logout",
                         Resource(LogoutView(self.session_service),
                                  ["GET", "POST"]))
        # TODO: config
        asset_dir = Path(
            Path(__file__).parent.resolve(),
            'static'
        )
        self.urlmap.assemble_asset_routes(asset_dir)

        self.push_to_context()

    def push_to_context(self):

        app_context.app = self
        self.app_context = app_context

    def add_recipe(self, recipe):

        self.urlmap.update(recipe.urlmap)

    def route(self, spec, methods=["GET"]):
        """
        use this decorator to register function to url_map
        under spec. methods can be "POST" or "GET".
        returns Resource for further consumption by decorators,
        which is not to be called directly; kessel.dispatch_request()
        performs lookup based on route in kessel.url_map instead.
        """
        def wrapper(view_fn):
            resource = Resource(view_fn, methods)
            self.urlmap.add(spec, resource)
            return view_fn
        return wrapper

    def secured(self, view_fn=None, roles=['user']):
        """
        use this decorator to register as restricted and assign roles.
        looks up resource in url_map, adds it to url_map.secure_routes.
        returns Resource as in kessel.route. Omit braces when using
        without arguments, e.g. just '@app.secure'.
        """
        def wrapper(view_fn):
            for pspec, resource in self.urlmap.routes.items():
                if view_fn is resource.view_fn:
                   resource.roles = roles
            return view_fn
        if view_fn:
            return wrapper(view_fn)
        return wrapper


