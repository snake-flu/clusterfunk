import csv

from clusterfunk.annotate_tree import TreeAnnotator, get_annotations, push_trait_to_tips
from clusterfunk.utils import prepare_tree


def run(options):
    tree = prepare_tree(options, options.input)
    annotator = TreeAnnotator(tree)

    def predicate(node):
        return True

    if options.filter is not None:
        key, value = options.filter.split("=")

        def predicate(node):
            return node.annotations.get_value(key) == value

    with open(options.traits_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        annotations = get_annotations("taxon", reader)
    annotator.annotate_tips(annotations)

    for trait_name in options.traits:
        #         get values or traits
        values = list(set([node.annotations.get_value(trait_name) for node in
                           tree.leaf_node_iter(lambda tip: tip.annotations.get_value(trait_name) is not None)]))

        for value in values:
            mrca = annotator.annotate_mrca(trait_name, value)
            push_trait_to_tips(mrca, trait_name, value, predicate)

    tree.write(path=options.output, schema="nexus")
