import copy
import os
import re

from clusterfunk.prune import TreePruner
from clusterfunk.utils import prepare_tree


def run(options):
    tree = prepare_tree(options, options.input)

    if options.trait is None:
        pruner = TreePruner(re.compile(options.parse_data), re.compile(options.parse_taxon), options.extract)
        if options.fasta is not None:
            pruner.parse_fasta(options.fasta)
        elif options.metadata is not None:
            pruner.parse_metadata(options.metadata, options.index_column)
        elif options.taxon is not None:
            pruner.parse_taxon(options.taxon)
        elif options.where_trait is not None:
            for trait_pattern in options.where_trait:
                trait, pattern = trait_pattern.split("=")
                regex = re.compile(pattern)
                pruner.parse_by_trait_value(tree, trait, regex)

        pruner.prune(tree)

        tree.write(path=options.output, schema="nexus")
    else:
        if not os.path.exists(options.output):
            os.makedirs(options.output)

        values = [tip.annotations.get_value(options.trait) for tip in tree.leaf_node_iter() if
                  tip.annotations.get_value(options.trait) is not None]

        for value in values:
            pruner = TreePruner(re.compile("(.*)"), re.compile("(.*)"), options.extract)
            copy_tree = copy.deepcopy(tree)
            regex = re.compile(value)
            pruner.parse_by_trait_value(copy_tree, options.trait, regex)
            pruner.prune(copy_tree)
            copy_tree.write(path=options.output + "/" + options.trait + "_" + value + ".tree", schema="nexus")
