import unittest

import dendropy

from clusterfunk.utils import collapse_nodes

text = "(((A:0.5,B:0.5):0.02,D:2):0.01,C:0.2);"
tree = dendropy.Tree.get_from_string(text, "newick")


class MyTestCase(unittest.TestCase):
    def test_something(self):
        collapse_nodes(tree, 5E-2)
        self.assertEqual(4, tree.seed_node.num_child_nodes())


if __name__ == '__main__':
    unittest.main()
