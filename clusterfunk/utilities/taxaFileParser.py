import csv
import re

import chardet
from Bio import SeqIO


class TaxaFileParser():
    """
    A helper class that parses fasta files, txt files,
    and dsv files and returns a list of taxon labels
    """

    def __init__(self, data_taxon_pattern="(.*)"):
        """

        :param data_taxon_pattern: A string pattern that will be compiled into a regex and used to parse the input
        """
        self.data_taxon_regex = re.compile(data_taxon_pattern)

    def parse_fasta(self, file):
        for record in SeqIO.parse(file, "fasta"):
            taxon_label = self.parse_data_taxon(record.id)
            self.taxon_set.append(taxon_label)

    def parse_taxon(self, file):
        taxon_set = []
        with open(file) as f:
            for line in f:
                taxon_label = self.parse_data_taxon(line.strip())
                taxon_set.append(taxon_label)
        return taxon_set

    def parse_metadata(self, file, index_column):
        taxon_set = []
        rawdata = open(file, "rb").read()
        result = chardet.detect(rawdata)
        with open(file, encoding=result['encoding']) as metadata_file:
            dialect = csv.Sniffer().sniff(metadata_file.readline())
            metadata_file.seek(0)
            reader = csv.DictReader(metadata_file, dialect=dialect)
            for row in reader:
                taxon_label = self.parse_data_taxon(row[index_column].strip())
                taxon_set.append(taxon_label)
        return taxon_set

    def parse_data_taxon(self, taxon):

        match = self.data_taxon_regex.match(taxon)
        if not match:
            raise ValueError("taxon %s in input file does not match data regex")
        return "".join(match.groups())

    def smart_parse(self, options):
        if options.fasta is not None:
            return self.parse_fasta(options.fasta)
        elif options.metadata is not None:
            return self.parse_metadata(options.metadata, options.index_column)
        elif options.taxon is not None:
            return self.parse_taxon(options.taxon)
