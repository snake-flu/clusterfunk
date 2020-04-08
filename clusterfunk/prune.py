import csv

from Bio import SeqIO


def parse_taxon_set(file, schema, column=None):
    taxon_set = []
    if schema == "fasta":
        for record in SeqIO.parse(file, "fasta"):
            taxon_set.append(record.id)

    elif schema == "txt":
        with open(file, "r") as taxon_file:
            for line in taxon_file:
                taxon_set.append(line.strip())

    elif schema == "metadata":
        with open(file, newline='') as metadata_file:
            dialect = csv.Sniffer().sniff(metadata_file.read(1024))
            metadata_file.seek(0)
            reader = csv.DictReader(metadata_file, dialect=dialect)
            for row in reader:
                taxon_set.append(row[column].strip())

    return taxon_set


def prune_tree(tree, taxon_set, extract):
    if extract:
        tree.retain_taxa_with_labels(taxon_set)
    else:
        tree.prune_taxa_with_labels(taxon_set)
    return tree
