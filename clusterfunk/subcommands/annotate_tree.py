from clusterfunk.annotate_tree import *
import csv

from clusterfunk.utils import check_str_for_bool, prepare_tree


def run(options):
    if options.deltran and options.acctran:
        raise ValueError("Can not use both acctran and deltran flags")
    if options.traits_file is not None and options.indices is not None:
        raise ValueError("Can annotate from a file and tip labels at the same time. Run as two separate steps")

    tree = prepare_tree(options)
    annotator = TreeAnnotator(tree, options.majority_rule)

    if options.traits_file is not None:
        with open(options.traits_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            annotations = get_annotations("taxon", reader)
        annotator.annotate_tips(annotations)

    if options.indices is not None and options.separator is not None:
        for i in range(0, len(options.traits)):
            annotator.annotate_tips_from_label(options.traits[i], options.indices[i], options.separator)

    if options.values is not None:
        i = 0
        for trait in options.traits:
            value = options.values[i]
            annotator.add_boolean_trait(trait, value)
            i += 1

    if options.acctran or options.deltran:
        acctran = True if options.acctran else False

        if len(options.traits) > 0:
            i = 0
            for annotation in options.traits:
                ancestral_state = check_str_for_bool(options.ancestral_state[i]) if len(
                        options.ancestral_state) > i else None

                annotator.annotate_nodes_from_tips(annotation, acctran, ancestral_state)
                i += 1
    if options.mrca is not None:
        for trait_name in options.mrca:
            #         get values ofr traits
            values = list(set([node.annotations.get_value(trait_name) for node in
                               tree.leaf_node_iter(lambda tip: tip.annotations.get_value(trait_name) is not None)]))

            for value in values:
                annotator.annotate_mrca(trait_name, value)

    tree.write(path=options.output, schema="nexus")
