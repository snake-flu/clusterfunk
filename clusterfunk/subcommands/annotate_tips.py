import re
import warnings

from clusterfunk.annotate_tree import *
import csv

from clusterfunk.utils import prepare_tree


def run(options):
    tree = prepare_tree(options, options.input)

    if not options.verbose:
        warnings.filterwarnings("ignore")

    annotator = TreeAnnotator(tree, re.compile(options.parse_taxon))

    if options.traits_file is not None:
        get_data_key = re.compile(options.parse_data)

        with open(options.traits_file, "r") as metadata:
            dialect = csv.Sniffer().sniff(metadata.readline())
            metadata.seek(0)
            reader = csv.DictReader(metadata, dialect=dialect)
            annotations = get_annotations(reader, options.index_column, get_data_key, options.trait_columns)
        annotator.annotate_tips(annotations)

    if options.from_taxon:
        for string in options.from_taxon:
            trait, regex = string.split("=")
            annotator.annotate_tips_from_label(trait, re.compile(regex))
    i = 0
    if options.boolean_for_trait is not None:
        for string in options.boolean_for_trait:
            trait_name, regex = string.split("=")
            boolean_trait_name = options.boolean_trait_names[i] if len(
                    options.boolean_trait_names) > i else trait_name + "_boolean"
            annotator.add_boolean_trait(trait_name, boolean_trait_name, re.compile(regex))

    if options.mrca is not None:
        for trait_name in options.mrca:
            #         get values of traits
            values = list(set([node.annotations.get_value(trait_name) for node in
                               tree.leaf_node_iter(lambda tip: tip.annotations.get_value(trait_name) is not None)]))

            for value in values:
                annotator.annotate_mrca(trait_name, value)

    tree.write(path=options.output, schema="nexus")
