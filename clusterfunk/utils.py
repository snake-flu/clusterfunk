# return parameter if not a string
import dendropy


def check_str_for_bool(s):
    if isinstance(s, str):
        if s.lower() == 'true':
            return True
        elif s.lower() == 'false':
            return False

    return s


def parse_tree(file, format):
    return dendropy.Tree.get(path=file, schema=format.lower(), preserve_underscores=True)


def write_tree(tree, options):
    if options.out_format == "newick":
        tree.write(path=options.output, schema=options.out_format, suppress_rooting=True)
    else:
        tree.write(path=options.output, schema=options.out_format)


def collapse_nodes(tree, threshold):
    for node in tree.postorder_node_iter(lambda n: not n.is_leaf()):
        if not node == tree.seed_node:
            if node.edge_length <= threshold:
                node.edge.collapse(adjust_collapsed_head_children_edge_lengths=True)


def prepare_tree(options, input_file_name=None):
    input_path = input_file_name if input_file_name is not None else options.input
    tree = parse_tree(input_path, options.in_format)
    if options.collapse:
        collapse_nodes(tree, options.collapse)
    return tree


class SafeNodeAnnotator:
    def __init__(self, safe=True):
        self.safe = safe

    def annotate(self, node, name, value):
        if self.safe:
            if node.annotations.get_value(name) is not None:
                node.annotations.drop(name=name)
        setattr(node, name, value)
        node.annotations.add_bound_attribute(name)


safeNodeAnnotator = SafeNodeAnnotator(True);


class NodeTraitMap:
    def __init__(self):
        self.traitDict = {}

    def set(self, l):
        node, trait = l
        self.traitDict[hash(node)] = trait

    def get(self, node):
        return self.traitDict[hash(node)]
