import argparse
import dendropy


def parse_args():
    parser = argparse.ArgumentParser(description='Assigns phylyoptes to a tree based on a branch length threshold')

    parser.add_argument("input", metavar='input', type=str,
                        help='The input file currently must be a nexus')
    parser.add_argument("output", metavar='input', type=str,
                        help='The output file currently must be a nexus')
    parser.add_argument('--threshold', dest='threshold', action='store',
                        default=0.00003,
                        help='branch threshold used to distinguish new phylotype (default: 0.00003')
    return parser.parse_args()


def read_tree(path):
    return dendropy.Tree.get(path=path, schema="nexus")


def phylotype(node, parent_phylotype, threshold, increment):
    current_phylotype = parent_phylotype

    if node.edge.length is not None:
        if node.taxon is None:
            if node.edge.length > threshold:
                current_phylotype = parent_phylotype + str(increment)
                increment += 1

    node.phylotype = "\"" + current_phylotype + "\""
    node.annotations.add_bound_attribute("phylotype", datatype_hint="xsd:string")
    i = 0
    for child in node.child_node_iter():
        i = phylotype(child, current_phylotype, threshold, i)
    return increment


if __name__ == '__main__':
    args = parse_args()
    tree = dendropy.Tree.get(path=args.input, schema="nexus")
    phylotype(tree.seed_node, "0", args.threshold, 0)
    tree.write(path=args.output, schema="nexus")

    print("done")
