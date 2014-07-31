from __future__ import print_function
import functools
import json
from flask import Flask, abort
from common.binder import Binder
from servers.base import Server

class API(Binder):
    """
    Process the JSON api functions.
    """

    @classmethod
    def get_app(cls):
        """
        Contruct a Flask object from the bound methods.
        """
        app = Flask(__name__)
        for func, data, kwdata in cls.bound:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if u'serverid' in kwargs:
                    serverid = int(kwargs[u'serverid'])
                    for server in Server.get_instances():
                        if server.id == serverid:
                            del kwargs[u'serverid']
                            return json.dumps(func(server, *args, **kwargs))
                    return abort(404)
                return json.dumps(func(*args, **kwargs))
            wrapper.__name__ = unicode(id(wrapper))
            print(data[0])
            app.route(*data, **kwdata)(wrapper)
        return app

#vim:et:ts=4:sts=4:sw=4
