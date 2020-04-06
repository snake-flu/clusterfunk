from pkg_resources import get_distribution

try:
    __version__ = get_distribution("clusterfunk").version
except:
    __version__ = "local"

__all__ = ["phylotype", "annotate_tree", "extract_tip_annotations", "get_taxa", "label_transitions", "subtyper"]

from clusterfunk import *
