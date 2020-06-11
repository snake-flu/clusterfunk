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
        self.eligible_taxa = self.taxon_labels  # TODO make this more robust copy?
        self.tree = tree
        print("looking for %d taxa" % len(self.taxon_labels))
        i = 1
        for taxon_label in self.taxon_labels:

            sys.stdout.write('\r')
            sys.stdout.write(" %d%%" % (round((i / len(self.taxon_labels)) * 100)))

            currentNode = tree.find_node_with_taxon_label(taxon_label)
            if currentNode is not None:
                neighborhood = set([currentNode])
                parent = currentNode.parent_node
                self.search_the_neighborhood(parent, currentNode, neighborhood)
                self.neighbours[taxon_label] = neighborhood
            else:
                print("%s not found in tree" % taxon_label)
            sys.stdout.flush()
            # print("%s neighborhood size: %d" % (taxon_label, len(neighborhood)))
            # print("with %d tips" % (len([x for x in neighborhood if x.is_leaf()])))

            i += 1

        sys.stdout.write("\n")

        while len(self.eligible_taxa) > 0:
            current_taxon = self.eligible_taxa.pop(0)
            self.current_taxon_set = self.neighbours[current_taxon]
            found_overlap = True
            while found_overlap:
                found_overlap = False
                to_remove = []
                for taxon2 in self.eligible_taxa:
                    if len(self.current_taxon_set.intersection(self.neighbours[taxon2])) > 0:
                        self.current_taxon_set = self.current_taxon_set.union(self.neighbours[taxon2])
                        found_overlap = True
                        to_remove.append(taxon2)
                for over_lapping_taxon in to_remove:
                    self.eligible_taxa.remove(over_lapping_taxon)

            self.taxon_sets.append(self.current_taxon_set)

        # print("found %d trees" % len(self.taxon_sets))
        # print("tips: %d and %d" % (len([x for x in self.taxon_sets[0] if x.is_leaf()]),
        #                            len([x for x in self.taxon_sets[1] if x.is_leaf()])))

        if not os.path.exists(self.options.output):
            os.makedirs(self.options.output)
        results = []
        with ThreadPool(self.options.threads) as pool:
            results.extend(pool.map(self.prune_lineage, self.taxon_sets))


    def prune_lineage(self, nodes):
        mrca = min(nodes, key=lambda n: n.level())
        taxon_labels = [node.taxon.label for node in nodes if node.is_leaf()]
        tree_to_prune = dendropy.Tree(seed_node=copy.deepcopy(mrca),
                                      taxon_namespace=dendropy.TaxonNamespace())
        self.pruner.set_taxon_set(taxon_labels)
        self.pruner.prune(tree_to_prune)
        tree_to_prune.purge_taxon_namespace()

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
            neighborhood.add(node)
            for child in node.child_node_iter():
                if child.is_leaf():
                    neighborhood.add(child)
            for child in node.child_node_iter(lambda n: n is not previousNode):
                self.searchForward(child, neighborhood, distance)

            if self.branch_count:
                distance += 1
            else:
                distance += node.edge.length
            if node.parent_node is not None:
                self.search_the_neighborhood(node.parent_node, node, neighborhood, distance)

    def searchForward(self, node, neighborhood, distance=0):
        if self.branch_count:
            distance += 1
        else:
            distance += node.edge.length
        if distance <= self.threshold:
            neighborhood.add(node)
            for child in node.child_node_iter():
                if child.is_leaf():
                    neighborhood.add(child)
                else:
                    self.searchForward(child, neighborhood, distance)
