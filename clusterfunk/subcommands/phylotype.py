from clusterfunk.phylotype import *
from clusterfunk.utils import write_tree, prepare_tree


def run(options):
    tree = prepare_tree(options, options.input)
    phylotype_tree(tree, options.threshold, options.prefix)
    write_tree(tree, options)
