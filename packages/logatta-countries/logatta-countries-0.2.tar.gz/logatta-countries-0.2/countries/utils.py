from datetime import datetime
from rest_framework.response import Response


def get_path(instance, filename):
    # get the current timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # split filename into name and extension
    name, ext = filename.rsplit('.', 1)
    
    # return the path with timestamp added to the name
    return "{0}/{1}_{2}.{3}".format(instance._meta.model_name, name, timestamp, ext)


def MyResponse(dict):
    if dict.get("data"):
        dict["status"] = True
        dict["error"] = None

    elif dict.get("data") == []:
        dict["status"] = True
        dict["data"] = []

    else:
        dict["status"] = False
        dict["data"] = None

    return Response(dict)