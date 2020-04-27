import copy
import os
import re
from multiprocessing.pool import ThreadPool
from functools import partial

from clusterfunk.prune import TreePruner
from clusterfunk.utils import prepare_tree


def prune_lineage(value, options):
    pruner = TreePruner(re.compile("(.*)"), re.compile("(.*)"), options.extract)
    tree_to_prune = prepare_tree(options, options.input)
    regex = re.compile(value)
    pruner.parse_by_trait_value(tree_to_prune, options.trait, regex)
    pruner.prune(tree_to_prune)
    tree_to_prune.write(path=options.output + "/" + options.trait + "_" + value + ".tree", schema="nexus")
    return value

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

        values = list(set([tip.annotations.get_value(options.trait) for tip in tree.leaf_node_iter() if
                           tip.annotations.get_value(options.trait) is not None]))
        prune_func = partial(prune_lineage, options=options)
        results = []
        with ThreadPool(options.threads) as pool:
            results.extend(pool.map(prune_func, values))

