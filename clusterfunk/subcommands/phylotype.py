from clusterfunk.subProcess import SubProcess
from clusterfunk.utils import safeNodeAnnotator

"""
Phylotype a tree. Essentially codify the internal nodes on a tree. No tip can have a unique phylotype.
"""
class Phylotype(SubProcess):
    def __init__(self, options):
        """
        Options contain :
        threshold - the branch length that determines when to define a new phylotype
        prefix - the prefix of the phylotyes. And the root phylotype.
        :param options:
        """
        super().__init__(options)

        self.threshold = options.threshold
        self.prefix = options.prefix

    def run(self, tree):
        self.phylotype_nodes(tree.seed_node, self.prefix)

    def phylotype_nodes(self, node, phylotype):
        safeNodeAnnotator.annotate(node, "phylotype", "\"" + phylotype + "\"")
        i = 1
        for child in node.child_node_iter():
            suffix = ""
            if child.taxon is None:
                if child.edge.length > self.threshold:
                    suffix = "." + str(i)
                    i += 1
            self.phylotype_nodes(child, phylotype + suffix)
