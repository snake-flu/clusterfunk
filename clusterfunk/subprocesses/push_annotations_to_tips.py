import re

from clusterfunk.subProcess import SubProcess
from clusterfunk.utilities.utils import safeNodeAnnotator


class AnnotationPusher(SubProcess):

    def __init__(self, options):
        super().__init__(options)
        self.predicate = lambda node: True

    def run(self, tree):

        if self.options.stop_where_trait is not None:
            key, regex = self.options.stop_where_trait.split("=")
            matcher = re.compile(regex)

            self.predicate = lambda node: False if matcher.match(str(node.annotations.get_value(key))) else True

        for trait_name in self.options.traits:
            #         get values or traits
            values = list(set([node.annotations.get_value(trait_name) for node in
                               tree.leaf_node_iter(lambda tip: tip.annotations.get_value(trait_name) is not None)]))
            values.sort()
            for value in values:
                taxon_set = [tip.taxon for tip in
                             tree.leaf_node_iter(lambda node: node.annotations.get_value(trait_name) == value)]
                mrca = tree.mrca(taxa=taxon_set)
                self.push_trait_to_tips(mrca, trait_name, value)

    def push_trait_to_tips(self, node, trait_name, value):
        """

        :param node:
        :param trait_name:
        :param value:
        :return:
        """

        def action(n):
            """
            partially loading this action with the trait_name and value to add to each node
            this will be called below on each node if it passes the predicate.
            :param n:
            :return:
            """
            if n.is_leaf():
                safeNodeAnnotator.annotate(n, trait_name, value)

        traverse_and_annotate = self.TraversalAndAct(self.predicate, action)
        if self.predicate(node):
            traverse_and_annotate.traverse(node)

    class TraversalAndAct:
        """
        A helper class to traverse the tree and push the annotation to the tip so long as the predicate is met
        """

        def __init__(self, predicate, action):
            self.predicate = predicate
            self.action = action

        def traverse(self, node):
            for child in node.child_node_iter():
                if self.predicate(child):
                    self.action(child)
                    self.traverse(child)
