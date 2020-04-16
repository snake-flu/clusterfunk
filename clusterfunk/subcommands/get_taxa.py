from clusterfunk.utils import prepare_tree


def run(options):
    tree = prepare_tree(options, options.input)
    with open(options.output, "w") as text_file:
        for tip in tree.leaf_node_iter():
            text_file.write(tip.taxon.label + "\n")
