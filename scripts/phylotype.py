import argparse
import dendropy


def parse_args():
    parser = argparse.ArgumentParser(description='Assigns phylyoptes to a tree based on a branch length threshold')

    parser.add_argument("input", metavar='input', type=str,
                        help='The input file currently must be a nexus')
    parser.add_argument("output", metavar='output', type=str,
                        help='The output file currently must be a nexus')
    parser.add_argument('--threshold', dest='threshold', action='store',
                        default=5E-6, type=float,
                        help='branch threshold used to distinguish new phylotype (default: 5E-6')
    return parser.parse_args()


def read_tree(path):
    return dendropy.Tree.get(path=path, schema="nexus")


def phylotype_nodes(node, phylotype, threshold):
    node.phylotype = "\"" + phylotype + "\""
    node.annotations.add_bound_attribute("phylotype")

    i = 0
    for child in node.child_node_iter():
        suffix = ""
        if child.taxon is None:
            if child.edge.length > threshold:
                suffix = "." + str(i)
                i += 1
        phylotype_nodes(child, phylotype + suffix, threshold)


if __name__ == '__main__':
    args = parse_args()
    tree = dendropy.Tree.get(path=args.input, schema="nexus")
    phylotype_nodes(tree.seed_node, "0", args.threshold)
    tree.write(path=args.output, schema="nexus")

    print("done")
