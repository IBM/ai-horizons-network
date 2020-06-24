#!/bin/bash
get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

# set -x
show_help(){
cat << EOF
USAGE: ${0##*/} [-h] [-i input data path (ending in .qza (Qiime2 artifact))]
                [-f defines if the input data is single-end or paired-end. The inputs can be single-end or paired-end.]
EOF
}
while getopts "hi:f:m:" opt; do
        case $opt in
        h)
                show_help
                exit 0
                ;;
        i)
                i=$OPTARG
                ;;
        f)
                f=$OPTARG
                ;;
        '?')
                printf "Unknown input option\n"
                show_help
                ;;
        esac
done

if [ -z $i ] || [ ! -s $i ]; then
  printf "Please provide the input Qiime2 artifact.\n"
  show_help
  exit 1
fi

if [ -z $f ]; then
  printf "Please provide if the input Qiime2 artifact belongs to paired-end or single-end FASTQ files.\n"
  show_help
  exit 1
fi

od=$(diraname $i)
ob=$(basename $i | sed -e 's/.qza//')

if [ "${f}" == "paired-end" ]; then
  qiime vsearch join-pairs --i-demultiplexed-seqs $i --o-joined-sequences $od/${ob}.joined.qza
  printf "The output of jojined paried end files are written on file $od/${ob}.joined.qza\n"
  qiime demux summarize --i-data $od/${ob}.joined.qza --o-visualization $od/${ob}.joined.qzv
  printf "The summary of joined data with read quality is written on file$od/${ob}.joined.qzv\n"
  qiime quality-filter q-score-joined --i-demux $od/${ob}.joined.qza --o-filtered-sequences $od/${ob}.joined.filtered.qza --o-filter-stats $od/${ob}.joined.filtered.stats.qza
  printf "The filtered seqeunces are witten on $od/${ob}.joined.filtered.qza, and the stats are written on $od/${ob}.joined.filtered.stats.qza\n"
elif [ "${f}" == "single-end" ]; then
  cp $i $od/${ob}.joined.qza
  qiime quality-filter q-score --i-demux $od/${ob}.qza --o-filtered-sequences $od/${ob}.joined.filtered.qza --o-filter-stats $od/${ob}.joined.filtered.stats.qza
  printf "The filtered seqeunces are witten on $od/${ob}.joined.filtered.qza, and the stats are written on $od/${ob}.joined.filtered.stats.qza\n"

else
  printf "Please use paired-end or single-end as the input to -f option\n"
  show_help
  exit 1
fi
