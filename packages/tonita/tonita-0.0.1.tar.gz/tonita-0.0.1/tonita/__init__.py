import os

import tonita.constants

# Assume first that API key has been exported as an environment variable (this
# value will be None if not).
# In particular, a key stored in the environment variable will be used if
# available, unless the user sets this value after importing this library.
# The `vars()` here gives us access to the module variables via the module's
# __dict__ attribute, and allows us to avoid hardcoding the values of
# `API_KEY_NAME` and `CORPUS_ID_NAME` here.
vars()[tonita.constants.API_KEY_NAME] = os.environ.get("TONITA_API_KEY")

# Initialize to `None`.
vars()[tonita.constants.CORPUS_ID_NAME] = None

# For API URL-related module variables, we first look for a value set in the
# environment variables. If the value is not set there, we use a default.
name_to_envname_and_defaultval = {
    tonita.constants.BASE_URL_NAME: (
        "TONITA_API_BASE_URL",
        "https://api.tonita.co",
    ),
    tonita.constants.CORPORA_PATH_ROOT_NAME: (
        "TONITA_CORPORA_PATH_ROOT",
        "corpora",
    ),
    tonita.constants.LISTINGS_PATH_ROOT_NAME: (
        "TONITA_LISTINGS_PATH_ROOT",
        "listings",
    ),
    tonita.constants.SEARCH_PATH_ROOT_NAME: (
        "TONITA_SEARCH_PATH_ROOT",
        "search",
    ),
    tonita.constants.EVAL_PATH_ROOT_NAME: (
        "TONITA_EVAL_PATH_ROOT",
        "eval",
    ),
}

for name, (envname, defaultval) in name_to_envname_and_defaultval.items():
    vars()[name] = os.environ.get(envname)
    if vars()[name] is None:
        vars()[name] = defaultval


# After having set the relative root paths for each part of the API, import
# APIs into the main namespace.
from tonita.api import corpora, eval, listings
from tonita.api.search import search
