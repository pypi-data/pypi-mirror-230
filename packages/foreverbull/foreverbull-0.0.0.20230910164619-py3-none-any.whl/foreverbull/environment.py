from functools import wraps
from importlib.machinery import SourceFileLoader
from inspect import getabsfile, signature

from foreverbull import data, models

func = None
parameters = None
file_path = None


def algo(f):
    @wraps(f)
    def wrapper(f):
        def eval_param(type: any) -> str:
            if type == int:
                return "int"
            elif type == float:
                return "float"
            elif type == bool:
                return "bool"
            elif type == str:
                return "str"
            else:
                raise Exception("Unknown parameter type: {}".format(type))

        global func
        global parameters
        global file_path
        func = f
        parameters = []
        file_path = getabsfile(f)
        for key, value in signature(f).parameters.items():
            if value.annotation == data.Asset or value.annotation == data.Portfolio:
                continue
            default = None if value.default == value.empty else str(value.default)
            parameter = models.service.Parameter(key=key, default=default, type=eval_param(value.annotation))
            parameters.append(parameter)
        return f

    return wrapper(f)


def import_file(file_path: str):
    SourceFileLoader("", file_path).load_module()
