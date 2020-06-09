import csv
import re

import chardet
from Bio import SeqIO


class TreePruner:
    def __init__(self, data_taxon_regex=re.compile("(.*)"), tree_taxon_regex=re.compile("(.*)"), extract=False):
        self.data_taxon_regex = data_taxon_regex
        self.tree_taxon_regex = tree_taxon_regex
        self.taxon_set = []
        self.extract = extract

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

    def prune(self, tree):
        taxa_labels = [tip.taxon.label for tip in tree.leaf_node_iter() if
                       self.parse_tree_taxon(tip.taxon.label) in self.taxon_set]
        if self.extract:
            tree.retain_taxa_with_labels(taxa_labels)
        else:
            tree.prune_taxa_with_labels(taxa_labels)

        return tree
