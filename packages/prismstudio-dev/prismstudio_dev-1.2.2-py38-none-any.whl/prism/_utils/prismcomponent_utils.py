import shutil
from functools import wraps
from pathlib import Path

import pandas as pd

def _get_params(param_dict):
    return {k: v for k, v in param_dict.items() if not (k.startswith("_") or (k == "self"))}


def _req_call(call_type):
    def decorator(func):
        @wraps(func)
        def wrapper(**kwargs):
            func(**kwargs)
            # vars = func.__code__.co_varnames[1:]
            # params = dict(zip(vars[: len(args)], args))
            # params.update(dict(kwargs))
            fn = getattr(call_type, func.__name__)
            obj = kwargs.pop("self")
            return fn(obj, **kwargs)

        return wrapper

    return decorator


class DisplayablePath(object):
    display_filename_prefix_middle = "├──"
    display_filename_prefix_last = "└──"
    display_parent_prefix_middle = "    "
    display_parent_prefix_last = "│   "

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + "/"
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path for path in root.iterdir() if criteria(path)), key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path, parent=displayable_root, is_last=is_last, criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + "/"
        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = self.display_filename_prefix_last if self.is_last else self.display_filename_prefix_middle

        parts = ["{!s} {!s}".format(_filename_prefix, self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle if parent.is_last else self.display_parent_prefix_last)
            parent = parent.parent

        return "".join(reversed(parts))


def create_files(paths, directory):
    for path in paths:
        output_file = Path(f"./tmp/{directory}/" + path)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        output_file.write_text("FOOBAR")


def plot_tree(paths: list, directory: str):
    # Create mock files on local file system
    rootdir = f"./tmp/{directory}"
    create_files(paths, directory)

    if not paths:
        return
    # Remove username in the front
    # Display all the files
    paths = DisplayablePath.make_tree(Path(rootdir))
    for path in paths:
        print(path.displayable())

    # delete folder
    shutil.rmtree(rootdir)
    return

def are_periods_exclusive(startdate1, enddate1, startdate2=None, enddate2=None):
    violated_condition = []
    if (startdate2 is not None) or (enddate2 is not None):
        if enddate2 is not None:
            violated_condition.append(startdate1 > pd.to_datetime(enddate2))
        if startdate2 is not None:
            violated_condition.append(enddate1 < pd.to_datetime(startdate2))
    return any(violated_condition)
