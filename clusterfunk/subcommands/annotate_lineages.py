import dendropy

from clusterfunk.utils import prepare_tree, write_tree
from clusterfunk.subtyper import Subtyper


def run(options):
    tree = prepare_tree(options, options.input)

    subtyper = Subtyper(tree, options.trait)

    write_tree(subtyper.tree, options)
