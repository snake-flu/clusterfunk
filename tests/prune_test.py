import unittest
import os

from clusterfunk.prune import parse_taxon_set

this_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(this_dir, "tests", 'data', 'prune')

true_taxon_set = ["virus1||B.1|country|admin1|admin0|date", "virus3||B.1|country|admin1|admin0|date",
                  "virus5||B.1|country|admin1|admin0|date", "virus10||B.1|country|admin1|admin0|date"]


class Prune_tests(unittest.TestCase):

    def test_fasta_parse(self):
        file = "%s/taxon.fasta" % data_dir
        taxon_set = parse_taxon_set(file, "fasta")

        self.assertEqual(taxon_set, true_taxon_set)

    def test_txt_parse(self):
        file = "%s/taxon.txt" % data_dir
        taxon_set = parse_taxon_set(file, "txt")

        self.assertEqual(taxon_set, true_taxon_set)

    def test_csv_parse(self):
        file = "%s/taxon.csv" % data_dir
        taxon_set = parse_taxon_set(file, "metadata", "taxon")
        self.assertEqual(taxon_set, true_taxon_set)

    def test_tsv_parse(self):
        file = "%s/taxon.tsv" % data_dir
        taxon_set = parse_taxon_set(file, "metadata", "taxon")
        self.assertEqual(taxon_set, true_taxon_set)


if __name__ == '__main__':
    unittest.main()
