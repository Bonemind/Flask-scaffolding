import functools
from peewee import Model, SelectQuery
from flask import make_response
import jsonpickle
from serializer import Serializer

def JsonResponse(f):
    """
    Constructs a json response from the data it is passed
    Should accept any returned data
    Sets the mimetype to application/json
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        returned = f(*args, **kwargs)
        if isinstance(returned, tuple):
            lst = list(returned)
            lst[0] = jsonify(returned[0])
            responseData = tuple(lst)
        else:
            responseData = jsonify(returned)
        print responseData

        resp = make_response(responseData)
        resp.mimetype = "application/json"
        return resp
    return wrapper

def jsonify(inputData):
        if isinstance(inputData, SelectQuery):
                inputData = fix_peewee_list(list(inputData))
        elif isinstance(inputData, list) and len(inputData) > 0:
                if isinstance(inputData[0], Model):
                        inputData = fix_peewee_list(inputData)
        elif isinstance(inputData, Model):
                inputData = fix_peewee_obj(inputData)
        return jsonpickle.encode(inputData, unpicklable=False)    

def fix_peewee_list(l):
    """
    Grabs all objects inside a peewee SelectQuery and serializes them
    """
    return [fix_peewee_obj(x) for x in l]

def fix_peewee_obj(obj):
    """
    Serializes a single peewee object
    """
    ser = Serializer()
    return ser.serialize_object(obj)
