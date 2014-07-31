from flask.ext.classy import FlaskView
from web import JsonResponse as jr
from web import ApplicationException as ax
from web import auth
class AuthView(FlaskView):
    @auth.authorize(role = "read")
    @jr.JsonResponse
    def index(self, **kwargs):
        return "xxxxx"

    @auth.authorize(role="asdasd")
    @jr.JsonResponse
    def post(self, **kwargs):
        return "Hello!", 48, {"X-Some-Header" : "Some-Value", "X-Other-Header" : "Other-Value"}


