import unittest

import dendropy

from clusterfunk.annotate_tree import TreeAnnotator


class AnnotationTest(unittest.TestCase):
    def setUp(self):
        self.tree = dendropy.Tree.get(data="((A|human:1,B|camel:1):3,C|bat:4,D|:4);", schema="newick")
        self.annotator = TreeAnnotator(self.tree)

    def test_annotation_from_dictionary(self):
        annotations = {"A|human": {"test": 1},
                       "B|camel": {"test": 1},
                       "C|bat": {"test": 2}}
        self.annotator.annotate_tips(annotations)
        self.assertEqual(self.tree.find_node_with_taxon_label("A|human").annotations.get_value("test"), 1)
        self.assertEqual(self.tree.find_node_with_taxon_label("C|bat").annotations.get_value("test"), 2)

    def test_annotation_from_tip_label(self):
        self.annotator.annotate_tips_from_label("host", 1, "|")
        self.annotator.annotate_tips_from_label("name", 0, "|")


        self.assertEqual(self.tree.find_node_with_taxon_label("A|human").annotations.get_value("host"), "human")
        self.assertEqual(self.tree.find_node_with_taxon_label("A|human").annotations.get_value("name"), "A")

        self.assertEqual(self.tree.find_node_with_taxon_label("D|").annotations.get_value("host"), None)
        self.assertEqual(self.tree.find_node_with_taxon_label("D|").annotations.get_value("name"), "D")




if __name__ == '__main__':
    unittest.main()
