from clusterfunk.phylotype import *
from clusterfunk.utils import write_tree, prepare_tree


def run(options):
    tree = prepare_tree(options)
    phylotype_tree(tree, options.threshold, options.suffix)
    write_tree(tree, options.output, "nexus")
