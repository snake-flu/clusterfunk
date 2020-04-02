import dendropy
class TransitionAnnotator:
    def __init__(self, parent_state, child_state, trait):
        self.parent_state = parent_state
        self.child_state = child_state
        self.trait = trait
        self.count = 0
        self.transition_points = []
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

            if str(child_state) == str(self.child_state):
                if str(state) == str(self.parent_state):
                    self.transition_points.append(child)
                    self.count += 1

                setattr(child, "introduction", self.trait + str(self.count))
                child.annotations.add_bound_attribute("introduction")

            self.traverse(child)

    def split_at_transitions(self, tree):
        self.annotate_transitions(tree)
        trees = []
        for node in self.transition_points:
            trees.append(dendropy.Tree(seed_node=node))
        return trees
