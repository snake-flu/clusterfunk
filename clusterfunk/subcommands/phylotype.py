from clusterfunk.phylotype import *
from clusterfunk.utils import parse_tree, write_tree, prepare_tree


def run(options):
    tree = prepare_tree(options)
    phylotype_tree(tree, options.threshold)
    write_tree(tree, options.output, options.format)
