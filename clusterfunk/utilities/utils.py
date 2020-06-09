# return parameter if not a string
import csv
import re

import chardet
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


class MetadataParser():
    """
    A utilities class for parsing deliminated files and detecting encodings
    """

    def parse_dsv(self, traits_file, index_column, trait_columns, parse_data="(.*)"):
        get_data_key = re.compile(parse_data)
        rawdata = open(traits_file, "rb").read()
        result = chardet.detect(rawdata)

        with open(traits_file, encoding=result['encoding']) as metadata:
            dialect = csv.Sniffer().sniff(metadata.readline())
            metadata.seek(0)
            self.reader = csv.DictReader(metadata, dialect=dialect)
            return self.get_traits_from_metadata(index_column, get_data_key, trait_columns)

    def get_traits_from_metadata(self, index_column, data_name_matcher, traits):
        """
        :param annotation_list: list of dictionaries that hold annotatations
        :param index_column: the key in the dictionary used to identify the taxon
        :param data_name_matcher: regex to parse the entries in the index column into groups to match taxon name g
        :param traits: name of trait keys to annotate
        :return: a dictionary keyed by parsed index column entries. Entries are dictionaries with trait and value pairs
        """
        annotation_dict = {}
        for row in self.reader:
            annotations = {}
            taxon_name_match = data_name_matcher.match(row[index_column])
            if not taxon_name_match:
                raise ValueError("taxon name %s in input file does not match regex pattern" % row[index_column])
            key_name = "".join(taxon_name_match.groups())
            for trait in traits:
                annotations[trait] = row[trait]
            annotation_dict[key_name] = annotations
        return annotation_dict
