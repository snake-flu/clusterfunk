import dendropy


class Phylotyper:
    def __init__(self, threshold):
        self.threshold = threshold
        pass

    def phylotype_nodes(self, node, phylotype="1"):
        node.phylotype = "\"" + phylotype + "\""
        node.annotations.add_bound_attribute("phylotype")

        i = 1
        for child in node.child_node_iter():
            suffix = ""
            if child.taxon is None:
                if child.edge.length > self.threshold:
                    suffix = "." + str(i)
                    i += 1
            self.phylotype_nodes(child, phylotype + suffix)

    def run(self, input_file, output_file):
        tree = dendropy.Tree.get(path=input_file, schema="nexus")
        self.phylotype_nodes(tree.seed_node)
        tree.write(path=output_file, schema="nexus")
