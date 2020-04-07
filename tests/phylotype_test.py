import unittest

import dendropy

from clusterfunk.phylotype import phylotype_tree


class PhylotypeTests(unittest.TestCase):
    def setUp(self):
        self.tree = dendropy.Tree.get(data="((A:1,B:1):3,C:4);", schema="newick")

    def test_assigns_phylotype(self):
        phylotype_tree(self.tree, 2)
        self.assertEqual(self.tree.find_node_with_taxon_label("A").annotations.get_value("phylotype"), '"p.1"')
        self.assertEqual(self.tree.find_node_with_taxon_label("B").annotations.get_value("phylotype"), '"p.1"')

    def test_no_singletons(self):
        phylotype_tree(self.tree, 2)
        self.assertEqual(self.tree.find_node_with_taxon_label("C").annotations.get_value("phylotype"), '"p"')


if __name__ == '__main__':
    unittest.main()
