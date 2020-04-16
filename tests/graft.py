import unittest
import dendropy
import os

from clusterfunk.graft import RootStock

this_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(this_dir, "tests", 'data', 'graft')


class test_grafting_big_trees(unittest.TestCase):
    def test_all_are_added(self):
        base_tree = dendropy.Tree.get(path="%s/representative_sequences.aln.tree" % data_dir, schema="nexus")
        A = dendropy.Tree.get(path="%s/COG_GISAID_2020-04-11_lineage_A.tree" % data_dir, schema="newick")
        for node in A.postorder_node_iter():
            node.base_lineage = "A"
            node.annotations.add_bound_attribute("base_lineage")

        B = dendropy.Tree.get(path="%s/COG_GISAID_2020-04-11_lineage_B.tree" % data_dir, schema="newick")
        for node in B.postorder_node_iter():
            node.base_lineage = "B"
            node.annotations.add_bound_attribute("base_lineage")
        B1 = dendropy.Tree.get(path="%s/COG_GISAID_2020-04-11_lineage_B.1.tree" % data_dir, schema="nexus")
        for node in B1.postorder_node_iter():
            node.base_lineage = "B1"
            node.annotations.add_bound_attribute("base_lineage")

        expected_tips = len(A.leaf_nodes()) + len(B.leaf_nodes()) + len(B1.leaf_nodes())
        print(expected_tips)
        guide_tree = RootStock(base_tree)

        guide_tree.graft(A)
        guide_tree.graft(B)
        guide_tree.graft(B1)
        guide_tree.remove_left_over_tips()

        # guide_tree.tree.write(path="%s/combined_tree.tree" % data_dir, schema="nexus")
        # print(len(guide_tree.tree.leaf_nodes()))

        self.assertEqual(len(guide_tree.tree.leaf_nodes()), expected_tips)


if __name__ == '__main__':
    unittest.main()
