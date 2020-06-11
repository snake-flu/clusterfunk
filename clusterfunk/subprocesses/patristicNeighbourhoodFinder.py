import copy
import os
import sys
from multiprocessing.pool import ThreadPool

import dendropy

from clusterfunk.subProcess import SubProcess
from clusterfunk.utilities.taxaFileParser import TaxaFileParser
from clusterfunk.utilities.treePruner import TreePruner


class PatristicNeighbourhoodFinder(SubProcess):
    def __init__(self, options):
        super().__init__(options)

        self.include_terminal_branch = options.include_terminal_branch if options.include_terminal_branch is not None else False
        self.threshold = options.threshold if options.threshold is not None else 0.00013
        self.branch_count = options.threshold if options.threshold is not None else False

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
        print("looking for %d taxa" % len(self.taxon_labels))
        i = 1
        for taxon_label in self.taxon_labels:

            sys.stdout.write('\r')
            sys.stdout.write(" %d%%" % (round((i / len(self.taxon_labels)) * 100)))

            currentNode = tree.find_node_with_taxon_label(taxon_label)
            if currentNode is not None:
                neighborhood = set()
                parent = currentNode.parent_node
                self.search_the_neighborhood(parent, currentNode, neighborhood)
                self.neighbours[taxon_label] = neighborhood
            else:
                print("%s not found in tree" % taxon_label)
            sys.stdout.flush()
            i += 1

        sys.stdout.write("\n")

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

    def search_the_neighborhood(self, node, previousNode, neighborhood, distance=0):
        if distance <= self.threshold:
            for child in node.child_node_iter():
                if child.is_leaf():
                    neighborhood.add(child.taxon.label)
            for child in node.child_node_iter(lambda n: n is not previousNode):
                self.searchForward(child, neighborhood, distance)

            if self.branch_count:
                distance += 1
            else:
                distance += node.edge.length
            if node.parent_node is not None:
                self.search_the_neighborhood(node.parent_node, node, neighborhood, distance)
        pass

    def searchForward(self, node, neighborhood, distance=0):
        if self.branch_count:
            distance += 1
        else:
            distance += node.edge.length
        if distance <= self.threshold:
            for child in node.child_node_iter():
                if child.is_leaf():
                    neighborhood.add(child.taxon.label)
                else:
                    self.searchForward(child, neighborhood, distance)
