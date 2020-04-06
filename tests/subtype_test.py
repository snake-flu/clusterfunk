import unittest
import dendropy

from clusterfunk.subtyper import Subtyper


class MyTestCase(unittest.TestCase):
    def test_sibling(self):
        tree = dendropy.Tree.get(path="../test_files/representative_sequences.aln.fasta.nexus.tree", schema="nexus")
        subtyper = Subtyper(tree, 2, "|")

        self.assertEqual(subtyper.get_subtype("Iceland/222/2020|EPI_ISL_417837|B.1.8|Iceland|||2020-03-16"), "B.1.8")

    def test_nested_no_sibling(self):
        tree = dendropy.Tree.get(path="../test_files/representative_sequences.aln.fasta.nexus.tree", schema="nexus")
        subtyper = Subtyper(tree, 2, "|")

        self.assertEqual(subtyper.get_subtype("France/IDF2256/2020|EPI_ISL_416498|B.1.4|France|||2020-03-11"), "B.1.4")

    def test_between_clades_fall_back(self):
        tree = dendropy.Tree.get(path="../test_files/representative_sequences.aln.fasta.nexus.tree", schema="nexus")
        subtyper = Subtyper(tree, 2, "|")

        self.assertEqual(subtyper.get_subtype("USA/CZB-RR057-013/2020|EPI_ISL_417937|B.1.3|USA|||2020-03-18"), "B.1")


if __name__ == '__main__':
    unittest.main()
