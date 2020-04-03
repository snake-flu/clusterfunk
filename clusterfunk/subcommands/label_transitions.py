import dendropy
import os
from clusterfunk.label_transitions import *
from clusterfunk.utils import check_str_for_bool


def run(options):
    tree = dendropy.Tree.get(path=options.input, schema="nexus")
    annotator = TransitionAnnotator(check_str_for_bool(options.parent_state), check_str_for_bool(options.child_state),
                                    options.trait, options.include_parent)

    if options.exploded_trees:
        trees = annotator.split_at_transitions(tree)
        print(len(trees))
        if not os.path.exists(options.output):
            os.makedirs(options.output)
        i = 1
        for tree in trees:
            tree["tree"].write(path=options.output + "/" + tree["id"] + '.tree', schema="nexus")
            i += 1

    else:
        count = annotator.annotate_transitions(tree)
        print(count)
        tree.write(path=options.output, schema="nexus")
