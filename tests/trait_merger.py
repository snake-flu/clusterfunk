import unittest

import dendropy

from clusterfunk.trait_merger import Merger


class MyTestCase(unittest.TestCase):
    def setUp(self):
        tree_string="((A[&t=1],(A1[&t=2],A2[&t=3],B),A3[&t=4]),(C[&t=5],D));"
        self.tree = dendropy.Tree.get(data=tree_string,schema="newick")
        self.A = self.tree.find_node_with_taxon_label("A")
        self.A1 = self.tree.find_node_with_taxon_label("A1")
        self.A2 = self.tree.find_node_with_taxon_label("A2")
        self.A3 = self.tree.find_node_with_taxon_label("A3")
    def test_merge(self):
        merger = Merger("t","lineage")
        merger.merge(self.tree)
        self.assertEqual(self.A1.annotations.get_value("lineage"), self.A2.annotations.get_value("lineage"))
        self.assertNotEqual(self.A.annotations.get_value("lineage"), self.A2.annotations.get_value("lineage"))
        self.assertNotEqual(self.A.annotations.get_value("lineage"), self.A3.annotations.get_value("lineage"))
    def test_merge_2(self):
        merger = Merger("t","lineage",max_merge=2)
        merger.merge(self.tree)
        self.assertEqual(self.A1.annotations.get_value("lineage"), self.A2.annotations.get_value("lineage"))
        self.assertNotEqual(self.A.annotations.get_value("lineage"), self.A2.annotations.get_value("lineage"))
        self.assertEqual(self.A.annotations.get_value("lineage"), self.A3.annotations.get_value("lineage"))
    def test_merge_0(self):
        merger = Merger("t","lineage",max_merge=0)
        merger.merge(self.tree)
        self.assertNotEqual(self.A1.annotations.get_value("lineage"), self.A2.annotations.get_value("lineage"))
        self.assertNotEqual(self.A.annotations.get_value("lineage"), self.A2.annotations.get_value("lineage"))
        self.assertNotEqual(self.A.annotations.get_value("lineage"), self.A3.annotations.get_value("lineage"))
if __name__ == '__main__':
    unittest.main()
