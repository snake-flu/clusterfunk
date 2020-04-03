import dendropy
import csv

class Phylotyper:
    def __init__(self, threshold, csv=False):
        self.threshold = threshold
        self.csv = csv
        pass

    def phylotype_nodes(self, node, phylotype="p"):
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
        if self.csv:
            tips = [{"taxon": x.taxon, "phylotype": x.phylotype.replace('"', '')} for x in tree.leaf_node_iter()]
            with open(output_file, "w") as csvfile:
                fileheader = ["taxon", "phylotype"]
                writer = csv.DictWriter(csvfile, fieldnames=fileheader)
                writer.writeheader()
                for tip in tips:
                    writer.writerow(tip)
        else:
            tree.write(path=output_file, schema="nexus")
