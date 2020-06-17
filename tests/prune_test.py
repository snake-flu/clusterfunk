import copy
import os
import re
import unittest

import dendropy

from clusterfunk.utilities.treePruner import TreePruner

this_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(this_dir, "tests", 'data', 'prune')

true_taxon_set = ["virus1||B.1|country|admin1|admin0|date", "virus3||B.1|country|admin1|admin0|date",
                  "virus5||B.1|country|admin1|admin0|date", "virus10||B.1|country|admin1|admin0|date"]


class Prune_tests(unittest.TestCase):
    def setUp(self):
        self.tree = dendropy.Tree.get(data="((A:1,B:1,A2):3:1,C:4);", schema="newick")

    #
    # def test_fasta_parse(self):
    #     file = "%s/taxon.fasta" % data_dir
    #     taxon_set = parse_taxon_set(file, "fasta")
    #
    #     self.assertEqual(taxon_set, true_taxon_set)
    #
    # def test_txt_parse(self):
    #     file = "%s/taxon.txt" % data_dir
    #     taxon_set = parse_taxon_set(file, "txt")
    #
    #     self.assertEqual(taxon_set, true_taxon_set)
    #
    # def test_csv_parse(self):
    #     file = "%s/taxon.csv" % data_dir
    #     taxon_set = parse_taxon_set(file, "metadata", "taxon")
    #     self.assertEqual(taxon_set, true_taxon_set)
    #
    # def test_tsv_parse(self):
    #     file = "%s/taxon.tsv" % data_dir
    #     taxon_set = parse_taxon_set(file, "metadata", "taxon")
    #     self.assertEqual(taxon_set, true_taxon_set)

    def test_prune(self):
        pruner = TreePruner(re.compile("(.*)"), re.compile("(.*)"), False)
        pruner.set_taxon_set(["A", "A2"])
        pruner.prune(self.tree)

        self.assertEqual([taxon.label for taxon in self.tree.taxon_set], ["B", "C"])

    def test_extract(self):
        pruner = TreePruner(re.compile("(.*)"), re.compile("(.*)"), True)
        pruner.set_taxon_set(["A", "A2"])
        pruner.prune(self.tree)
        print(self.tree.as_ascii_plot())

        self.assertEqual([taxon.label for taxon in self.tree.taxon_set], ["A", "A2"])

    def test_multiplePrune(self):
        pruner = TreePruner(re.compile("(.*)"), re.compile("(.*)"), True)

        pruner.set_taxon_set(["B", "C"])
        mrca = self.tree.mrca(taxa=[n.taxon for n in self.tree.leaf_node_iter() if n.taxon.label in ["B", "C"]])
        tree_to_prune2 = dendropy.Tree(seed_node=copy.deepcopy(mrca),
                                       taxon_namespace=dendropy.TaxonNamespace())

        pruner.prune(tree_to_prune2)

        pruner.set_taxon_set(["A", "A2"])

        mrca = self.tree.mrca(taxa=[n.taxon for n in self.tree.leaf_node_iter() if n.taxon.label in ["A", "A2"]])
        tree_to_prune = dendropy.Tree(seed_node=copy.deepcopy(mrca),
                                      taxon_namespace=dendropy.TaxonNamespace())
        pruner.prune(tree_to_prune)
        self.assertEqual([taxon.label for taxon in tree_to_prune.taxon_namespace], ["A", "A2"])

        pruner.set_taxon_set(["B", "C"])
        mrca = self.tree.mrca(taxa=[n.taxon for n in self.tree.leaf_node_iter() if n.taxon.label in ["B", "C"]])
        tree_to_prune2 = dendropy.Tree(seed_node=copy.deepcopy(mrca),
                                       taxon_namespace=dendropy.TaxonNamespace())

        pruner.prune(tree_to_prune2)

        self.assertEqual([taxon.label for taxon in tree_to_prune2.taxon_namespace], ["B", "C"])

        self.assertEqual([taxon.label for taxon in self.tree.taxon_namespace], ["A", "B", "A2", "C"])

    # def test_prune_by_triats(self):


if __name__ == '__main__':
    unittest.main()
