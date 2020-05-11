from clusterfunk.utils import prepare_tree, write_tree


def run(options):
    tree = prepare_tree(options)
    write_tree(tree, options)
