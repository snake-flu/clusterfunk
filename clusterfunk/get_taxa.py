import dendropy


class TaxaGetter():
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        pass

    def run(self):
        tree = dendropy.Tree.get(path=self.input_file, schema="nexus")
        with open(self.output_file, "w") as text_file:
            for tip in tree.leaf_node_iter():
                text_file.write(tip.taxon.label + "\n")
