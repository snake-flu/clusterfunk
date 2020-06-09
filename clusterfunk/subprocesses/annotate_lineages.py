from clusterfunk.utilities.subtyper import Subtyper
from clusterfunk.utilities.utils import prepare_tree, write_tree


def run(options):
    tree = prepare_tree(options, options.input)

    subtyper = Subtyper(tree, options.trait)

    write_tree(subtyper.tree, options)
