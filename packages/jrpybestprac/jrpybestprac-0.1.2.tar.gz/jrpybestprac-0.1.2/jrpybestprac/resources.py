import errno
import os
from pkg_resources import resource_listdir, resource_filename


def find(filename, parent="data", ext="csv"):
    """Find filepath to a resource within this package"""

    if "." not in filename:
        filename += ext
        print(f"No file extension specified; trying to load {filename}.")

    if filename not in resource_listdir(__name__, parent):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)

    file_path = resource_filename(__name__, f"{parent}/{filename}")

    return file_path
