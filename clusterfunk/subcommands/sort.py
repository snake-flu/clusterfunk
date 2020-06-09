from clusterfunk.subProcess import SubProcess
import bisect

class Sorter(SubProcess):
    def __init__(self, options):
        super().__init__(options)

    def run(self, tree):
        for node in tree.preorder_internal_node_iter():
            subtree_lengths = []
            for next_node_down in node.child_node_iter():
                subtree = next_node_down.extract_subtree()
                n = len(subtree.leaf_nodes())

                index = bisect.bisect_left(subtree_lengths, n)
                subtree_lengths.insert(index, n)

                node.insert_child(index, next_node_down)
