from shutil import copyfile

from .resources import find


def populate_example(filename):
    """Copy example from package resources to current working directory."""
    file_path = find(filename, "examples")
    copyfile(file_path, filename)
    print(f"\nCreated file {filename} in current directory.\n")


def get_dirty():
    """Copy the dirty script example to the user's current directory."""
    populate_example("script-dirty.py")


def get_messy():
    """Copy the messy script example to the user's current directory."""
    populate_example("script-messy.py")


def get_test():
    """Copy the test function to the user's current directory."""
    populate_example("test_forecast.py")
