import json

from bson import json_util


# bson -> json str
def bson_to_json(data):
    return json.loads(json_util.dumps(data))
