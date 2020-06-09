import unittest

import dendropy

from clusterfunk.utilities.utils import SafeNodeAnnotator, collapse_nodes

text = "(((A[&test=1]:0.5,B:0.5):0.02,D:2):0.01,C:0.2);"
tree = dendropy.Tree.get_from_string(text, "newick")


class Options:
    def __init__(self):
        pass

    def set(self, key, value):
        setattr(self, key, value)


class MyTestCase(unittest.TestCase):
    def test_something(self):
        collapse_nodes(tree, 5E-2)
        self.assertEqual(4, tree.seed_node.num_child_nodes())

    def test_annotator(self):
        tree = dendropy.Tree.get_from_string(text, "newick")
        nodeAnnotator = SafeNodeAnnotator()
        nodeAnnotator.annotate(tree.find_node_with_taxon_label("A"), "test", 2)
        self.assertEqual(len(tree.find_node_with_taxon_label("A").annotations.findall(name='test')), 1)
        setattr(tree.find_node_with_taxon_label("A"), "test", 2)
        tree.find_node_with_taxon_label("A").annotations.add_bound_attribute("test")
        self.assertEqual(len(tree.find_node_with_taxon_label("A").annotations.findall(name='test')), 2)


if __name__ == '__main__':
    unittest.main()
