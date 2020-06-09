import csv
import re

import chardet
import dendropy
from Bio import SeqIO
from numpy import linspace
from scipy import stats

from clusterfunk.Main import Main
from clusterfunk.subProcess import SubProcess
from clusterfunk.utilities.utils import SafeNodeAnnotator

nodeAnnotator = SafeNodeAnnotator()


class TaxonParser():
    def __init__(self, data_taxon_regex, tree_taxon_regex):
        self.data_taxon_regex = data_taxon_regex
        self.tree_taxon_regex = tree_taxon_regex
        self.taxon_set = []

    def parse_data_taxon(self, taxon):
        match = self.data_taxon_regex.match(taxon)
        if not match:
            raise ValueError("taxon %s in input file does not match data regex")
        return "".join(match.groups())

    def parse_tree_taxon(self, taxon):
        match = self.tree_taxon_regex.match(taxon)
        if not match:
            raise ValueError("taxon %s in input file does not match data regex")
        return "".join(match.groups())

    def parse_fasta(self, file):
        for record in SeqIO.parse(file, "fasta"):
            taxon_label = self.parse_data_taxon(record.id)
            self.taxon_set.append(taxon_label)

    def parse_taxon(self, file):
        with open(file) as f:
            for line in f:
                taxon_label = self.parse_data_taxon(line.strip())
                self.taxon_set.append(taxon_label)

    def set_taxon_set(self, ts):
        self.taxon_set = ts

    def parse_metadata(self, file, index_column):
        rawdata = open(file, "rb").read()
        result = chardet.detect(rawdata)
        with open(file, encoding=result['encoding']) as metadata_file:
            dialect = csv.Sniffer().sniff(metadata_file.readline())
            metadata_file.seek(0)
            reader = csv.DictReader(metadata_file, dialect=dialect)
            for row in reader:
                taxon_label = self.parse_data_taxon(row[index_column].strip())
                self.taxon_set.append(taxon_label)

    def parse_by_trait_value(self, tree, trait_name, regex):
        matcher = re.compile(regex)
        for tip in tree.leaf_node_iter():
            if tip.annotations.get_value(trait_name):
                if matcher.match(tip.annotations.get_value(trait_name)):
                    self.taxon_set.append(self.parse_data_taxon(tip.taxon.label))


class TargetTreeProcess(SubProcess):
    def __init__(self, options):
        super().__init__(options)
        self.tree = None
        self.threshold = options.threshold

    def run(self, target_tree):
        target_tree.encode_bipartitions()
        namespace = target_tree.taxon_namespace

        tree_yielder = dendropy.Tree.yield_from_files(
                files=self.options.trees,
                schema='nexus',
                taxon_namespace=namespace,
        )

        node_map = {}
        for node in target_tree.postorder_node_iter(lambda n: not n.is_leaf()):
            if float(node.annotations.get_value("posterior")) > self.threshold:
                node_map[node.split_bitmask] = []

        for tree_idx, tree in enumerate(tree_yielder):
            tree.encode_bipartitions()
            distances = tree.calc_node_root_distances()
            origin = max(distances)
            for bitmap in node_map:
                split_edge = tree.split_bitmask_edge_map.get(bitmap)
                if split_edge is not None:
                    height = origin - split_edge.head_node.root_distance
                    node_map[bitmap].append(height)
        to_remove = []
        for bitmap in node_map:
            if len(node_map[bitmap]) <= 1:
                to_remove.append(bitmap)
        for bad_apple in to_remove:
            del node_map[bad_apple]

        for bitmap in node_map:
            kernel = stats.gaussian_kde(node_map[bitmap])
            kde = [[i, kernel.pdf(i)[0]] for i in linspace(min(node_map[bitmap]), max(node_map[bitmap]), num=50)]
            node = target_tree.split_bitmask_edge_map.get(bitmap).head_node

            nodeAnnotator.annotate(node, "height_density", [x[1] for x in kde])
            nodeAnnotator.annotate(node, "height_points", [x[0] for x in kde])


def run(options):
    main = Main(options, TargetTreeProcess(options))
    main.run()
