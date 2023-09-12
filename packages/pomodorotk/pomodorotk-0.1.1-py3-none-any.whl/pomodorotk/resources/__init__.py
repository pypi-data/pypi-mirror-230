from contextlib import contextmanager
from importlib import resources

@contextmanager
def get_resource(name):
    res_obj = resources.files("pomodorotk.resources").joinpath(name)
    with resources.as_file(res_obj) as file_:
        yield file_
