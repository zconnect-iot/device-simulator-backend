from flask.json import JSONEncoder


class JSONEncodable:
    json_fields_to_ignore = []

    def serialize_to_json(self):
        d = self.__dict__
        output = d.copy()
        for key in d:
            if key in self.json_fields_to_ignore:
                del output[key]
        return output


class CustomJSONEncoder(JSONEncoder):
    """ Allows encoding any class that implements a method 'serialize_to_json'
    """
    # pylint: disable=method-hidden

    def default(self, o):
        if issubclass(o.__class__, JSONEncodable):
            return o.serialize_to_json()

        return JSONEncoder.default(self, o)


def dump_plain_json(obj):
    """ Used to dump a plain JSON object from mongoengine - for MQTT messages"""
    return JSONEncoder().encode(obj)
