import dendropy
import csv

from clusterfunk.utils import SafeNodeAnnotator

nodeAnnotator = SafeNodeAnnotator(safe=True)
def phylotype_tree(tree, threshold=5e-6, suffix="p"):
    def phylotype_nodes(node, phylotype="p"):
        nodeAnnotator.annotate(node, "phylotype", "\"" + phylotype + "\"")

        i = 1
        for child in node.child_node_iter():
            suffix = ""
            if child.taxon is None:
                if child.edge.length > threshold:
                    suffix = "." + str(i)
                    i += 1
            phylotype_nodes(child, phylotype + suffix)

    phylotype_nodes(tree.seed_node, suffix)
