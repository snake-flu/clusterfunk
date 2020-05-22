import dendropy


class TreeHandler():
    def __init__(self, options):
        """
        :param options: Options passed in from argparse
        :param process: The subprocess that will be run
        """
        self.collapse = options.collapse
        self.data = None

    def prepare_tree(self, data):
        """
        Parse and collapse a input tree
        :return:
        """
        if self.collapse:
            for tree in data:
                self.collapse_nodes(tree)
            self.collapse_nodes(data)

    def collapse_nodes(self, tree):
        """
        Collapse branches with lengths below the provided threshold.
        This will create polytomies
        :param tree:
        :return:
        """
        for node in tree.postorder_node_iter(lambda n: not n.is_leaf()):
            if not node == tree.seed_node:
                if node.edge_length <= self.collapse:
                    node.edge.collapse(adjust_collapsed_head_children_edge_lengths=True)

    def parse_tree(self, **kwargs):
        """
        Parse a tree file
        :return:
        """
        data = dendropy.TreeList.get(preserve_underscores=True, **kwargs)
        self.prepare_tree(data)
        return data

    def write(self, data, **kwargs):
        """
        Write tree or tree list to file
        :return:
        """
        if kwargs["schema"] == "newick":
            data.write(**kwargs, suppress_rooting=True)
        else:
            data.write(**kwargs)
