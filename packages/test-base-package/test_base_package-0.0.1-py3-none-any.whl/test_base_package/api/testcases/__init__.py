from base.http_client import HttpClient


class Auth(HttpClient):
    def __init__(self):
        super(Auth, self).__init__()


auth = Auth()
