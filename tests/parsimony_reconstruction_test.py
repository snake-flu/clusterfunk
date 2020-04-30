import unittest
from clusterfunk import annotate_tree
import dendropy


class TestFitch(unittest.TestCase):
    def setUp(self):
        tree = dendropy.Tree.get_from_string("(A:1,(B:1,(C:1,(D:1,E:1):1):1):1);", "newick")
        self.PR = annotate_tree.TreeAnnotator(tree)

    def test_annotations(self):
        self.PR.annotate_node("A", {"UK": False})
        node = self.PR.tree.find_node_with_taxon(lambda taxon: True if taxon.label == "A" else False)
        self.assertEqual(node.annotations.get_value("UK"), False)

    def test_fitch_parsimony(self):
        self.PR.annotate_node("D", {"UK": True})
        self.PR.annotate_node("E", {"UK": True})
        self.PR.annotate_node("C", {"UK": True})
        self.PR.annotate_node("B", {"UK": False})
        self.PR.annotate_node("A", {"UK": False})

        firstNode = self.PR.tree.find_node_with_taxon(lambda taxon: True if taxon.label == "D" else False).parent_node
        conflict = self.PR.tree.find_node_with_taxon(lambda taxon: True if taxon.label == "B" else False).parent_node

        self.PR.fitch_parsimony(self.PR.tree.seed_node, "UK")
        print(self.PR.tree.as_string('nexus'))

        self.assertEqual(True, firstNode.annotations.get_value("UK"))
        self.assertEqual([False, True], conflict.annotations.get_value("UK"))

    def test_accTrans(self):
        self.PR.annotate_node("D", {"UK": False})
        self.PR.annotate_node("E", {"UK": False})
        self.PR.annotate_node("C", {"UK": True})
        self.PR.annotate_node("B", {"UK": True})
        self.PR.annotate_node("A", {"UK": False})

        root = self.PR.tree.seed_node
        self.PR.fitch_parsimony(root, "UK")

        self.PR.reconstruct_ancestors(root, [False], True, "UK")
        print(self.PR.tree.as_string('nexus'))

        conflict = self.PR.tree.find_node_with_taxon(lambda taxon: True if taxon.label == "C" else False).parent_node
        conflict2 = self.PR.tree.find_node_with_taxon(lambda taxon: True if taxon.label == "B" else False).parent_node
        self.assertEqual(False, root.annotations.get_value("UK"))
        self.assertEqual(True, conflict.annotations.get_value("UK"))
        self.assertEqual(True, conflict2.annotations.get_value("UK"))

    def test_delTrans(self):
        self.PR.annotate_node("D", {"UK": False})
        self.PR.annotate_node("E", {"UK": False})
        self.PR.annotate_node("C", {"UK": True})
        self.PR.annotate_node("B", {"UK": True})
        self.PR.annotate_node("A", {"UK": False})
        root = self.PR.tree.seed_node
        self.PR.fitch_parsimony(root, "UK")

        self.PR.reconstruct_ancestors(root, [False], False, "UK")
        print(self.PR.tree.as_string('nexus'))

        conflict = self.PR.tree.find_node_with_taxon(lambda taxon: True if taxon.label == "B" else False).parent_node
        conflict2 = self.PR.tree.find_node_with_taxon(lambda taxon: True if taxon.label == "C" else False).parent_node

        self.assertEqual(False, root.annotations.get_value("UK"))
        self.assertEqual(False, conflict.annotations.get_value("UK"))
        self.assertEqual(False, conflict2.annotations.get_value("UK"))

    def test_polytomy(self):
        text = "(A[&t=1]:1,(B[&t=1]:1,(C[&t=1]:1,(D[&t=1]:1,E[&t=1]:1,G[&t=2]:1):1):1):1);"
        polytomy = dendropy.Tree.get_from_string(text, "newick")
        annotator = annotate_tree.TreeAnnotator(polytomy)
        annotator.fitch_parsimony(polytomy.seed_node, "t")
        self.assertEqual(polytomy.find_node_with_taxon_label("D").parent_node.annotations.get_value("t"), ["1", "2"])

    def test_polytomy_majority(self):
        text = "(A[&t=1]:1,(B[&t=1]:1,(C[&t=1]:1,(D[&t=1]:1,E[&t=1]:1,G[&t=2]:1):1):1):1);"
        polytomy = dendropy.Tree.get_from_string(text, "newick")
        annotator = annotate_tree.TreeAnnotator(polytomy, True)
        annotator.fitch_parsimony(polytomy.seed_node, "t")
        self.assertEqual(polytomy.find_node_with_taxon_label("D").parent_node.annotations.get_value("t"), "1")

    def test_polytomy_maxtrans(self):
        text = "(A[&t=2]:1,(B[&t=2]:1,(C[&t=2]:1,(D[&t=1]:1,E[&t=1]:1,G[&t=2]:1):1):1):1);"
        polytomy = dendropy.Tree.get_from_string(text, "newick")
        annotator = annotate_tree.TreeAnnotator(polytomy, True)
        annotator.annotate_nodes_from_tips("t", True, "2", "1")
        self.assertEqual(polytomy.find_node_with_taxon_label("D").parent_node.annotations.get_value("t"), "1")

    def test_polytomy_maxtrans_nogo(self):
        text = "(A[&t=2]:1,(B[&t=2]:1,(C[&t=2]:1,(D[&t=1]:1,E[&t=1]:1,G[&t=2]:1):1):1):1);"
        polytomy = dendropy.Tree.get_from_string(text, "newick")
        annotator = annotate_tree.TreeAnnotator(polytomy, True)
        annotator.annotate_nodes_from_tips("t", True, "2", "3")
        self.assertEqual(polytomy.find_node_with_taxon_label("D").parent_node.annotations.get_value("t"), "2")
