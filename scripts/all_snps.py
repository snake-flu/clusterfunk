from Bio import SeqIO
import argparse
from collections import defaultdict
import parasail
import json
from multiprocessing.pool import Pool

def parse_args():
    parser = argparse.ArgumentParser(description='get_all_snps_and_their_lineage')

    parser.add_argument("--fasta", action="store", type=str, dest="fasta")
    parser.add_argument("--tree", action="store", type=str, dest="tree")
    parser.add_argument("--matrix", action="store", type=str, dest="matrix")
    parser.add_argument("--ref_file", action="store", type=str, dest="ref_file")

    return parser.parse_args()


def load_ref_seq(ref_file):
    ref_seq = ""

    for record in SeqIO.parse("finding_defining_mutations/WH04_reference.fasta","fasta"):
        ref_seq = str(record.seq).replace("-","")
        print(f"Loaded reference {record.id}")

    return ref_seq

def load_matrix(matrix_file):
    print(f"Loading substitution matrix from {matrix_file}")
    return parasail.Matrix("finding_defining_mutations/substitution_matrix.txt")

def load_seq_dict(fasta):
    seq_dict = {}
    for record in SeqIO.parse(str(fasta),"fasta"):
        seq_dict[record.id] = str(record.seq)
    return seq_dict

def extract_lineage_hierarchy(lineage):
    tokens = lineage.split(".")
    lineages = []
    for i in range(len(tokens)):
        l = ".".join(tokens[:i+1])
        lineages.append(l)
    return lineages

def parse_lineage_annotations_from_line(l):
    l = l.rstrip(']\n').lstrip('\t')
    tokens= l.split("[")
    name = tokens[0]
    
    annotations = tokens[1].lstrip("&").split(',')

    clade = ""
    lineage = ""
    
    for i in annotations:
        if i.startswith("Clade"):
            clade = i.split("=")[1].lstrip('"').rstrip('"')
        else:
            lineage = i.split("=")[1].lstrip('"').rstrip('"')
    if lineage == "":
        lineage = clade

    return name,lineage


def extract_taxlabels_from_file(treefile):
    
    lineage_dict = defaultdict(list)
    name_to_lineages = {}
    
    with open(str(treefile), "r") as f:
        read_line = False
        for l in f:
            l = l.rstrip("\n")
            
            if l == ";":
                read_line = False
                
                
            if read_line:
                name,lineage = parse_lineage_annotations_from_line(l)
                
                lineages = extract_lineage_hierarchy(lineage)
                
                name_to_lineages[name]=lineages
                
                for sub_lineage in lineages:
                    lineage_dict[sub_lineage].append(name)
                    
            if l.startswith("\ttaxlabels"):
                read_line = True

    return lineage_dict,name_to_lineages

def run_alignments(aln_args):
    
    seq_dict, ref_seq, matrix, aln_dict = aln_args

    for i in seq_dict:
        print(f"Aligning {i}")
        query = seq_dict[i]

        traceback = run_alignment(query, ref_seq, matrix)

        aln_dict[i] = traceback

def run_alignment(query, reference, matrix):
    
    result_trace = None
    traceback = None
    result_trace = parasail.sw_trace_scan_sat(query, reference, 3, 2, matrix)
    traceback = result_trace.get_traceback('|', '.', ' ')
    pythonic_traceback = [str(traceback.ref),str(traceback.query)]
    return pythonic_traceback

def parse_alignment(member, traceback, all_snps):
    ref,query = traceback
    snps = []
    index = 0
    for i in range(len(ref)):
        if ref[i]!='-':
            index+=1
        col = [ref[i], query[i]]
        if len(set(col))>1 and "N" not in col:
            print(f"- Position {index+1}:\tReference:\t{col[0]}\tConsensus:\t{col[1]}\n")
            snp = f"{index+1}{col[0]}{col[1]}"
            snps.append(snp)
            all_snps.append(snp)
            
    return(snps)

def iterate_over_lineages(lineage_dict, seq_dict, aln_dict):
    snp_db = defaultdict(list)

    all_snps_db = {}   
    lineage_db = {}

    alignment_store = {}

    for lineage in sorted(lineage_dict):
        lineage_snps = []
        all_snps = []

        print("Lineage:", lineage)

        for member in lineage_dict[lineage]:
            if member in seq_dict:
            
                traceback = aln_dict[member]

                sequence_snps = parse_alignment(member, traceback, all_snps)

                alignment_store[member] = sequence_snps

                if lineage_snps:
                    lineage_snps = list(set(sequence_snps).intersection(lineage_snps))
                else:
                    lineage_snps = sequence_snps

        print(f"SNPs common to all sequences in {lineage}: {lineage_snps}")

        lineage_db[lineage]= lineage_snps
        
        all_snps = list(set(all_snps))
        
        print(f"All SNPs found in {lineage}: {all_snps}")

        for snp in all_snps:            
            if snp in clade_snps:
                snp_db[snp].append(lineage)
            else:
                snp_db[snp].append("NA")

    for snp in snp_db:
        lineage_list = [i for i in list(set(snp_db[snp])) if not i=="NA"]
        all_snps_db[snp] = lineage_list

    return all_snps_db,lineage_db

def batch_align(aln_args):
    if __name__ == '__main__':
        with Pool(10) as pool:
            pool.map(run_alignments,(aln_args,))

def find_snps_and_lineages(tree, fasta, matrix, ref_file):

    lineage_dict,name_to_lineages = extract_taxlabels_from_file(tree)

    print("Number of lineages:",len(lineage_dict))
    for i in sorted(lineage_dict):
        print(f"{i} has {len(lineage_dict[i])} members")

    seq_dict = load_seq_dict(fasta)

    matrix = load_matrix(matrix)

    ref_seq = load_ref_seq(ref_file)

    aln_dict = {}

    aln_args = (seq_dict, ref_seq, matrix)

    batch_align(aln_args)

    all_snps_db,lineage_db = iterate_over_lineages(lineage_dict, seq_dict, aln_dict)

    with open("all_snps_db_hierarchical.json","w") as fw:
        json.dump(all_snps_db, fw)
    with open("lineage_db_hierarchical.json","w") as fw:
        json.dump(lineage_db, fw)


if __name__ == '__main__':

    args = parse_args()

    find_snps_and_lineages(args.tree, args.fasta, args.matrix, args.ref_file)
    



            
