# Bash scripts to import and preprocess data

This folder contains bash scripts to import and preprocess data. These scripts require [Qiime2](https://docs.qiime2.org/2019.4/tutorials/qiime2-for-experienced-microbiome-researchers/#data-processing-steps). We recommend creating a conda environment for [Qiime2](https://docs.qiime2.org/2019.4/install/). Let's assume that the name of this conda environment is **qiime2-2019.4**. To work with these scripts, you need to activate this environment using the following commnad

```
source activate qiime2-2019.4 
```

Then, you can check if Qiime is installed successfully, using

```
qiime --help
```

## Importing data to Qiime2 artifact format

You can use **import\_to\_qiime.sh** to import different types of data into qiime2 artifact. This script is based on the official tutorial available on [this link](https://docs.qiime2.org/2019.4/tutorials/importing/).

The data types that you can import into qiime2 using this script are

* Unaligned sequences in [FASTA](https://docs.qiime2.org/2019.4/tutorials/importing/#per-feature-unaligned-sequence-data-i-e-representative-fasta-sequences) format 

* Sequences with quality information in [FASTQ](https://docs.qiime2.org/2019.4/tutorials/importing/#sequence-data-with-sequence-quality-information-i-e-fastq) format
* Count tables in [BIOM](https://docs.qiime2.org/2019.4/tutorials/importing/#biom-v2-1-0) format
* Rooted [phylogeny](https://docs.qiime2.org/2019.4/tutorials/importing/#phylogenetic-trees)

### Importing FASTA file

To import unaligned seqeunces from FASTA format please use the following command. For more inofrmation regarding FASTA format please look at [here](https://en.wikipedia.org/wiki/FASTA).

```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh -i [PATH TO FASTA FILE]
```

Please note that the FASTA file should end in either **.fna** (e.g., sequences.fna), **.fasta** (e.g., sequences.fasta), or **.fas** (e.g., sequences.fas). The code will create the output in the same directory as input FASTA file, and using the same file name but ending in **.qza** (e.g., sequences.qza).

### Importing BIOM file

We typically store information regarding the features and samples in the compresse [Biom](http://biom-format.org/documentation/) format. To import Biom files, you can use the following command

```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh -i [PATH TO BIOM FILE]
```

Please note that the BIOM file should end in **.biom** (e.g., table.biom). The code will create the output in the same directory as input BIOM file, and using the same file name but ending in **.qza** (e.g., table.qza).

### Importing rooted phylogenies

We typically save phylogenies in [newick](https://en.wikipedia.org/wiki/Newick_format) format, and to import rooted phylogenyies into Qiime2 you can use the following command


```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh -i [PATH TO PHYLOGENY FILE]
```

Please note that the phylogeny file should end in either **.tre** or **.tree** (e.g., phylogeny.tre or phylogeny.tree). The code will create the output in the same directory as input phylogeny, and using the same file name but ending in **.qza** (e.g., phylogeny.qza).

### Importing FASTQ files

[FASTQ](https://en.wikipedia.org/wiki/FASTQ_format) files are sequences with quality informations. You could import them stored using different protocoles. The supported protocles are 

* **EMPSingleEnd**: [EMP](https://docs.qiime2.org/2019.4/tutorials/importing/#emp-protocol-multiplexed-single-end-fastq) protocol multiplexed single-end fastq
* **EMPPairedEnd**: [EMP](https://docs.qiime2.org/2019.4/tutorials/importing/#emp-protocol-multiplexed-paired-end-fastq) protocol multiplexed paired-end fastq
* **CasavaSingleEnd**: [Casava 1.8](https://docs.qiime2.org/2019.4/tutorials/importing/#casava-1-8-single-end-demultiplexed-fastq) single-end demultiplexed fastq
* **CasavaPairedEnd**: [Casava 1.8](https://docs.qiime2.org/2019.4/tutorials/importing/#casava-1-8-paired-end-demultiplexed-fastq) paired-end demultiplexed fastq
* **ManifestSingleEnd33**: Single-end fastq [Manifest](https://docs.qiime2.org/2019.4/tutorials/importing/#singleendfastqmanifestphred33v2) file format with PHRED offset 33
* **ManifestSingleEnd64**: Single-end fastq [Manifest](https://docs.qiime2.org/2019.4/tutorials/importing/#singleendfastqmanifestphred64v2) file format with PHRED offset 64
* **ManifestPairedEndP33**: Paired-end fastq [Manifest](https://docs.qiime2.org/2019.4/tutorials/importing/#pairedendfastqmanifestphred33v2) file format with PHRED offset 33
* **ManifestPairedEndP64**: Paired-end fastq [Manifest](https://docs.qiime2.org/2019.4/tutorials/importing/#pairedendfastqmanifestphred64v2) file format with PHRED offset 64

In FASTQ files, you should pass the protocols (examples are provided in bold in above bullets). Using **import\_to\_qiime.sh** to import FASTQ files will create multiple files in the same directory as provided by the user (using the **-i** option, look at the bottom for more information). The imported files will be written on a file ending in **.qza**.




#### EMP multiplexed single-end format 

You can import the directory containing files from EMP single-end FASTQ protocle into Qiime2 using the following command

```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh -i [input directory] -f EMPSingleEnd
``` 

**Note**: This example is from [here](https://docs.qiime2.org/2019.4/tutorials/importing/#emp-protocol-multiplexed-single-end-fastq). 

For example, you could create a directory and download the input sequences and barcodes using `wget`

```
mkdir emp-single-end-sequences
wget \
  -O "emp-single-end-sequences/barcodes.fastq.gz" \
  "https://data.qiime2.org/2019.4/tutorials/moving-pictures/emp-single-end-sequences/barcodes.fastq.gz"
 
wget \
  -O "emp-single-end-sequences/sequences.fastq.gz" \
  "https://data.qiime2.org/2019.4/tutorials/moving-pictures/emp-single-end-sequences/sequences.fastq.gz"
```

Then you can use the import the sequences using the following command

```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh -i emp-single-end-sequences -f EMPSingleEnd
```



Alternatively, you could download it using Qiime directly with the following command:

```
qiime tools import \
  --type EMPSingleEndSequences \
  --input-path emp-single-end-sequences \
  --output-path emp-single-end-sequences/emp_single_end.qza
```

The output of both commands will be **emp-single-end-sequences/emp\_single\_end.qza**, and is provide [here](https://docs.qiime2.org/2019.4/data/tutorials/importing/emp-single-end-sequences.qza) for downloading.


#### EMP multiplexed paired-end format 


Similar to the EMP single-end format, you can import the EMP multiplexed paired-end FASTQ format using the following command

```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh -i [input directory] -f EMPPairedEnd
``` 

**Note**: The following example is from [here](https://docs.qiime2.org/2019.4/tutorials/importing/#emp-protocol-multiplexed-single-end-fastq). 

For example, you could create a directory and download the input sequences and barcodes using `wget`

```
mkdir emp-paired-end-sequences
wget \
  -O "emp-paired-end-sequences/forward.fastq.gz" \
  "https://data.qiime2.org/2019.4/tutorials/atacama-soils/1p/forward.fastq.gz"
 
wget \
  -O "emp-paired-end-sequences/reverse.fastq.gz" \
  "https://data.qiime2.org/2019.4/tutorials/atacama-soils/1p/reverse.fastq.gz"
  
wget \
  -O "emp-paired-end-sequences/barcodes.fastq.gz" \
  "https://data.qiime2.org/2019.4/tutorials/atacama-soils/1p/barcodes.fastq.gz"
  
```

Then you can use the import the sequences using the following command

```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh -i emp-paired-end-sequences -f EMPPairedEnd
```



Alternatively, you could download it using Qiime directly with the following command:

```
qiime tools import \
  --type EMPPairedEndSequences \
  --input-path emp-paired-end-sequences \
  --output-path emp-paired-end-sequences/emp_paired_end.qza
```
The output of both commands will be **emp-paired-end-sequences/emp\_paired\_end.qza**, and is provide [here](https://docs.qiime2.org/2019.4/data/tutorials/importing/emp-paired-end-sequences.qza) for downloading.



#### Casava 1.8 demultiplexed format

You can import the directory containing files in Casava demultiplexed single-end/paired-end protocle into Qiime2 using the following command


```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh -i [input directory] -f [CasavaSingleEnd or CasavaPairedEnd]
``` 

**Note**: The following examples are from [here](https://docs.qiime2.org/2019.4/tutorials/importing/#casava-1-8-single-end-demultiplexed-fastq) for single-end and [here](https://docs.qiime2.org/2019.4/tutorials/importing/#casava-1-8-paired-end-demultiplexed-fastq) for paired-end formats. 

For example, you can download the input sequences and unarchive them using `wget` and `unzip` commands


```
wget \
  -O "casava-18-single-end-demultiplexed.zip" \
  "https://data.qiime2.org/2019.4/tutorials/importing/casava-18-single-end-demultiplexed.zip"
unzip -q casava-18-single-end-demultiplexed.zip
```

Then, you can import it into Qiime artifact using the following command

```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh -i casava-18-single-end-demultiplexed -f CasavaSingleEnd
```

Alternatively, you can import it using the following command

```
qiime tools import \
  --type 'SampleData[SequencesWithQuality]' \
  --input-path casava-18-single-end-demultiplexed \
  --input-format CasavaOneEightSingleLanePerSampleDirFmt \
  --output-path casava-18-single-end-demultiplexed/casava_demux_single_end.qza
```

Both commans will import the FASTQ files into **casava-18-single-end-demultiplexed/casava\_demux\_single\_end.qza**, a  Qiime artifact.

Similarly, you can download and unzip Casava paired-end format FASTQ files using the following commands

```
wget \
  -O "casava-18-paired-end-demultiplexed.zip" \
  "https://data.qiime2.org/2019.4/tutorials/importing/casava-18-paired-end-demultiplexed.zip"
unzip -q casava-18-paired-end-demultiplexed.zip
```
and you can import it into Qiime artifact using either the following command

```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh -i casava-18-paired-end-demultiplexed -f CasavaPairedEnd
```
or, alternately, using the following command

```
qiime tools import \
  --type 'SampleData[PairedEndSequencesWithQuality]' \
  --input-path casava-18-paired-end-demultiplexed \
  --input-format CasavaOneEightSingleLanePerSampleDirFmt \
  --output-path casava-18-paired-end-demultiplexed/casava_demux_paired_end.qza
```

Both will create the output Qiime2 file **casava-18-paired-end-demultiplexed/casava\_demux\_paired\_end.qza** available [here](https://docs.qiime2.org/2019.4/data/tutorials/importing/demux-paired-end.qza) to download.

#### Manifest format

If the format is one of the **Manifest** ones, you should also provide a [TSV](https://en.wikipedia.org/wiki/Tab-separated_values) file wiht information regarding the absolute paths to FASTQ files and sample names. Information regarding the format of this file is provided [here](https://docs.qiime2.org/2019.4/tutorials/importing/#id12). 

```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh -i [input directory] -f [ManifestSingleEnd33, ManifestSingleEnd64, ManifestPairedEndP33, or ManifestPairedEndP64] -m [path to manifest TSV file]
```

**Note**: The following examples is from [here](https://docs.qiime2.org/2019.4/tutorials/importing/#singleendfastqmanifestphred33v2).

For example, you can download the example FASTQ files and the manifest TSV file using the following command

```
wget \
  -O "se-33.zip" \
  "https://data.qiime2.org/2019.4/tutorials/importing/se-33.zip"
wget \
  -O "se-33-manifest" \
  "https://data.qiime2.org/2019.4/tutorials/importing/se-33-manifest"
unzip -q se-33.zip
```

Then we can import the FASTQ files into Qiime format using the following command

```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh -i se-33 -f ManifestSingleEnd33 -m se-33-manifest
```

Alternatively, you can use the following command to import the FASTQ files into Qiime2

```
qiime tools import \
  --type 'SampleData[SequencesWithQuality]' \
  --input-path se-33-manifest \
  --output-path se-33/manifest_single_end_demux.qza \
  --input-format SingleEndFastqManifestPhred33V2
```
Both should produce a Qiime2 artifact, **se-33/manifest\_single\_end\_demux.qza**, which can be downloaded from [here](https://docs.qiime2.org/2019.4/data/tutorials/importing/single-end-demux.qza).


In another example, you can dowlonad and unzip the following files from the Qiime2 tutorial [page](https://docs.qiime2.org/2019.4/tutorials/importing/#pairedendfastqmanifestphred64v2)

```
wget \
  -O "pe-64.zip" \
  "https://data.qiime2.org/2019.4/tutorials/importing/pe-64.zip"
wget \
  -O "pe-64-manifest" \
  "https://data.qiime2.org/2019.4/tutorials/importing/pe-64-manifest"
unzip -q pe-64.zip
```

Then you can import the FASTQ files into Qiime2 artifact using the folloing command

```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh -i pe-64 -f ManifestPairedEndP64 -m pe-64-manifest
```

Alternatively, you can use the following command to import the FASTQ files into Qiime2 artifact,

```
qiime tools import \
  --type 'SampleData[PairedEndSequencesWithQuality]' \
  --input-path pe-64-manifest \
  --output-path pe-64/manifest_paired_end_demux_64.qza \
  --input-format PairedEndFastqManifestPhred64V2
```

This will create the Qiime2 artifact **pe-64/manifest\_paired\_end\_demux\_64.qza**.

##### Create manifest TSV file

Alternatively, you can use the script (provided in this repository) **create\_manifest\_files.sh** to create this TSV file.

```
USAGE: create_manifest_file.sh [-h] [-i input directory]
                [-f whether the input FASTQ sequences are single-end or paired-end]
```

This code assumes that forward fastq files end in **R1.fastq.gz**, **R1.fastq**, **r1.fastq.gz**, **r1.fastq**, **forward.fastq.gz**, or **forward.fastq**.

Also, it assumes that the backward fastq files end in **R2.fastq.gz**, **R2.fastq** (if using R1 in the suffix), **r2.fastq.gz**, **r2.fastq** (if sing r1 in the suffix), **reverse.fastq.gz**, or **reverse.fastq** (if using forward in the suffix). The other assumption for the paired-end fastq files is that the only difference between the file path of forward and backward files is the suffixes listed above. For example, forward file path is **sample1\_R1.fastq.gz** and backwar is **sample1\_R2.fastq.gz**.

For example, using examples available on [Qiime2](https://docs.qiime2.org/2019.4/tutorials/importing/) web page for the manifest [single-end](https://docs.qiime2.org/2019.4/tutorials/importing/#singleendfastqmanifestphred33v2) and [paired-end](https://docs.qiime2.org/2019.4/tutorials/importing/#pairedendfastqmanifestphred64v2) formats, you can use the following commands to create a similar manifest TSV file


```
[PATH TO THIS GitHub REPO]/src/utils/shell/create_manifest_file.sh -i se-33 -f single-end
[PATH TO THIS GitHub REPO]/src/utils/shell/create_manifest_file.sh -i pe-33 -f paired-end
```

to create the **se-33/manifest.csv** and **pe-64/manifest.csv** files respectively.

Please note that, you need the following commands to download and unzip the required files before running the above commands

```
wget \
  -O "se-33.zip" \
  "https://data.qiime2.org/2019.4/tutorials/importing/se-33.zip"
unzip -q se-33.zip
wget \
  -O "pe-64.zip" \
  "https://data.qiime2.org/2019.4/tutorials/importing/pe-64.zip"
unzip -q pe-64.zip
```

#### Joining and filtering sequences



You could use **join\_and\_quality\_control.sh** to join (if using paired-end sequences) and apply quality control filtering on top of imported FASTQ files. 


```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh [-h] [-i input data path (ending in .qza (Qiime2 artifact))] [-f defines if the input data is single-end or paired-end. The inputs can be single-end or paired-end.]
```

If the input is paired-end, the joined file is available on a file with the same address and basename as input data (qza file), but ending in **.joined.qza** instead. Also, the filtered sequences (for both paired-end and single-end) will be available on a file with the same address and basename as input data (qza file) but ending in **.joined.filtered.qza**.

Then you can apply further filtering such as [Deblur](https://docs.qiime2.org/2019.4/tutorials/read-joining/#deblur) or [DADA2](https://docs.qiime2.org/2019.4/tutorials/moving-pictures/#option-1-dada2) to the output of this script.

For example, after importing the joined, demultiplexed, and filtered fastq files, you might wish to apply Deblur following the steps provided [here](https://docs.qiime2.org/2019.4/tutorials/read-joining/#deblur/). The proper command should be similar to

```
qiime deblur denoise-16S \
  --i-demultiplexed-seqs demux-joined-filtered.qza\
  --p-trim-length [some number] \
  --p-sample-stats \
  --o-representative-sequences rep-seqs.qza \
  --o-table table.qza \
  --o-stats deblur-stats.qza
``` 


### Export sequences from biom

Here we will assume that the DNA sequences are used as feature IDs (similar to [this](https://github.com/CognitiveHorizons/UCSD/blob/dev-embeddings/TADA/data/reference/TADA_input.tar.gz) example) in the biom table. If you have installed [biom](http://biom-format.org/), and you have a count table in **.biom** format, you can check this by using the following command 

```
biom table-ids -i [path to your count table file ending in biom format] --observations
```

This should list DNA sequences. For example, if I downloaded [this](https://github.com/CognitiveHorizons/UCSD/blob/dev-embeddings/TADA/data/reference/TADA_input.tar.gz) file, by running the following commands

```
tar xzvf TADA_input.tar.gz
biom table-ids -i Gevers/feature-frequency-filtered-table.3/feature-table.biom --observations | sort | head
```

you would see the following output

```
AACATAGGGGGCAAGCGTTGTCCGGAACCACTGGGCGTAAAGGGCGCGTAGGTGGTCTGTTAAGTCAGATGTGAAATGTAAGGGCTCAACCCTTAACGTGCATCTGATACTGGCAGACTTGAGTGCGGAAGAGGCAAGTGGAATTCCTAG
AACATAGGGGGCAAGCGTTGTCCGGAATCACTGGGCGTAAAGGGCGCGCAGGCGGTAAATTAAGTCAGGTGTGAAAGTTCGGGGCTCAACCCCGTGATTGCACCTGATACTGATAAACTAGAGTGTTGGAGAGGTAAGTGGAATTCCTAG
AACATAGGGGGCAAGCGTTGTCCGGAATCACTGGGCGTAAAGGGCGCGCAGGCGGTCTGTTAAGTCAGATGTGAAAGGTTAGGGCTCAACCCTGAACGTGCATCTGATACTGGCAGACTTGAGTATGGAAGAGGTAAGTGGAATTCCTAG
AACATAGGGGGCAAGCGTTGTCCGGAATCACTGGGCGTAAAGGGCGCGCAGGCGGTCTGTTAAGTCAGATGTGAAAGTTTAGGGCTCAACCCTGAACGTGCATCTGATACTGGCAGACTTGAGTATGGAAGAGGTAAGTGGAATTCCTAG
AACATAGGGGGCAAGCGTTGTCCGGAATCACTGGGCGTAAAGGGCGCGCAGGTGGTCTGTTAAGTCAGATGTGAAATGTAAGGGCTCAACCCTTAACGTGCATCTGATACTGGCAGACTTGAGTGCGGAAGAGGCAAGTGGAATTCCTAG
AACATAGGGGGCAAGCGTTGTCCGGAATCACTGGGCGTAAAGGGCGCGTAGGCGGTCTGTTAAGTCGGATGTGAAATGTAAGGGCTCAACCCTTAACGTGCATCCGATACTGGCAGACTTGAGTGCGGAAGAGGCAAGTGGAATTCCTAG
AACATAGGGGGCAAGCGTTGTCCGGAATCACTGGGCGTAAAGGGCGCGTAGGTGGTCTGTTAAGTCAGATGTGAAATGTAAGGGCTCAACCCTTAACGTGCATCTGATACTGGCAGACTTGAGTGCGGAAGAGGCAAGTGGAATTCCTAG
AACATAGGGGGCAAGCGTTGTCCGGAATCACTGGGCGTAAAGGGCGCGTAGGTGGTTTGTTAAGTCAGATGTGAAATGTAGGGGCTCAACCCCTAACGTGCATCTGATACTGGCAGACTTGAGTGCGGAAGAGGCAAGTGGAATTCCTAG
AACATAGGGGGCAAGCGTTGTCCGGAATTACTGGGCGTAAAGGGCGCGTAGGTGGTTTGTTAAGTCGGATGTGAAATGTAAGGGCTCAACCCTTAACGTGCATCCGATACTGGCAGACTTGAGTGCGGAAGAGGCAAGTGGAATTCCTAG
AACCTAGGGGGCAAGCGTTGTCCGGAATCACTGGGCGTAAAGGGCGCGTAGGTGGTCTGTTAAGTCAGATGTGAAATGTAAGGGCTCAACCCTTAACGTGCATCTGATACTGGCAGACTTGAGTGCGGAAGAGGCAAGTGGAATTCCTAG
``` 

To create the FASTA file that's required for reconstructing the phylogeny in this case, you need to first import the biom table into Qiita artifact and then export the sequences using the following set of commands

```
[PATH TO THIS GitHub REPO]/src/utils/shell/import_to_qiime.sh -i [table in biom format]
```

This will create a Qiita artifact with the same name and in the same directory of your original biom table ending in **biom.qza**. You can then use the following command to create the sequence file in FASTA format


```
[PATH TO THIS GitHub REPO]/src/utils/shell/export_seqs_from_biom.sh -i [path to the file ending in biom.qza ] -o [ the output directory]
```

This will create four new files in the output directory passed by the user named

* relabeled.dna-sequences.fna
* relabeled.dna-sequences.qza
* relabeled.feature-table.biom
* relabeled.feature-table.qza

User can use **relabeled.dna-sequences.fna** for phylogeny reconstruction, and **relabeled.feature-table.biom** for machine learning analyses. 

Please not that if you use [this](https://docs.qiime2.org/2019.4/tutorials/read-joining/) pipeline to apply Deblur filtering on your imported FASTQ files, you don't need to use **export\_seqs\_from\_biom.sh** to create the FASTA file and the biom tables. This pipeline creates both files in Qiime artifact, and to use them for data augmentation in TADA you can export them using the followin [command](https://docs.qiime2.org/2018.11/tutorials/exporting/)



```
qiime tools export --input-path [input deblured biom file in Qiime artifact] --output-path [output directory]
qiime tools export --input-path [input deblured FASTA file in Qiime artifact] --output-path [output directory]
```

For example, using the Qiime [example](https://docs.qiime2.org/2018.11/tutorials/exporting/), you can export the biom table from the Qiime artifact 

```
wget \
  -O "feature-table.qza" \
  "https://data.qiime2.org/2018.11/tutorials/exporting/feature-table.qza"
 qiime tools export \
  --input-path feature-table.qza \
  --output-path exported-feature-table
```

This will create the biom file under **exported-feature-table/feature-table.biom**.


## Reconstructing the phylogeny

To reconstruct the phylogeny one could use different methods, including closed-reference methods, where the tree is precomputed, de novo using methods usch as [FastTree-II](http://www.microbesonline.org/fasttree/), or insertion methods like [SEPP](https://github.com/smirarab/sepp/blob/master/sepp-package/README.md). For more information please visit this [page](https://github.com/qiime2/q2-fragment-insertion). Here, we will show how you could reconstruct the phylogeny from the input table using [SEPP](https://docs.qiime2.org/2019.4/plugins/available/fragment-insertion/sepp/).

```
qiime fragment-insertion sepp --i-representative-sequences rep-seqs.qza \
--p-threads [The number of threads to use (default 1)] --output-dir [output directory]
```

Using the example file provided [here](https://docs.qiime2.org/2017.10/data/tutorials/moving-pictures/), you can reconstruct the phylogeny using the following command

```
wget https://docs.qiime2.org/2017.10/data/tutorials/moving-pictures/rep-seqs.qza
qiime fragment-insertion sepp \
  --i-representative-sequences rep-seqs.qza \
  --o-tree insertion-tree.qza \
  --o-placements insertion-placements.qza
```

This will create the [phylogeny](https://github.com/biocore/q2-fragment-insertion/blob/master/Example/insertion-tree.qza?raw=true) (`insertion-tree.qza`) and the [placement](https://github.com/biocore/q2-fragment-insertion/blob/master/Example/insertion-placements.qza?raw=true) (`insertion-placements.qza`). 

### Closed reference OTU picking
For more information regarding the closed reference OTU picking please look at this [link](https://docs.qiime2.org/2019.4/tutorials/otu-clustering/).

## Applying different filters on feature tables
You could read more from the following [link](https://docs.qiime2.org/2019.4/tutorials/filtering/). 


## References
1. Bolyen E, Rideout JR, Dillon MR, Bokulich NA, Abnet C, Al-Ghalith GA, Alexander H, Alm EJ, Arumugam M, Asnicar F, Bai Y, Bisanz JE, Bittinger K, Brejnrod A, Brislawn CJ, Brown CT, Callahan BJ, Caraballo-Rodríguez AM, Chase J, Cope E, Da Silva R, Dorrestein PC, Douglas GM, Durall DM, Duvallet C, Edwardson CF, Ernst M, Estaki M, Fouquier J, Gauglitz JM, Gibson DL, Gonzalez A, Gorlick K, Guo J, Hillmann B, Holmes S, Holste H, Huttenhower C, Huttley G, Janssen S, Jarmusch AK, Jiang L, Kaehler B, Kang KB, Keefe CR, Keim P, Kelley ST, Knights D, Koester I, Kosciolek T, Kreps J, Langille MG, Lee J, Ley R, Liu Y, Loftfield E, Lozupone C, Maher M, Marotz C, Martin BD, McDonald D, McIver LJ, Melnik AV, Metcalf JL, Morgan SC, Morton J, Naimey AT, Navas-Molina JA, Nothias LF, Orchanian SB, Pearson T, Peoples SL, Petras D, Preuss ML, Pruesse E, Rasmussen LB, Rivers A, Robeson, II MS, Rosenthal P, Segata N, Shaffer M, Shiffer A, Sinha R, Song SJ, Spear JR, Swafford AD, Thompson LR, Torres PJ, Trinh P, Tripathi A, Turnbaugh PJ, Ul-Hasan S, van der Hooft JJ, Vargas F, Vázquez-Baeza Y, Vogtmann E, von Hippel M, Walters W, Wan Y, Wang M, Warren J, Weber KC, Williamson CH, Willis AD, Xu ZZ, Zaneveld JR, Zhang Y, Zhu Q, Knight R, Caporaso JG. 2018. QIIME 2: Reproducible, interactive, scalable, and extensible microbiome data science. PeerJ Preprints 6:e27295v2 https://doi.org/10.7287/peerj.preprints.27295v2
2. Mirarab, S., Nguyen, N. and Warnow, T., 2012. SEPP: SATé-enabled phylogenetic placement. In Biocomputing 2012 (pp. 247-258).
4. Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V. and Vanderplas, J., 2011. Scikit-learn: Machine learning in Python. Journal of machine learning research, 12(Oct), pp.2825-2830.
5. Price, M.N., Dehal, P.S. and Arkin, A.P., 2010. FastTree 2–approximately maximum-likelihood trees for large alignments. PloS one, 5(3), p.e9490.
6. Stéfan van der Walt, S. Chris Colbert and Gaël Varoquaux. The NumPy Array: A Structure for Efficient Numerical Computation, Computing in Science & Engineering, 13, 22-30 (2011), DOI:10.1109/MCSE.2011.37
7. Travis E, Oliphant. A guide to NumPy, USA: Trelgol Publishing, (2006).