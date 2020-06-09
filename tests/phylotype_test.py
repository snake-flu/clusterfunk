import unittest

import dendropy

from clusterfunk.phylotype import Phylotype
from tests.utils import Options


class PhylotypeTests(unittest.TestCase):
    def setUp(self):
        self.tree = dendropy.Tree.get(data="((A:1,B:1):3,C:4);", schema="newick")
        options = Options()
        options.set("threshold", 2)
        options.set("prefix", "p")

        self.phylotyper = Phylotype(options)

    def test_assigns_phylotype(self):
        self.phylotyper.run(self.tree)
        self.assertEqual(self.tree.find_node_with_taxon_label("A").annotations.get_value("phylotype"), '"p.1"')
        self.assertEqual(self.tree.find_node_with_taxon_label("B").annotations.get_value("phylotype"), '"p.1"')

    def test_no_singletons(self):
        self.phylotyper.run(self.tree)
        self.assertEqual(self.tree.find_node_with_taxon_label("C").annotations.get_value("phylotype"), '"p"')


if __name__ == '__main__':
    unittest.main()
