import functools
from flask import request, abort

def getUserFromToken(currToken = None):
    import database.general as d
    if not currToken:
        return None

    if isinstance(currToken, d.Tokens):
        return currToken.user

    try:
        t = d.Tokens.get(d.Tokens.token == currToken)
        u = t.user
        print u.username 
    except d.Tokens.DoesNotExist:
        return None
    return u

def authorize(role = None):
    import database.general as d
    def wrap(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            print "Request:" + str(request.headers.get("X-Auth-Token"))
            print role
            token = request.headers.get("X-Auth-Token")
            if not token:
                abort(401)
            token = str(request.headers.get("X-Auth-Token"))
            user = getUserFromToken(token)
            if not user:
                abort(401)
            if role:
                if not user.hasRole(role):
                    abort(403)
            return f(*args, **kwargs)
        return wrapper
    return wrap
