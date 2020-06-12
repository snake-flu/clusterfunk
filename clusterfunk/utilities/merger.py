from clusterfunk.utilities.utils import NodeTraitMap, SafeNodeAnnotator

nodeAnnotator = SafeNodeAnnotator()


class Merger:
    def __init__(self, trait_to_merge, trait_name, prefix="", max_merge=1):
        self.trait_to_merge = trait_to_merge
        self.trait_name = trait_name
        self.max_merge = max_merge
        self.merge_counts = None
        self.count = 1
        self.prefix = prefix

    def merge(self, tree):
        self.count = 1

        self.merge_counts = NodeTraitMap()
        for node in tree.postorder_node_iter():
            self.merge_counts.set([node, 0])

        values = list(set([tip.annotations.get_value(self.trait_to_merge) for tip in tree.leaf_node_iter() if
                           tip.annotations.get_value(self.trait_to_merge) is not None]))

        mrcas = []
        for value in values:
            taxa = [n.taxon for n in
                    tree.leaf_node_iter(lambda n: n.annotations.get_value(self.trait_to_merge) == value)]
            mrca = tree.mrca(taxa=taxa)
            mrcas.append(mrca)
        level_order_mrcas = [node for node in tree.levelorder_node_iter() if node in mrcas]

        while len(level_order_mrcas) > 0:
            current_node = level_order_mrcas.pop()
            parent = current_node.parent_node
            siblings = [node for node in level_order_mrcas if node.parent_node == parent]

            # combine
            if self.merge_counts.get(parent) < self.max_merge and len(siblings) > 0:
                level_order_mrcas = [node for node in level_order_mrcas if node not in siblings]
                self.increment_to_root(parent)
                self.name_merger(parent)
            # name them
            else:
                self.name_merger(current_node)
            self.count += 1

    def name_merger(self, node):
        nodeAnnotator.annotate(node, self.trait_name, self.prefix + str(self.count))
        for child in node.child_node_iter():
            if child.annotations.get_value(self.trait_to_merge) is not None:
                self.name_merger(child)

    def increment_to_root(self, node):
        new_count = self.merge_counts.get(node) + 1
        self.merge_counts.set([node, new_count])
        if node.parent_node is not None:
            self.increment_to_root(node.parent_node)