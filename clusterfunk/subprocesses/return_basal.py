from clusterfunk.subProcess import SubProcess


class BasalReturner(SubProcess):
    def __init__(self, options):
        super().__init__(options)
        self.handleOwnOutput = True;

    def run(self, tree):
        with open(self.options.output, "w") as text_file:
            for node in tree.levelorder_node_iter():
                if node.is_leaf():
                    text_file.write(node.taxon.label + "\n")
                    break
