import dendropy


class TransitionAnnotator:
    def __init__(self, trait, include_parent, transition_name):

        self.trait = trait
        self.From = None
        self.to = None
        self.count = 0
        self.transition_points = []
        self.include_parent = include_parent
        self.found_transition = False;

        self.transition_name = transition_name

    def annotate_transitions(self, tree, From=None, to=None):

        if From is None and to is None:
            raise ValueError("Must provide at least a from or to state")

        self.From = From
        self.to = to
        self.count = 0
        self.transition_points = []
        node = tree.seed_node
        self.traverse(node)
        return self.count

    def traverse(self, node):
        state = node.annotations.get_value(self.trait)

        for child in node.child_node_iter():
            child_state = child.annotations.get_value(self.trait)

            if self.From is not None:
                if state == self.From:
                    self.found_transition = False
                    if self.to is not None:
                        if child_state == self.to:
                            self.transition_points.append(child)
                            self.count += 1
                            self.found_transition = True
                    else:
                        if child_state != state:
                            self.transition_points.append(child)
                            self.count += 1
                            self.found_transition = True
                        else:
                            self.found_transition = False


            else:
                if child_state == self.to:
                    if state != self.to:
                        self.transition_points.append(child)
                        self.count += 1
                        self.found_transition = True
                else:
                    self.found_transition = False
            if self.found_transition:
                setattr(child, self.transition_name, self.transition_name + str(self.count))
                child.annotations.add_bound_attribute(self.transition_name)

            self.traverse(child)

    def split_at_transitions(self, tree, From=None, to=None):
        self.annotate_transitions(tree, From, to)
        trees = []
        for node in self.transition_points:
            new_root = node
            if self.include_parent:
                if node.parent_node is not None:
                    new_root = node.parent_node
            trees.append({"id": node.annotations.get_value('introduction'), "tree": dendropy.Tree(seed_node=new_root)})
        return trees
