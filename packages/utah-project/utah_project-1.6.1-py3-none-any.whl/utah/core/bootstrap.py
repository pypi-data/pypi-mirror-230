import os

UTAH_APP_HOME = None
UTAH_VARIABLE_DATA = None
UTAH_STASH_CLASS = "utah.core.utilities.UtahStash"
TEXT_ENCODING = None

class HomeDirException(Exception):
    pass

def set_app_home(bootstrap_path:str):
    global UTAH_APP_HOME
    global UTAH_VARIABLE_DATA
    global UTAH_STASH_CLASS
    global TEXT_ENCODING

    # Determine location of bootstrap flask app
    app_path = bootstrap_path
    if app_path == "":
        app_path = "."
    
    app_path = app_path.replace("\\", "/")


    # Determine if environment variables are set
    # If so take app home from variable
    # if not set environment variables to location of bootstrap
    # This is to make testing in a workspace easier
    if "UTAH_APP_HOME" in os.environ:
        UTAH_APP_HOME = os.environ["UTAH_APP_HOME"]
        UTAH_VARIABLE_DATA = os.environ["UTAH_VARIABLE_DATA"]
    else:
        UTAH_APP_HOME = app_path
        UTAH_VARIABLE_DATA = app_path

    # Override the stash class if it is provided as a environment variable
    if UTAH_STASH_CLASS in os.environ:
        UTAH_STASH_CLASS = os.environ["UTAH_STASH_CLASS"]

    if not os.path.isdir(UTAH_APP_HOME):
        raise HomeDirException("Bad directory was provided:[%s]" % UTAH_APP_HOME)

    with open("%s/config/utah_encoding.txt" % UTAH_APP_HOME, 'r') as f:
        TEXT_ENCODING = f.readline()
        f.close()


def get_app_home():
    if not UTAH_APP_HOME:
        raise HomeDirException("APP_HOME is not set, app must call utah.core.bootstrap.set_app_home() before executing any operation")

    return UTAH_APP_HOME

def get_text_encoding():
    if not TEXT_ENCODING:
        raise HomeDirException("TEXT_ENCODING is not set, app must call utah.core.bootstrap.set_app_home() before executing any operation")

    return TEXT_ENCODING

def get_stash_class():
    if not UTAH_STASH_CLASS:
        raise HomeDirException("UTAH_STASH_HOME is not set, app must call utah.core.bootstrap.set_app_home() before executing any operation")

    return UTAH_STASH_CLASS

def get_var_data_loc():
    if not UTAH_VARIABLE_DATA:
        raise HomeDirException("UTAH_VARIABLE_DATA is not set, app must call utah.core.bootstrap.set_app_home() before executing any operation")

    return UTAH_VARIABLE_DATA

