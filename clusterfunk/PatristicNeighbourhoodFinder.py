import copy
import os
from multiprocessing.pool import ThreadPool

import dendropy

from clusterfunk.TaxaFileParser import TaxaFileParser
from clusterfunk.prune import TreePruner
from clusterfunk.subProcess import SubProcess


class PatristicNeighbourhoodFinder(SubProcess):
    def __init__(self, options):
        super().__init__(options)

        self.include_terminal_branch = options.include_terminal_branch if options.include_terminal_branch is not None else False
        self.threshold = options.threshold if options.threshold is not None else 0.00013

        self.taxon_labels = []
        self.taxon_sets = []
        self.eligible_taxa = []
        self.current_taxon_set = set()
        self.neighbours = {}
        self.tree = None

        self.pruner = TreePruner(extract=True)
        self.taxa_parser = TaxaFileParser(options.data_taxon_pattern)
        self.counter = 0
        self.handleOwnOutput = True

    def run(self, tree, results=None):

        self.taxon_labels = self.taxa_parser.smart_parse(self.options)
        self.eligible_taxa = self.taxon_labels
        self.tree = tree
        pdm = tree.phylogenetic_distance_matrix()

        for taxon_label in self.taxon_labels:
            taxon = tree.find_node_with_taxon_label(taxon_label).taxon
            self.neighbours[taxon_label] = {taxon_label}
            for taxon2 in tree.taxon_namespace:
                if taxon != taxon2:
                    weighted_patristic_distance = pdm.patristic_distance(taxon, taxon2)
                    if not self.include_terminal_branch:
                        weighted_patristic_distance -= tree.find_node_with_taxon_label(taxon.label).edge.length
                        weighted_patristic_distance -= tree.find_node_with_taxon_label(taxon2.label).edge.length

                    if weighted_patristic_distance < self.threshold:
                        self.neighbours[taxon_label].add(taxon2.label)

        while len(self.eligible_taxa) > 0:
            current_taxon = self.eligible_taxa.pop(0)
            self.current_taxon_set = self.neighbours[current_taxon]
            self.rally_the_neighbors(current_taxon)
            self.taxon_sets.append(self.current_taxon_set)

        print("found %d trees" % len(self.taxon_sets))
        if not os.path.exists(self.options.output):
            os.makedirs(self.options.output)
        results = []
        with ThreadPool(self.options.threads) as pool:
            results.extend(pool.map(self.prune_lineage, self.taxon_sets))

    def rally_the_neighbors(self, taxon1):
        for taxon2 in self.eligible_taxa:
            if len(self.neighbours[taxon1].intersection(self.neighbours[taxon2])) > 0:
                self.current_taxon_set.union(self.neighbours[taxon2])
                self.eligible_taxa.remove(taxon2)
                self.rally_the_neighbors(taxon2)

    def prune_lineage(self, taxon_set):
        taxon_list = list(taxon_set)
        mrca = self.tree.mrca(taxon_labels=taxon_list)
        tree_to_prune = dendropy.Tree(seed_node=copy.deepcopy(mrca),
                                      taxon_namespace=copy.deepcopy(dendropy.TaxonNamespace()))
        self.pruner.set_taxon_set(taxon_list)
        self.pruner.prune(tree_to_prune)
        self.counter += 1
        if self.options.out_format == "newick":
            tree_to_prune.write(path=self.options.output + "/" + "tree" + "_" + str(self.counter) + ".tree",
                                schema=self.options.out_format, suppress_rooting=True)
        else:
            tree_to_prune.write(path=self.options.output + "/" + "tree" + "_" + str(self.counter) + ".tree",
                                schema=self.options.out_format)
        return
