"""
SubProcess is an abstract class that provides a standard framework for the main methdod.
Logic of running each funk (parsing/handling non-tree files) ect.
will be implemented in the run method. The Main class will call this method passing in the tree.
The Main also calls the cleanup function which is here to handle any updates to the tree data structure in dendropy
that need to be handled before writing the output to file.
"""


class SubProcess:

    def __init__(self, options):
        """
        Constructior. Options is the argument options passed in from argparse
        :param options:
        """
        self.options = options
        self.handleOwnOutput = False  # Does this process write its own output to file so that main doesn't need to.

    def run(self, tree):
        """
        The main method of the process acts on the tree.
        It will be called on each tree of a tree list
        :param tree:
        :return:
        """
        return

    def cleanup(self, tree):
        """
        A cleanup function that gets call after the run method.
        When the main is acting on a treelist It will be called once after all trees of a tree list are processed.
        :param tree:
        :return:
        """
        return
