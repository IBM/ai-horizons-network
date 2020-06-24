# ----------------------------------------------------------------------------
# Copyright (c) 2019, AIHN-UCSD development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from __future__ import print_function
import re
import sys
input_fp = sys.argv[1]
out_fp = sys.argv[2]
with open(input_fp) as f:
        seq_lns = f.readlines()
        seq_dct  = dict()
        for seq_ln in seq_lns:
                if re.search(">", seq_ln):
                        name = seq_ln.strip(">").strip().split()[0]
                else:
                        seq_dct[name] = seq_ln.strip()
c = 0
len(seq_dct.keys())
len(seq_lns)
c = 0
with open(out_fp, 'w') as f:
        for key in seq_dct:
                print(">" + "fragment" + str(c) + "\n" + seq_dct[key], file=f)
                c += 1
