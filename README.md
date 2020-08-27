# clusterfunk
Miscellaneous clustering manipulation tools

## Install
Either pip install using command
```
pip install .
```
or use
```
python setup.py install
```
and test with
```
python setup.py test
```

Commands
```
 clusterfunk -h
usage: clusterfunk <subcommand> <options>

Miscellaneous clustering tools

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

Available subcommands:
  
    phylotype 
                        Assigns phylotypes to a tree based on a branch length
                        threshold
    annotate_tips 
                        Annotates the tips of tree. Can annotate tips from a
                        csv/tsv and/or taxon labels
    ancestral_reconstruction
                        Reconstructs ancestral states on internal nodes using
                        Fitch parsimony algorithm
    push_annotations_to_tips
                        This funk pushes annotations to tips. It identifies
                        the mrca of nodes with each value of the trait
                        provided and pushes the annotation up to any
                        descendent tip
    extract_tip_annotations 
                        extracts annotations from tips in a tree and ouputs a
                        csv
    get_taxa 
                        extracts taxa labels from tips in a tree
    return_basal 
                        returns a representative basal taxon
    label_transitions 
                        counts and labels transitions of traits on a tree
    prune 
                        Prunes a tree either removing the specified taxa or
                        keeping only those specified. Taxa can be specified
                        from a fasta file, text file, metadata file, or by an
                        annotation.
    graft 
                        This function grafts trees (scions) onto a guide tree
                        (input). The scion tree is grafted onto the guide tree
                        at the MRCA of the tips shared between the two. Any
                        shared tips originally in the guide tree are then
                        removed. All incoming trees must be in the same format
                        [nexus,newick,ect.]
```

## Examples

Annotate the tips of a tree using fields from a CSV file. It will use 'sequence_name' column in the CSV to match the tips of the tree and then add the data from the columns specified by `--trait-columns` to each tip using the NEXUS metacomment format.
```
clusterfunk annotate_tips --in-metadata <master.metadata.csv> --index-column sequence_name --trait-columns <trait1 trait1 ...> -  --input <input.tree> --output <output.tree>
```

Same as above but adds the metadata fields to the taxon labels of the tree.
```
clusterfunk relabel_tips --in-metadata <master.metadata.csv> --index-column sequence_name --trait-columns <trait1 trait1 ...>  --input <input.tree> --output <output.tree>
```
