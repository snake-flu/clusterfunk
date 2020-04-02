class TransitionAnnotator:
    def __init__(self, parent_state, child_state, trait):
        self.parent_state = parent_state
        self.child_state = child_state
        self.trait = trait
        self.count = 0
        pass

    def annotate_transitions(self, tree):
        self.count = 0
        node = tree.seed_node
        self.traverse(node)
        return self.count

    def traverse(self, node):
        state = node.annotations.get_value(self.trait)

        for child in node.child_node_iter():
            child_state = child.annotations.get_value(self.trait)

            if str(child_state) == str(self.child_state):
                if str(state) == str(self.parent_state):
                    self.count += 1

                setattr(child, "introduction", self.trait + str(self.count))
                child.annotations.add_bound_attribute("introduction")

            self.traverse(child)
