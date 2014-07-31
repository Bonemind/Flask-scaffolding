import datetime
import sys

from peewee import Model, ForeignKeyField


class Serializer(object):
    """
    Serializes peewee objects
    Shamelessly stolen from https://github.com/coleifer/flask-peewee/blob/master/flask_peewee/serializer.py
    """
    date_format = '%Y-%m-%d'
    time_format = '%H:%M:%S'
    datetime_format = ' '.join([date_format, time_format])

    def convert_value(self, value):
        """
        Converts dates to a string
        """
        if isinstance(value, datetime.datetime):
            return value.strftime(self.datetime_format)
        elif isinstance(value, datetime.date):
            return value.strftime(self.date_format)
        elif isinstance(value, datetime.time):
            return value.strftime(self.time_format)
        elif isinstance(value, Model):
            return value.get_id()
        else:
            return value

    def clean_data(self, data):
        """
        Cleans data
        Converts dates to strings
        """
        for key, value in data.items():
            if isinstance(value, dict):
                self.clean_data(value)
            elif isinstance(value, (list, tuple)):
                data[key] = map(self.clean_data, value)
            else:
                data[key] = self.convert_value(value)
        return data

    def serialize_object(self, obj, fields=None, exclude=None):
        """
        Turns a peewee model into a dictionary
        Cleans the returned dictionary, i.e converts dates to strings
        Flattens maps
        """
        data = get_dictionary_from_model(obj, fields, exclude)
        return self.clean_data(data)


class Deserializer(object):
    """
    Deserilizes an object into a model
    """
    def deserialize_object(self, model, data):
        return get_model_from_dictionary(model, data)

def get_dictionary_from_model(model, fields=None, exclude=None):
    """
    Gets a fields dictionary from a model
    """
    model_class = type(model)
    data = {}

    fields = fields or {}
    #Models can have an excluse function that should return a dictionary for field names
    #to exclude when serializing
    try:
        exclude = model.exclude()
    except:
        exclude = exclude or {}
    curr_exclude = exclude
    curr_fields = fields.get(model_class, model._meta.get_field_names())

    for field_name in curr_fields:
        if field_name in curr_exclude:
            continue
        field_obj = model_class._meta.fields[field_name]
        field_data = model._data.get(field_name)
        if isinstance(field_obj, ForeignKeyField) and field_data and field_obj.rel_model in fields:
            rel_obj = getattr(model, field_name)
            data[field_name] = get_dictionary_from_model(rel_obj, fields, exclude)
        else:
            data[field_name] = field_data
    return data

def get_model_from_dictionary(model, field_dict):
    """
    Returns a model from a dictionary
    """
    if isinstance(model, Model):
        model_instance = model
        check_fks = True
    else:
        model_instance = model()
        check_fks = False
    models = [model_instance]
    for field_name, value in field_dict.items():
        field_obj = model._meta.fields[field_name]
        if isinstance(value, dict):
            rel_obj = field_obj.rel_model
            if check_fks:
                try:
                    rel_obj = getattr(model, field_name)
                except field_obj.rel_model.DoesNotExist:
                    pass
                if rel_obj is None:
                    rel_obj = field_obj.rel_model
            rel_inst, rel_models = get_model_from_dictionary(rel_obj, value)
            models.extend(rel_models)
            setattr(model_instance, field_name, rel_inst)
        else:
            setattr(model_instance, field_name, field_obj.python_value(value))
    return model_instance, models
