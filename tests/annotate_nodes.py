import re
import unittest

import dendropy

from clusterfunk.annotate_tree import TreeAnnotator, get_annotations, push_trait_to_tips


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
        self.annotator.annotate_tips_from_label("host", re.compile(".*\|(.*)"))
        self.annotator.annotate_tips_from_label("name", re.compile("(.*)\|.*"))

        self.assertEqual(self.tree.find_node_with_taxon_label("A|human").annotations.get_value("host"), "human")
        self.assertEqual(self.tree.find_node_with_taxon_label("A|human").annotations.get_value("name"), "A")

        self.assertEqual(self.tree.find_node_with_taxon_label("D|").annotations.get_value("host"), None)
        self.assertEqual(self.tree.find_node_with_taxon_label("D|").annotations.get_value("name"), "D")

    def test_get_annotations(self):
        annotator = TreeAnnotator(self.tree, re.compile("(.*)\|.*"))

        raw_annotations = [{"index_column": "A-t", "value": "human", "ignore": "T"},
                           {"index_column": "C-t", "value": "bat"}]
        annotations = get_annotations(raw_annotations, "index_column", re.compile("(.+)-.*"), ["value"])
        annotator.annotate_tips(annotations)
        self.assertEqual(self.tree.find_node_with_taxon_label("A|human").annotations.get_value("value"), "human")
        self.assertEqual(self.tree.find_node_with_taxon_label("C|bat").annotations.get_value("value"), "bat")
        self.assertIsNone(self.tree.find_node_with_taxon_label("A|human").annotations.get_value("ignore"), "human")

    def test_boolean(self):
        annotations = {"A|human": {"test": 1},
                       "B|camel": {"test": 1},
                       "C|bat": {"test": 2}}
        self.annotator.annotate_tips(annotations)

        self.annotator.add_boolean_trait("test", "test_1", re.compile("1"))
        self.assertEqual(self.tree.find_node_with_taxon_label("A|human").annotations.get_value("test_1"), True)


    def test_push_annotations(self):
        annotations = {"A|human": {"test": "yes"},
                       "C|bat": {"test": "yes"}}
        self.annotator.annotate_tips(annotations)
        mrca = self.annotator.annotate_mrca("test", "yes")
        push_trait_to_tips(mrca, "test", "yes", lambda node: True)
        self.assertEqual(self.tree.find_node_with_taxon_label("B|camel").annotations.get_value("test"), "yes")

    def test_push_annotations_with_predicate(self):
        annotations = {"A|human": {"test": "yes"},
                       "C|bat": {"test": "yes"}}
        self.annotator.annotate_tips(annotations)
        mrca = self.annotator.annotate_mrca("test", "yes")
        A = self.tree.find_node_with_taxon_label('A|human')
        push_trait_to_tips(mrca, "test", "yes", lambda node: A not in node.child_nodes())
        self.assertIsNone(self.tree.find_node_with_taxon_label("B|camel").annotations.get_value("test"))
        self.assertEqual(self.tree.find_node_with_taxon_label("D|").annotations.get_value("test"), "yes")




if __name__ == '__main__':
    unittest.main()
