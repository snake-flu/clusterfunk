import csv

import dendropy

from clusterfunk.subProcess import SubProcess
from clusterfunk.utilities.taxaFileParser import TaxaFileParser


class TreeFocuser(SubProcess):
    def __init__(self, options):
        super().__init__(options)
        self.protected_taxa = []
        self.protected_ancestor = set()
        self.taxa_parser = TaxaFileParser(options.data_taxon_pattern)
        self.log = []
        self.count = 0
        self.nameSpace = None

    def run(self, tree):
        self.protected_taxa = self.taxa_parser.smart_parse(self.options)
        self.nameSpace = tree.taxon_namespace

        for taxon_label in self.protected_taxa:
            node = tree.find_node_with_taxon_label(taxon_label)
            if node is not None:
                for ancestor in node.ancestor_iter(inclusive=True):
                    self.protected_ancestor.add(ancestor)

        self.collapse_chaff(tree.seed_node)

        if self.options.tsv_file is not None:
            with open(self.options.tsv_file, 'w', newline='') as tsv_file:
                fieldnames = ['taxon', 'members']
                writer = csv.DictWriter(tsv_file, delimiter="\t", fieldnames=fieldnames)
                writer.writeheader()
                for row in self.log:
                    writer.writerow(row)

    def cleanup(self, tree):
        tree.purge_taxon_namespace()

    def collapse_chaff(self, node):

        removed_labels = []
        to_be_removed = []

        number_of_disappointing_leafs = len(
                [child for child in node.child_node_iter(lambda n: n not in self.protected_ancestor and n.is_leaf())])

        for disappointing_child in node.child_node_iter(lambda n: n not in self.protected_ancestor):

            # How many are leafs? if above threshold collapse
            if number_of_disappointing_leafs > self.options.collapse_threshold:
                if disappointing_child.is_leaf():
                    removed_labels.append(disappointing_child.taxon.label)
                    to_be_removed.append(disappointing_child)

            if not disappointing_child.is_leaf():
                # How many are leafs? if above threshold collapse
                number_of_disappointing_descendents = len([child for child in disappointing_child.leaf_iter()])
                if number_of_disappointing_descendents > self.options.collapse_threshold:
                    for leaf in disappointing_child.leaf_iter():
                        removed_labels.append(leaf.taxon.label)
                        # to_be_removed.append(disappointing_child)
                    to_be_removed.append(disappointing_child)

        if len(to_be_removed) > 0:
            for disappointing_child in to_be_removed:
                node.remove_child(disappointing_child)
            new_label = "inserted_node%d" % self.count
            self.log.append({"taxon": new_label, "members": ",".join(removed_labels)})
            new_taxon = dendropy.datamodel.taxonmodel.Taxon(label=new_label)
            self.nameSpace.add_taxon(new_taxon)
            node.insert_new_child(0, edge_length=0, taxon=new_taxon)
            self.count += 1

        for favorite_child in node.child_node_iter():
            self.collapse_chaff(favorite_child)

