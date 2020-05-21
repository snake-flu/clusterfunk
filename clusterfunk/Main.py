import dendropy


class Main:
    def __init__(self, options, process):
        self.input = options.input
        self.input_format = options.in_format
        self.output = options.output
        self.output_format = options.output_format
        self.collapse = options.collapse
        self.process = process
        self.tree_list = options.tree_list
        self.tree = None
        self.trees = None
        self.options = options

    def run(self):
        if self.tree_list:
            for tree in self.trees:
                self.process.run(tree)
        else:
            self.prepare_tree()
            self.process.run(self.tree)
        if not self.process.handleOwnOutput:
            self.write()

    def prepare_trees(self):
        trees = self.parse_trees()
        if self.collapse:
            for tree in trees:
                self.collapse_nodes(tree)
        self.trees = trees

    def prepare_tree(self):
        self.tree = self.parse_tree()
        if self.collapse:
            self.collapse_nodes(self.tree)

    def collapse_nodes(self, tree):
        for node in tree.postorder_node_iter(lambda n: not n.is_leaf()):
            if not node == tree.seed_node:
                if node.edge_length <= self.collapse:
                    node.edge.collapse(adjust_collapsed_head_children_edge_lengths=True)

    def parse_tree(self):
        return dendropy.Tree.get(path=self.input, schema=self.input_format.lower(), preserve_underscores=True)

    def parse_trees(self):
        return dendropy.TreeList.get(path=self.input, schema=self.input_format.lower(), preserve_underscores=True)

    def write(self):
        if self.tree_list:
            if self.output_format == "newick":
                self.trees.write(path=self.output, schema=self.output_format, suppress_rooting=True)
            else:
                self.trees.write(path=self.output, schema=self.output_format)
        else:
            if self.output_format == "newick":
                self.tree.write(path=self.output, schema=self.output_format, suppress_rooting=True)
            else:
                self.tree.write(path=self.output, schema=self.output_format)
