import dendropy


class TransitionAnnotator:
    def __init__(self, parent_state, child_state, trait, include_parent):
        self.parent_state = parent_state
        self.child_state = child_state
        self.trait = trait
        self.count = 0
        self.transition_points = []
        self.include_parent = include_parent
        pass

    def annotate_transitions(self, tree):
        self.count = 0
        self.transition_points = []
        node = tree.seed_node
        self.traverse(node)
        return self.count

    def traverse(self, node):
        state = node.annotations.get_value(self.trait)

        for child in node.child_node_iter():
            child_state = child.annotations.get_value(self.trait)

            if child_state == self.child_state:
                if state == self.parent_state:
                    self.transition_points.append(child)
                    self.count += 1

                setattr(child, "introduction", self.trait + str(self.count))
                child.annotations.add_bound_attribute("introduction")

            self.traverse(child)

    def split_at_transitions(self, tree):
        self.annotate_transitions(tree)
        trees = []
        for node in self.transition_points:
            new_root = node
            if self.include_parent:
                if node.parent_node is not None:
                    new_root = node.parent_node
            trees.append({"id": node.annotations.get_value('introduction'), "tree": dendropy.Tree(seed_node=new_root)})
        return trees
