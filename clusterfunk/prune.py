import csv

from Bio import SeqIO


def parse_taxon_set(file, schema, index_column=None):
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
                taxon_set.append(row[index_column].strip())
    return taxon_set


def parse_taxon_sets_by_trait(file, tree, trait_name):
    taxon_sets = []
    values = []

    with open(file, newline='') as metadata_file:
        dialect = csv.Sniffer().sniff(metadata_file.read(1024))
        metadata_file.seek(0)
        reader = csv.DictReader(metadata_file, dialect=dialect)
        for row in reader:
            if row[trait_name] not in values:
                values.append(row[trait_name])
    for value in values:
        taxon_sets.append({"value": value, "tip_labels": [tip.taxon.label for tip in tree.leaf_node_iter() if
                                                          tip.annotations.get_value(trait_name) == value]})
    return taxon_sets


def prune_tree(tree, taxon_set, extract):
    if extract:
        tree.retain_taxa_with_labels(taxon_set)
    else:
        tree.prune_taxa_with_labels(taxon_set)
    return tree
