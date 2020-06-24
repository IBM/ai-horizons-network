# ----------------------------------------------------------------------------
# Copyright (c) 2019, AIHN-UCSD development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import re
from io import StringIO
import pandas as pd
from biom.util import biom_open
import biom
import numpy as np
import os
import dendropy


def read_table_and_labels(biom_fp, meta_fp, tree_fp):
    if re.search(".tsv", biom_fp):
        tsv_fh = StringIO(biom_fp)
        func = lambda x: x
        table = biom.Table.from_tsv(tsv_fh, None, None, func)

    else:
        table = biom.load_table(biom_fp)

    if meta_fp:
        meta = pd.read_csv(meta_fp, sep='\t', low_memory=False, dtype={'#SampleID': str})
        meta = meta.set_index('#SampleID')
        meta.columns = ['label']
        y = meta.label
        samples = meta.index
    else:
        y = np.ones((len(table.ids('sample')), 1))
        samples = table.ids('sample')


    table = table.sort_order(axis='sample', order=samples)

    if sum(samples != table.ids('sample')) > 0:
        print("The samples IDs in meta data and biom table are not the same! Please double check.")
        print("The difference is:", set(samples) - set(table.ids('sample')))
        exit()

    tree = dendropy.Tree.get(path=tree_fp, preserve_underscores=True, schema="newick", rooting='default-rooted')
    return table, y, tree


def make_data_frame(orig_biom, augm_biom, orig_labels, augm_labels):
    orig_pd = pd.Series(np.asarray(orig_labels).ravel(), index=orig_biom.ids('sample'))
    orig_pd.index.names = ['#SampleID']
    augm_pd = pd.Series(np.asarray(augm_labels).ravel(), index=augm_biom.ids('sample'))
    augm_pd.index.names = ['#SampleID']
    return orig_pd, augm_pd


def write_biom_and_meta_data(orig_biom, orig_pd, augm_biom, augm_pd, out_dir, biom_fp, meta_fp):
    if not os.path.exists(out_dir):
        os.mkdir(os.path.abspath(out_dir))
    with biom_open(out_dir + '/' + os.path.basename(biom_fp), 'w') as f:
        orig_biom.to_hdf5(f, "original biom table")
    with biom_open(out_dir + '/augmented_data.biom', 'w') as f:
        augm_biom.to_hdf5(f, "augmented biom table")
    if meta_fp is not None:
        orig_pd.to_csv(out_dir + '/' + os.path.basename(meta_fp), sep='\t', header=['labels'])
        augm_pd.to_csv(out_dir + '/augmented_meta_data.csv', sep='\t', header=['labels'])
