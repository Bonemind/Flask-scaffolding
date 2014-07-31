from flask import Flask, request
from JsonResponse import *
import database.general as generaldb
import pyclbr
from auth import *
from flask.ext.classy import FlaskView
import jsonpickle
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from views import *
from ApplicationException import *

DEBUG = True

__all__ = ['json_app']

def json_app(import_name, **kwargs):
    """
    Creates a JSON-oriented Flask app.

    All error responses that you don't specifically
    manage yourself will have application/json content
    type, and will contain JSON like this (just an example):

    {
        "message": "405: Method Not Allowed",
        "statuscode": 405
    }
    """
    def make_json_error(ex):
        if not isinstance(ex, ApplicationException):
            appexception = ApplicationException(message=str(ex), statuscode=ex.code)
        else:
            appexception = ex
        json_str = jsonpickle.encode(appexception, unpicklable=False)
        resp = make_response(json_str)
        resp.status_code = appexception.statuscode
        resp.mimetype = "application/json"
        return resp

        response = jsonpickle.encode(ex)
        response.status_code = (ex.code
                                if isinstance(ex, HTTPException)
                                else 500)
        return response

    app = Flask(import_name, **kwargs)

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error

    return app

app = json_app(__name__)
app.config.from_object(__name__)

@app.errorhandler(ApplicationException)
def applicationErrorHandler(e):
    """
    Handles application errors
    """
    json_str = jsonpickle.encode(e, unpicklable=False)
    resp = make_response(json_str)
    resp.status_code = e.statuscode
    resp.mimetype = "application/json"
    return resp

# AuthView.register(app)

@app.after_request
def add_cors(resp):
    """ 
    Ensure all responses have the CORS headers. This ensures any failures are also accessible
    by the client.
    """
    print resp.headers
    resp.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin','*')
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    resp.headers['Access-Control-Allow-Headers'] = request.headers.get( 
        'Access-Control-Request-Headers', 'X-Auth-Token' )
    # set low for debugging
    if app.debug:
        resp.headers['Access-Control-Max-Age'] = '1'
    return resp

def get_subclasses(c):
    """
    Returns all subclasses of a given class
    Used to autmaticly register all views with the app
    """
    subclasses = c.__subclasses__()
    for d in list(subclasses):
        subclasses.extend(get_subclasses(d))
    return subclasses

class Web(object):
    @classmethod
    def run(self):
        generaldb.initTables()
        for cls in get_subclasses(FlaskView):
            route_prefix = "/"
            if cls.route_prefix:
                route_prefix = cls.route_prefix
            cls.register(app, route_prefix=route_prefix)
        #generaldb.createTestData()
        app.run(host="0.0.0.0")
