import os
import re
from collections import Counter
import copy
from multiprocessing.pool import ThreadPool
from functools import partial

import dendropy

from clusterfunk.prune import TreePruner
from clusterfunk.utils import prepare_tree


def prune_lineage(subtree, options):
    tree_to_prune = dendropy.Tree(seed_node=copy.deepcopy(subtree["mrca"]),
                                  taxon_namespace=dendropy.TaxonNamespace())
    pruner = TreePruner(re.compile("(.*)"), re.compile("(.*)"), options.extract)
    pruner.set_taxon_set([taxon.label for taxon in subtree["taxa"]])
    pruner.prune(tree_to_prune)
    tree_to_prune.write(path=options.output + "/" + options.trait + "_" + subtree["value"] + ".tree",
                        schema="nexus")
    return subtree["value"]


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

        values = Counter([tip.annotations.get_value(options.trait) for tip in tree.leaf_node_iter() if
                          tip.annotations.get_value(options.trait) is not None])

        no_singletons = [element for element, count in values.items() if count > 1]

        print("expecting %d trees" % len(no_singletons))
        subtrees = []
        mrcas = []
        for value in no_singletons:
            taxa = [n.taxon for n in tree.leaf_node_iter(lambda n: n.annotations.get_value(options.trait) == value)]
            mrca = tree.mrca(taxa=taxa)
            mrcas.append(mrca)
            subtrees.append({"taxa": taxa, "mrca": mrca, "value": value})

        postorder_mrca = [node for node in tree.postorder_node_iter() if node in mrcas]

        subtrees.sort(key=lambda n: postorder_mrca.index(n["mrca"]))

        print("starting to prune")
        prune_func = partial(prune_lineage, options=options)
        results = []
        with ThreadPool(options.threads) as pool:
            results.extend(pool.map(prune_func, subtrees))
