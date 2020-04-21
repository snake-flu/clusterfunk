import csv
import re

from clusterfunk.annotate_tree import TreeAnnotator, push_trait_to_tips
from clusterfunk.utils import prepare_tree


def run(options):
    tree = prepare_tree(options, options.input)
    annotator = TreeAnnotator(tree)

    def predicate(node):
        return True

    if options.stop_where_trait is not None:
        key, regex = options.stop_where_trait.split("=")
        matcher = re.compile(regex)

        def predicate(node):
            return False if matcher.match(str(node.annotations.get_value(key))) else True

    for trait_name in options.traits:
        #         get values or traits
        values = list(set([node.annotations.get_value(trait_name) for node in
                           tree.leaf_node_iter(lambda tip: tip.annotations.get_value(trait_name) is not None)]))
        for value in values:
            mrca = annotator.annotate_mrca(trait_name, value)
            push_trait_to_tips(mrca, trait_name, value, predicate)

    tree.write(path=options.output, schema="nexus")
