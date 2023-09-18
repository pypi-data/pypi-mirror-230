import json
from uuid import uuid4 as uuid
from secrets import token_urlsafe
from datetime import timedelta, timezone
from datetime import datetime

import jwt
from jwt import ExpiredSignatureError

class SessionService:
    """Performs common operations on session objects"""

    def __init__(self, app):

        self.app = app
        self.session = None
        self.user = None
        self.login_route = '/login'
        self.cookie_key = 'session_token'
        # self.psk = token_urlsafe(512)
        # TODO: Config
        self.psk = 'change to something safe'
        # TODO: Config
        # self.private_key = self.read_key('test-app/private.pem')
        # self.private_key = self.read_key('test-app/private.pem')
        self.public_key = None
        self.public_key = None

    def read_key(self, path):
        with open(path, 'rb') as openFile:
            key = openFile.read()
        return key

    def check_authentication(self, request):
        """sets user session or initiates new one"""
        if token_msg := self.has_session_cookie(request.cookies):
            # maintain session even without user
            self.register_session(
                self.create_session(from_msg=token_msg)
            )
            # if user present, set self.user
            if uid := token_msg.get('sub', False):
                self.register_user(
                    User(uid=uid,
                         roles=token_msg.get('roles', ['user']),
                         logged_in=token_msg.get('logged_in', False))
                )
        else: # create new session
            self.register_session(self.create_session())

    def has_session_cookie(self, cookies):
        if self.cookie_key in [c.lower() for c in cookies.keys()]:
            if token_msg := self.verify_token(cookies[self.cookie_key]):
                return token_msg

    def verify_token(self, token):
        if self.psk:
            key = self.psk
        elif self.public_key:
            key = self.public_key
        try:
            msg = jwt.decode(token, key, algorithms=["HS256", "RS256"])
        except ExpiredSignatureError as e:
            # Signature expired
            # TODO: do somthing sensible here
             return None
        return msg

    def issue_token(self, msg):
        if self.psk:
            key = self.psk
            alg ="HS256"
        elif self.private_key:
            key = self.private_key
            alg = "RS256"
        args = self.jwt_args()
        return jwt.encode(msg, key, algorithm=alg)

    def create_session(self, from_msg=False):

        if msg := from_msg:
            return Session(uuid = msg['jti'],
                           csrf_token = msg['csrf_token'],
                           issued_at = msg['iat'],
                           expires = msg['exp'],
                           msg = msg)
        return Session()

    def check_authorisation(self, resource):
        """assumes user present and authenticated session"""

        # true iff any of user roles matches those tied to resource
        return any(
            map(lambda role: role in self.user.roles, resource.roles)
        )

    def check_csrf(self, request):
        # check for csrf token in header
        if csrf_token := request.headers.get('x-csrf-token'):
            return csrf_token == self.session.csrf_token

        # alternatively check in hidden form value
        if csrf_token := request.form.get('CSRFToken'):
            return csrf_token == self.session.csrf_token

    def session_cookie(self):

        if self.session.msg:
            msg = self.session.msg
        else:
            msg = {'iss' : f'{self.app.sitename}',
                   'iat' : self.session.issued_at,
                   'exp' : self.session.expires,
                   'jti' : self.session.uuid,
                   'csrf_token' : self.session.csrf_token}
        if self.user:
            msg['sub'] = self.user.uid
            msg['roles'] = self.user.roles
            msg['logged_in'] = self.user.logged_in

        cookie = (
            f"{self.cookie_key}={self.issue_token(msg)}"
            ";Path=/"
            ";HTTPOnly"
            ";SameSite=Strict"
        )
        return cookie

    def register_user(self, user):

        self.user = user
        self.app.app_context.user = user
        return True

    def reset_user(self):

        self.user = None
        self.app.app_context.user = None
        return True

    def register_session(self, session):

        self.session = session
        self.app.app_context.session = session
        return True

    def reset_session(self):

        self.session = Session()
        self.app.app_context.session = self.session
        return True

    def mock_login(self, username, password):

        self.register_user(User(uid=username, roles=['user'], logged_in=True))
        return self.user

    def jwt_args(self):
        # psk takes precedence over RSA because of sheer speed
        if self.psk:
            args = (self.psk, ["HS256"])
        elif self.public_key and self.private_key:
            args = self.public_key, ["RS256"]
        else:
            raise AttributeError('No key present')
        return args



class User:

    def __init__(self, uid=None, roles=['user'], logged_in=False):
        self.uid = uid
        self.roles = roles
        self.logged_in = logged_in

    def __str__(self):

        return str(self.uid)

class Session:
    """Object holding session information"""

    def __init__(self,
                 uuid=str(uuid()),
                 issued_at=datetime.now(timezone.utc),
                 expires=datetime.now(timezone.utc) + timedelta(hours=1),
                 csrf_token=token_urlsafe(),
                 msg=None,
                 ):

        self.uuid = uuid
        self.issued_at = issued_at
        self.expires = expires
        self.csrf_token = csrf_token
        self.msg = msg

def parse_cookies(cookie_list):
    if cookie_list:
        return dict(((c.split("=")) for c in cookie_list.split(";")))
    return dict()

