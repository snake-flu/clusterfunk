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


def write_tree(tree, file, format):
    tree.write(path=file, schema=format)


def collapse_nodes(tree, predicate):
    for node in tree.preorder_node_iter(predicate):
        if not node.is_leaf():
            node.edge.collapse(adjust_collapsed_head_children_edge_lengths=True)


def prepare_tree(options, input_file_name=None):
    input_path = input_file_name if input_file_name is not None else options.input
    tree = parse_tree(input_path, options.format)
    if options.collapse:
        collapse_nodes(tree, lambda node: node.edge.length <= options.collapse)
    return tree
