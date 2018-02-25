# Let's import local settings if a file is available.
try:
    from .development_settings import *
except:
    from .production_settings import *
