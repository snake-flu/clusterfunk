import csv
import re

from clusterfunk.annotate_tree import TreeAnnotator, push_trait_to_tips
from clusterfunk.utils import prepare_tree, write_tree


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
        values.sort()
        for value in values:
            taxon_set = [tip.taxon for tip in
                         tree.leaf_node_iter(lambda node: node.annotations.get_value(trait_name) == value)]
            mrca = tree.mrca(taxa=taxon_set)
            push_trait_to_tips(mrca, trait_name, value, predicate)

    write_tree(tree, options)
