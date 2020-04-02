import dendropy
import os
from clusterfunk.label_transitions import *


def run(options):
    tree = dendropy.Tree.get(path=options.input, schema="nexus")
    annotator = TransitionAnnotator(options.parent_state, options.child_state, options.trait)

    if options.exploded_trees:
        trees = annotator.split_at_transitions(tree)
        print(len(trees))
        if not os.path.exists(options.output):
            os.makedirs(options.output)
        i = 1
        for tree in trees:
            label = tree.seed_node.annotations.get_value("introduction")  # TODO remove hardcoded label
            tree.write(path=options.output + "/" + label + '.tree', schema="nexus")
            i += 1

    else:
        count = annotator.annotate_transitions(tree)
        print(count)
        tree.write(path=options.output, schema="nexus")
