import sys

import dendropy

"""
Main method for clusterfunk. Each funk starts here. This handles the tree parsing/writing as well as
managing tree input vs tree list input
"""


class Main:
    def __init__(self, options, process):
        """
        :param options: Options passed in from argparse
        :param process: The subprocess that will be run
        """
        self.input = options.input
        self.input_format = options.in_format
        self.output = options.output
        self.output_format = options.out_format
        self.collapse = options.collapse
        self.process = process
        self.tree_list = options.tree_list
        self.tree = None
        self.trees = None
        self.options = options

        self.run()

    def run(self):
        """
        Read in the tree(s)
        Run the subprocess on the tree data
        post process the data as needed
        write the tree to file unless the process handles it's own writing
        :return:
        """

        if self.tree_list:
            self.prepare_trees()
            number_of_trees = len(self.trees)
            sys.stdout.write("Found %d trees \n" % number_of_trees)
            i = 0
            for tree in self.trees:
                sys.stdout.write('\r')
                sys.stdout.write(" %d%%" % (round((i / number_of_trees) * 100)))
                self.process.run(tree)
                sys.stdout.flush()
                i += 1
            sys.stdout.write("\n")
            self.process.cleanup(self.trees)

        else:
            self.prepare_tree()
            self.process.run(self.tree)
            self.process.cleanup(self.tree)
        if not self.process.handleOwnOutput:
            self.write()

    def prepare_trees(self):
        """
        Parse and collapse trees in a tree list
        :return:
        """
        self.parse_trees()
        if self.collapse:
            for tree in self.trees:
                self.collapse_nodes(tree)

    def prepare_tree(self):
        """
        Parse and collapse a input tree
        :return:
        """
        self.parse_tree()
        if self.collapse:
            self.collapse_nodes(self.tree)

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

    def parse_tree(self):
        """
        Parse a tree file
        :return:
        """
        self.tree = dendropy.Tree.get(path=self.input, schema=self.input_format.lower(), preserve_underscores=True)

    def parse_trees(self):
        """
        Parse a file with multiple trees
        :return:
        """
        self.trees = dendropy.TreeList.get(path=self.input, schema=self.input_format.lower(), preserve_underscores=True)

    def write(self):
        """
        Write tree or tree list to file
        :return:
        """
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
