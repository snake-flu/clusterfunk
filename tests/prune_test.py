import os
import re
import unittest

import dendropy

from clusterfunk.prune import TreePruner

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
        self.tree.purge_taxon_namespace()

        self.assertEqual([taxon.label for taxon in self.tree.taxon_set], ["B", "C"])

    def test_extract(self):
        pruner = TreePruner(re.compile("(.*)"), re.compile("(.*)"), True)
        pruner.set_taxon_set(["A", "A2"])
        pruner.prune(self.tree)
        self.tree.purge_taxon_namespace()
        print(self.tree.as_ascii_plot())
        self.assertEqual([taxon.label for taxon in self.tree.taxon_set], ["A", "A2"])

if __name__ == '__main__':
    unittest.main()
