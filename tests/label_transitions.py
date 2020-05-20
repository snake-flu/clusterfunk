import unittest

import dendropy

from clusterfunk.label_transitions import TransitionAnnotator


class TransitionTest(unittest.TestCase):
    def setUp(self):
        self.tree = dendropy.Tree.get(
            data="((watch_out_polytomy[&country=The_Shire],A|human[&country=UK]:1,(B|camel[&country=US]:1,(G[&country=UK]:1,F[&country=US]:2)[&country=US])[&country=US]:1,H[&country=UK]:1)[&country=UK]:3,"
                 "C|bat[&country=UK]:4)[&country=China];", schema="newick")
        self.transition_annotator = TransitionAnnotator("country", False, "introduction", "introduction")

    def test_transitions_from(self):
        count = self.transition_annotator.annotate_transitions(self.tree, From="China")
        self.assertEqual(count, 2)
        self.assertEqual(self.tree.find_node_with_taxon_label("C|bat").annotations.get_value("introduction"),
                         "introduction2")
        self.assertEqual(self.tree.find_node_with_taxon_label("A|human").annotations.get_value("introduction"),
                         "introduction1")

    def test_transitions_to(self):
        count = self.transition_annotator.annotate_transitions(self.tree, to="UK")
        self.assertEqual(self.tree.find_node_with_taxon_label("G").annotations.get_value("introduction"),
                         "introduction2")
        self.assertEqual(count, 3)
        self.assertEqual(self.tree.find_node_with_taxon_label("C|bat").annotations.get_value("introduction"),
                         "introduction3")
        self.assertEqual(self.tree.find_node_with_taxon_label("A|human").annotations.get_value("introduction"),
                         "introduction1")
        self.assertIsNone(self.tree.find_node_with_taxon_label("B|camel").annotations.get_value("introduction"))

    def test_transitions_to_from(self):
        count = self.transition_annotator.annotate_transitions(self.tree, From="Italy", to="UK")
        self.assertEqual(count, 0)
        self.assertIsNone(self.tree.find_node_with_taxon_label("B|camel").annotations.get_value("introduction"))
        self.assertIsNone(self.tree.find_node_with_taxon_label("A|human").annotations.get_value("introduction"))
        self.assertIsNone(self.tree.find_node_with_taxon_label("C|bat").annotations.get_value("introduction"))

    def test_stubborn(self):
        tree_string = "((A[&t=1],(A1[&t=1],B[&t=0])[&t=0])[&t=1],(C[&t=1],D[&t=0])[&t=0])[&t=0];"
        tree = dendropy.Tree.get(data=tree_string, schema="newick")
        transition_annotator = TransitionAnnotator("t", False, "introduction", "introduction", stubborn=True)
        count = transition_annotator.annotate_transitions(tree, to="1")
        self.assertEqual(count, 2)
        self.assertEqual(tree.find_node_with_taxon_label("A").annotations.get_value("introduction"),
                         tree.find_node_with_taxon_label("A1").annotations.get_value("introduction"))
    def test_not_stubborn(self):
        tree_string = "((A[&t=1],(A1[&t=1],B[&t=0])[&t=0])[&t=1],(C[&t=1],D[&t=0])[&t=0])[&t=0];"
        tree = dendropy.Tree.get(data=tree_string, schema="newick")
        transition_annotator = TransitionAnnotator("t", False, "introduction", "introduction", stubborn=False)
        count = transition_annotator.annotate_transitions(tree, to="1")
        self.assertEqual(count, 3)
        self.assertNotEqual(tree.find_node_with_taxon_label("A").annotations.get_value("introduction"),
                         tree.find_node_with_taxon_label("A1").annotations.get_value("introduction"))

if __name__ == '__main__':
    unittest.main()
