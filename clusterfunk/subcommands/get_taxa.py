from clusterfunk.subProcess import SubProcess


class TaxaGetter(SubProcess):
    def __init__(self, options):
        super().__init__(options)
        self.handleOwnOutput = True;

    def run(self, tree):
        with open(self.options.output, "w") as text_file:
            for tip in tree.leaf_node_iter():
                text_file.write(tip.taxon.label + "\n")
