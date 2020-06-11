import csv
import statistics

import dendropy

from clusterfunk.subProcess import SubProcess
from clusterfunk.utilities.taxaFileParser import TaxaFileParser


class PolytomySummarizer(SubProcess):
    def __init__(self, options):
        super().__init__(options)
        self.protected_taxa = []
        self.taxa_parser = TaxaFileParser(options.data_taxon_pattern)
        self.log = []
        self.count = 0
        self.nameSpace = None

    def run(self, tree):
        self.protected_taxa = self.taxa_parser.smart_parse(self.options)
        self.nameSpace = tree.taxon_namespace

        self.collapse_polytomies(tree.seed_node)

        if self.options.tsv_file is not None:
            with open(self.options.tsv_file, 'w', newline='') as tsv_file:
                fieldnames = ['taxon', 'members']
                writer = csv.DictWriter(tsv_file, delimiter="\t", fieldnames=fieldnames)
                writer.writeheader()
                for row in self.log:
                    writer.writerow(row)

    def cleanup(self, tree):
        tree.purge_taxon_namespace()

    def collapse_polytomies(self, node):
        leaf_children = [n for n in
                         node.child_node_iter(lambda n: n.is_leaf() and not n.taxon.label in self.protected_taxa)]
        if len(leaf_children) > 2:
            lengths = []
            removed = []
            for child in leaf_children:
                lengths.append(child.edge.length)
                removed.append(child.taxon.label)
                node.remove_child(child)

            new_label = "inserted_node%d" % self.count
            self.log.append({"taxon": new_label, "members": ",".join(removed)})
            new_taxon = dendropy.datamodel.taxonmodel.Taxon(label=new_label)
            self.nameSpace.add_taxon(new_taxon)
            node.insert_new_child(0, edge_length=statistics.mean(lengths), taxon=new_taxon)
            self.count += 1

        for child in node.child_node_iter(lambda n: not n.is_leaf()):
            self.collapse_polytomies(child)
