from threading import local


class ApplicationContext(local):

    def __init__(self, /, **kw):
        self.__dict__.update(kw)
        self.app = None
        self.request = None
        self.user = None

    def current_user(self):
        return self.user

    def current_app(self):
        return self.app

    def current_request(self):
        return self.request

app_context = ApplicationContext()
