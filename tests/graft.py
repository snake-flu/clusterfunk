import unittest
import dendropy
import os

from clusterfunk.graft import RootStock

this_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(this_dir, "tests", 'data', 'graft')


class test_grafting_big_trees(unittest.TestCase):
    def setUp(self):
        tree = dendropy.Tree.get(data="((A:1,B:1):3,C:4);", schema="newick", rooting="default-rooted")
        self.rootStock = RootStock(tree)

    def test_tip_graft(self):
        incoming = dendropy.Tree.get(data="((aC:1,aB:1):3,A:4);", schema="newick", rooting="default-rooted")
        self.rootStock.graft(incoming)

        print(self.rootStock.tree.as_ascii_plot())
        self.assertTrue(True)

    def test_tip_graft(self):
        incoming = dendropy.Tree.get(data="((aC:1,aB:1):3,A:4);", schema="newick", rooting="default-rooted")
        incoming2 = dendropy.Tree.get(data="((a2C:1,a2B:1):3,A:4);", schema="newick", rooting="default-rooted")

        self.rootStock.graft(incoming)
        self.rootStock.graft(incoming2)

        print(self.rootStock.tree.as_ascii_plot())
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
