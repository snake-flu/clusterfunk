import dendropy
from clusterfunk.label_transitions import *


def run(options):
    tree = dendropy.Tree.get(path=options.input, schema="nexus")
    annotator = TransitionAnnotator(options.parent_state, options.child_state, options.trait)
    count = annotator.annotate_transitions(tree)

    print(count)

    tree.write(path=options.output, schema="nexus")
