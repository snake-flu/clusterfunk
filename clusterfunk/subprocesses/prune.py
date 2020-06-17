import copy
import os
import re
from collections import Counter
from multiprocessing.pool import ThreadPool

import dendropy

from clusterfunk.subProcess import SubProcess
from clusterfunk.utilities.treePruner import TreePruner


class PruneProcess(SubProcess):
    """
    The logic for pruning trees
    """

    def __init__(self, options):
        super().__init__(options)
        self.tree = None
        self.pruner = TreePruner(re.compile(self.options.parse_data),
                                 re.compile(self.options.parse_taxon),
                                 self.options.extract)
        self.parse_taxon()

    def parse_taxon(self):
        if self.options.fasta is not None:
            self.pruner.parse_fasta(self.options.fasta)
        elif self.options.metadata is not None:
            self.pruner.parse_metadata(self.options.metadata, self.options.index_column)
        elif self.options.taxon is not None:
            self.pruner.parse_taxon(self.options.taxon)

    def run(self, tree):
        self.tree = tree

        if self.options.where_trait is not None:
            for trait_pattern in self.options.where_trait:
                trait, pattern = trait_pattern.split("=")
                regex = re.compile(pattern)
                self.pruner.parse_by_trait_value(self.tree, trait, regex)

        if self.options.trait is None:
            self.prune_once()
        else:
            self.prune_for_each_trait()

    def prune_once(self):
        self.pruner.prune(self.tree)

    def prune_for_each_trait(self):
        self.handleOwnOutput = True
        if not os.path.exists(self.options.output):
            os.makedirs(self.options.output)

        values = Counter([tip.annotations.get_value(self.options.trait) for tip in self.tree.leaf_node_iter() if
                          tip.annotations.get_value(self.options.trait) is not None])

        no_singletons = [element for element, count in values.items() if count > 1]

        print("expecting %d trees" % len(no_singletons))
        subtrees = []
        mrcas = []
        for value in no_singletons:
            taxa = [n.taxon for n in
                    self.tree.leaf_node_iter(lambda n: n.annotations.get_value(self.options.trait) == value)]
            mrca = self.tree.mrca(taxa=taxa)
            mrcas.append(mrca)
            subtrees.append({"taxa": taxa, "mrca": mrca, "value": value})

        postorder_mrca = [node for node in self.tree.postorder_node_iter() if node in mrcas]

        subtrees.sort(key=lambda n: postorder_mrca.index(n["mrca"]))
        print("starting to prune")
        results = []
        with ThreadPool(self.options.threads) as pool:
            results.extend(pool.map(self.prune_lineage, subtrees))

    def prune_lineage(self, subtree):
        tree_to_prune = dendropy.Tree(seed_node=copy.deepcopy(subtree["mrca"]),
                                      taxon_namespace=dendropy.TaxonNamespace())

        thread_pruner = TreePruner(re.compile(self.options.parse_data),
                                   re.compile(self.options.parse_taxon),
                                   self.options.extract)

        thread_pruner.set_taxon_set([taxon.label for taxon in subtree["taxa"]])

        thread_pruner.prune(tree_to_prune)
        if self.options.out_format == "newick":
            tree_to_prune.write(path=self.options.output + "/" + self.options.trait + "_" + subtree["value"] + ".tree",
                                schema=self.options.out_format, suppress_rooting=True)
        else:
            tree_to_prune.write(path=self.options.output + "/" + self.options.trait + "_" + subtree["value"] + ".tree",
                                schema=self.options.out_format)
        return subtree["value"]
