import vhcs.ctxp.data_util as data_util
from os import path
from vhcs.plan import PlanException

_template_dir = path.abspath(path.join(path.dirname(__file__), "templates"))


def get(name: str, raise_on_not_found: bool = True):
    file_name = path.join(_template_dir, name)
    ret = data_util.load_data_file(file_name)

    if raise_on_not_found and not ret:
        raise PlanException("Template not found: " + name)
    return ret
