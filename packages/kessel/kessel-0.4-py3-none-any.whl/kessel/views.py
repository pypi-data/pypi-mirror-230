from kessel.helpers import setup_jinja2_environment


class BaseView:

    def __call__(self, request):

        return self.dispatch_request(request)

    def dispatch_request(self, request):
        pass

class AssetView(BaseView):

    def __init__(self, assetPath):

        self.path = assetPath

    def dispatch_request(self, request):

        return open(self.path, 'rb')

class HomeView(BaseView):

    def __init__(self):

        self.methods = ['GET', 'POST']

    def dispatch_request(self, request):

        return "Welcome User!"

class AuthView(BaseView):

    def __init__(self, session_service):

        self.session_service = session_service
        self.render_template = setup_jinja2_environment()

class LoginView(AuthView):

    def __init__(self, session_service):
        super().__init__(session_service)

        self.methods = ['GET', 'POST']

    def dispatch_request(self, request):

        if request.method == 'POST':

            username = request.form.get('username', 'None')
            password = request.form.get('password', 'None')

            # user = self.session_service.login_with_ldap(username, password)
            user = self.session_service.mock_login(username, password)

            if user is not None:

                return 'Login succeeded.'

        elif request.method == 'GET':

            if request.query[0]:
                action=f"{request.path}?{'&'.join(request.query)}"
            else:
                action=f"{request.path}?next=/"

            return self.render_template('login.html',
                                   action=action,
                                   csrf_token=self.session_service.session.csrf_token)
        return 'Login failed.'

class LogoutView(AuthView):

    def __init__(self, session_service):
        super().__init__(session_service)

        self.methods = ['GET', 'POST']

    def dispatch_request(self, request):

        if request.method == 'POST':
            pass
        elif request.method == 'GET':

            if self.session_service.reset_user() and self.session_service.reset_session():
                return self.render_template('logout.html')

        return 'Logout failed.'
