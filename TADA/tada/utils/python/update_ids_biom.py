# ----------------------------------------------------------------------------
# Copyright (c) 2019, AIHN-UCSD development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import biom
import sys
import re
from biom.util import biom_open

if "-h" in sys.argv[1:] or "--help" in sys.argv[1:] or len(sys.argv[1:])<2:
	print("USAGE:",sys.argv[0], "biom_table_file_path", "fragments_file_path")
	sys.exit(0)

biom_fp = sys.argv[1]
frag_fp = sys.argv[2]

table = biom.load_table(biom_fp)

def read_fasta(fasta_fp):
	with open(fasta_fp, 'r') as f:
		seq_lns = f.readlines()
		seq_dct = dict()
		for seq_ln in seq_lns:
			if re.search(">", seq_ln) is not None:
				seq_ln = seq_ln.strip()
				sp_name = re.sub(">", "", seq_ln)
			else:
				seq_dct[sp_name] = seq_ln.strip()
	return seq_dct

def inv_seq_dictionary(seq_dct):
	mapping = dict()
	for sp in seq_dct:
		mapping[seq_dct[sp]] = sp
	return mapping


seq_dct = read_fasta(frag_fp)
mapping = inv_seq_dictionary(seq_dct)

new_table = table.update_ids(mapping, axis='observation', inplace=False)
with biom_open('relabeled.' + biom_fp, 'w') as f:
	new_table.to_hdf5(f, "new table")
