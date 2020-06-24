## Abstract

TADA is a new data augmentation technique for classifying phenotypes based on the microbiome. 
Our algorithm, TADA, uses available data and a statistical generative model to create new samples augmenting existing ones, addressing issues of low-sample-size. 
In generating new samples,
TADA takes into account phylogenetic relationships between microbial species. Adding these synthetic samples to the training set improves the accuracy of downstream classification, especially when the training data have an unbalanced representation of classes.

## Installation 
TADA is a python3 package and depends on several other python packages, including i) [numpy](https://www.numpy.org/) ii) [Dendropy](https://dendropy.org/) iii) [scikit-learn](https://scikit-learn.org/stable/install.html) iv) [biom-format](http://biom-format.org/documentation/biom_format.html) v) [pandas](https://pandas.pydata.org/).

To install these packages using **conda**, first create a conda environment

```
conda create --name TADA python=3.6
conda activate TADA
```

Then clone this [github](git@github.com:tada-alg/TADA.git) repository somewhere on your machine. You can inst`all TADA using the following set of commands

```
cd TADA
python setup install
```
To test your installation, please use the following command

```
run_TADA.py -h
```

And if your installation was successful, you should see the following help messages

```
Usage: run_TADA.py [options]

Options:
  -h, --help            show this help message and exit
  -t TREE_FP, --tree=TREE_FP
                        Phylogeny file in newick format.
  -b BIOM_FP, --biom=BIOM_FP
                        The count table. This can be a biom (file with suffix
                        .biom) or TSV (Tab Separated Values) file (file with
                        suffix .tsv). In TSV format rows define features, and
                        columns define samples.The first column defines the
                        feature IDs. The first row defines a header where from
                        the second column sample IDs are listed.
  -o OUT_DIR, --output=OUT_DIR
                        The output directory.
  --seed=SEED_NUM       Seed number. Default is 0.
  -g GENERATE_STRATEGY, --generate_strategy=GENERATE_STRATEGY
                        Specifies the generating strategy for either balancing
                        or data augmentation without balancing. If TADA is
                        used for augmentation, this shouldn't be passed.
                        Otherwise, pass a meta data file (in TSV format, a tab
                        delimited with no header). The first column should be
                        samples, and second column should be class labels.
  -x XGEN, --xgen=XGEN  Amount of generation for balancing. If TADA is used
                        for only balancing (no extra augmentation afterwards),
                        0 should be passed. In balancing, TADA eventually will
                        generate new samples until all classes have [xgen+1] *
                        [maximum class size] samples. Default is 0
  -k N_BETA, --n_beta=N_BETA
                        The number of draws from the beta distribution. For
                        augmentation, TADA will generate [n_binom]*[n_beta]
                        samples per each sample. Default is 1.
  -u N_BINOM, --n_binom=N_BINOM
                        The number of draws from binomial distribution. For
                        augmentation, TADA will generate [n_binom]*[n_beta]
                        samples per each sample. Default is 5
  -v VAR_METHOD, --var_method=VAR_METHOD
                        Defines how to introduce the variation. Options are
                        br_penalized and class. The br_penalized can be used
                        with a monotonically increasing function of branch
                        length to define the variation. The class options can
                        be used to use estimate the variation from training
                        data. We suggest using br_penalized.
  -z STAT_METHOD, --stat_method=STAT_METHOD
                        The generative model. Options are binom or beta_binom.
  -r PRIOR_WEIGHT, --prior_weight=PRIOR_WEIGHT
                        The class conditional probability weight. The default
                        is 0.
  -c COEF, --coef=COEF  The penalty factor in the calculation of nu. This
                        affects the amount of variation.
  --exponent=EXPONENT   The exponent in the calculation of nu. This affects
                        the amount of variation.
  --br_pseudo=PSEUDO    A pesudo small branch length will be added to all
                        branches to avoid zero branch length estimate problem.
  --pseudo_cnt=PSEUDO_CNT
                        Pseudo count to avoid zero count problem
  --normalized=NORMALIZED
                        If set to 1, the OTU counts will be normalized to add
                        up to one.
```

## Running
Input to TADA are

1. A rooted tree in newick format. For microbiome data, you could use this [pipline](https://github.com/qiime2/q2-fragment-insertion) to get the tree.
2. A count table where each sample is represented with a set of feature (OTU for microbiome). The rows are typically features and columns are samples. This input can be biom format or TSV (Tab Separated Values). The code recognizes if the input count table is in the biom format if the file ends in .biom or TSV format if it ends in .tsv. If the table is in TSV format, columns correspond to samples. The first column is an exception which stores the feature IDs. The first row also stores the sample IDs, and the first string in this file (string at first column, first row) should be a dummy string.
3. The output directory to store augmented data (and metadata if applicable) in the biom format.
If TADA is used for balancing, a metadata file (TSV) format is also needed. In this file, the first column indicates sample IDs, and the second column shows the class labels corresponding to each sample. The first row assumes to be a header with your choice of wording.

The outputs of the code are (written on the output directory)

1. Augmented data in the biom format
2. A copy of original data in the biom format
3. Only for balancing: Metadata for augmented data
4. Only for balancing: A copy of the metadata for original data
5. The log file to keep track of progress and errors


### Using TADA for augmentation
The training data size has a tremendous effect on the machine learning method performance. Generating new samples from the training data can be helpful. To use TADA for data augmentation, you can use the following command

```
run_TADA.py -t [phylogeny_fp] -b [table_fp] -o [output_dir]
```

Please download the example data available [here](data/reference/test.tar.gz). Next unarchive the file and go to the resulting directory

```
tar xzvf test.tar.gz
cd test
```

Next, you can augment data (using hierarchy of binomials) to it using the following command

```
mkdir binom
run_TADA.py -t phylogeny.tre -b feature-table.biom -o ./binom
```


This will create a log file `binom/logfile.txt`, and the augmented data file in biom format `binom/augmented_data.biom`. If you wish using beta binomial, you can use the following command

```
mkdir beta_binom
run_TADA.py -t phylogeny.tre -b feature-table.biom -o ./beta_binom -z beta_binom
```

This will create a log file `beta_binom/logfile.txt`, and the augmented data file in biom format `beta_binom/augmented_data.biom`.


### Using TADA for balancing datasets
In microbiome samples, the distribution of class labels (or cluster labels for unsupervised learning) is often unbalanced. This can cause overfitting and poor generalization of the machine learning method on new samples. You can use TADA to generate new samples for the underrepresented classes to make classes the same size. For this application, you can use TADA with the following command

```
run_TADA.py -t [phylogeny_fp] -b [table_fp] -o [output_dir] -g [metadata_fp] 
```
Please download the example data available [here](data/reference/test.tar.gz). Next unarchive the file and go to the resulting directory

```
tar xzvf test.tar.gz
cd test
```

Next, you can generate synthetic data (using hierarchy of binomials) to create balanced datasets using the following commands

```
mkdir binom
run_TADA.py -t phylogeny.tre -b feature-table.biom -o ./binom_balance -g metadata.csv
```

This will generate the folder `binom`, and it will create the following files under this directory:

* `augmented_meta_data.csv`: class/cluster labels of the new samples, first column: sample IDs, second column: labels)
* `augmented_data.biom`: generated features
* `logfile.txt`: log file for generating features
* `feature-table.biom`: original features
* `metadata.csv`: original meta data file

If you wish to use the Beta-Binomial generative model, you can use the following commands respectively

```
mkdir beta_binom
run_TADA.py -t phylogeny.tre -b feature-table.biom -o ./beta_binom_balance -g metadata.csv -z beta_binom
```

The outputs are similar to what described above. The above command will generate enough number of samples for the least size cluster/class (in provided example, from group `1`) so that both groups have the same size. In this implementation of TADA, user can choose to continue generating samples so that the final size of each group be a multiple of initial size of the most frequent group. For example, if the most frequent gorup has `20` samples, and the least size group has `10` samples, and user wishes to have augmentation level of `5x`, then the final size of both classes will be `120 = (5)*20 + 20`. The augmentation level of `0x` means the user wants both classes the same size and no further augmentation (default). For example, the following command will peform a `5x` augmentation.

```
mkdir beta_binom
run_TADA.py -t phylogeny.tre -b feature-table.biom -o ./beta_binom_balance_5x -g metadata.csv -z beta_binom -x 5
```

The outpus are similar to what described above. Please note that in the augmented meta data file, there are `110` samples with class `1` and `100` samples with class 0. Overal, you will have `120` samples for both classes. 

## Seed number

Please note that you can specify the seed number for the random number generator  by passing `--seed [a number]`. By default, the seed number is `0`. 

# Importing and preprocessing data

This tutorial is based on the official [Qiime2](https://docs.qiime2.org/2019.4/tutorials/overview/) tutorials. We also created in-house scripts (all based on Qiime2) to import files from FASTA and FASTQ format to Qiime2 artifacts, denoise them using Deblur, and create the phylogeny. You can read more about them [here](https://github.com/tada-alg/TADA/tree/master/src/utils/shell). 


 


## References
1. Erfan Sayyari, Ban Kawas, Siavash Mirarab, TADA: phylogenetic augmentation of microbiome samples enhances phenotype classification, Bioinformatics, Volume 35, Issue 14, July 2019, Pages i31–i40, [DOI](https://doi.org/10.1093/bioinformatics/btz394)
2. Bolyen E, Rideout JR, Dillon MR, Bokulich NA, Abnet C, Al-Ghalith GA, Alexander H, Alm EJ, Arumugam M, Asnicar F, Bai Y, Bisanz JE, Bittinger K, Brejnrod A, Brislawn CJ, Brown CT, Callahan BJ, Caraballo-Rodríguez AM, Chase J, Cope E, Da Silva R, Dorrestein PC, Douglas GM, Durall DM, Duvallet C, Edwardson CF, Ernst M, Estaki M, Fouquier J, Gauglitz JM, Gibson DL, Gonzalez A, Gorlick K, Guo J, Hillmann B, Holmes S, Holste H, Huttenhower C, Huttley G, Janssen S, Jarmusch AK, Jiang L, Kaehler B, Kang KB, Keefe CR, Keim P, Kelley ST, Knights D, Koester I, Kosciolek T, Kreps J, Langille MG, Lee J, Ley R, Liu Y, Loftfield E, Lozupone C, Maher M, Marotz C, Martin BD, McDonald D, McIver LJ, Melnik AV, Metcalf JL, Morgan SC, Morton J, Naimey AT, Navas-Molina JA, Nothias LF, Orchanian SB, Pearson T, Peoples SL, Petras D, Preuss ML, Pruesse E, Rasmussen LB, Rivers A, Robeson, II MS, Rosenthal P, Segata N, Shaffer M, Shiffer A, Sinha R, Song SJ, Spear JR, Swafford AD, Thompson LR, Torres PJ, Trinh P, Tripathi A, Turnbaugh PJ, Ul-Hasan S, van der Hooft JJ, Vargas F, Vázquez-Baeza Y, Vogtmann E, von Hippel M, Walters W, Wan Y, Wang M, Warren J, Weber KC, Williamson CH, Willis AD, Xu ZZ, Zaneveld JR, Zhang Y, Zhu Q, Knight R, Caporaso JG. 2018. QIIME 2: Reproducible, interactive, scalable, and extensible microbiome data science. PeerJ Preprints 6:e27295v2 https://doi.org/10.7287/peerj.preprints.27295v2
3. Mirarab, S., Nguyen, N. and Warnow, T., 2012. SEPP: SATé-enabled phylogenetic placement. In Biocomputing 2012 (pp. 247-258).
4. Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V. and Vanderplas, J., 2011. Scikit-learn: Machine learning in Python. Journal of machine learning research, 12(Oct), pp.2825-2830.
5. Price, M.N., Dehal, P.S. and Arkin, A.P., 2010. FastTree 2–approximately maximum-likelihood trees for large alignments. PloS one, 5(3), p.e9490.
6. Stéfan van der Walt, S. Chris Colbert and Gaël Varoquaux. The NumPy Array: A Structure for Efficient Numerical Computation, Computing in Science & Engineering, 13, 22-30 (2011), DOI:10.1109/MCSE.2011.37
7. Travis E, Oliphant. A guide to NumPy, USA: Trelgol Publishing, (2006).
