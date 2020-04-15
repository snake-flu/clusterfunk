import dendropy
import csv


def phylotype_tree(tree, threshold=5e-6, suffix="p"):
    def phylotype_nodes(node, phylotype="p"):
        node.phylotype = "\"" + phylotype + "\""
        node.annotations.add_bound_attribute("phylotype")
        i = 1
        for child in node.child_node_iter():
            suffix = ""
            if child.taxon is None:
                if child.edge.length > threshold:
                    suffix = "." + str(i)
                    i += 1
            phylotype_nodes(child, phylotype + suffix)

    phylotype_nodes(tree.seed_node, suffix)
