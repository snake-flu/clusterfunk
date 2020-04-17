import re

from clusterfunk.annotate_tree import *
import csv

from clusterfunk.utils import prepare_tree


def run(options):
    tree = prepare_tree(options, options.input)

    annotator = TreeAnnotator(tree, re.compile(options.parse_taxon))

    if options.traits_file is not None:
        get_data_key = re.compile(options.parse_data)

        with open(options.traits_file, newline='') as metadata:
            dialect = csv.Sniffer().sniff(metadata.read(1024))
            metadata.seek(0)
            reader = csv.DictReader(metadata, dialect=dialect)
            annotations = get_annotations(reader, options.index_column, get_data_key, options.trait_columns)
        annotator.annotate_tips(annotations)

    if options.from_taxon:
        for string in options.from_taxon:
            trait, regex = string.split("=")
            annotator.annotate_tips_from_label(trait, re.compile(regex))

    if options.where_trait is not None:
        for string in options.where_trait:
            boolean_trait_name, regex = string.split("=")
            trait = boolean_trait_name.split("_")[0]
            annotator.add_boolean_trait(trait, boolean_trait_name, re.compile(regex))

    if options.mrca is not None:
        for trait_name in options.mrca:
            #         get values ofr traits
            values = list(set([node.annotations.get_value(trait_name) for node in
                               tree.leaf_node_iter(lambda tip: tip.annotations.get_value(trait_name) is not None)]))

            for value in values:
                annotator.annotate_mrca(trait_name, value)

    tree.write(path=options.output, schema="nexus")
