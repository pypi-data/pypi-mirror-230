import pandas as pd

from .resources import find


def load_penguins():
    """Return Chinstrip and Adelie penguins from the Palmer penguins dataset."""
    file_path = find("penguins.csv")
    penguins = pd.read_csv(file_path)

    penguin_species = dict(tuple(penguins.groupby("species")))
    penguin_species = {
        species: data.reset_index(drop=True)
        for species, data in penguin_species.items()
    }

    return penguin_species["Chinstrap"], penguin_species["Adelie"]


def load_taxis():
    """Return subset of taxis dataset, as amended from the seaborn package."""
    file_path = find("taxis.csv")
    return pd.read_csv(file_path, skiprows=2)


def load_movies():
    """Return the IMDB movies DataFrame."""
    file_path = find("movies.zip")
    return pd.read_csv(file_path)
