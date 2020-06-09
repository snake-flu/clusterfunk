from pkg_resources import get_distribution

try:
    __version__ = get_distribution("clusterfunk").version
except:
    __version__ = "local"

__all__ = ["Main", "subProcess"]

from clusterfunk import *
