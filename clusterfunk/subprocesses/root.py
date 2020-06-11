from clusterfunk.subProcess import SubProcess

class Rooter(SubProcess):
    def __init__(self, options):
        super().__init__(options)

    def run(self, tree):
        outgroup = self.options.outgroup

        outgroup_node = tree.find_node_with_taxon_label(outgroup)
        tree.to_outgroup_position(outgroup_node)
