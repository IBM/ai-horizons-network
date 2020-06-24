#!/bin/bash
get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

# set -x
show_help(){
cat << EOF
This code assumes that forward fastq files end in
                  R1.fastq.gz, R1.fastq,
                  r1.fastq.gz, r1.fastq,
                  forward.fastq.gz, or forward.fastq.
Also, it assumes that the backward fastq files end in
                  R2.fastq.gz, R2.fastq (if using R1 in the suffix),
                  r2.fastq.gz, r2.fastq (if using r1 in the suffix),
                  reverse.fastq.gz, or reverse.fastq (if using forward in the suffix).
The other assumption for the paired-end fastq files is that the only difference
between the file path of forward and backward files is the suffixes listed above.
For example, forward file path is sample1_R1.fastq.gz and backwar is
sample1_R2.fastq.gz.
USAGE: ${0##*/} [-h] [-i input directory]
                [-f whether the input FASTQ sequences are single-end or paired-end]
EOF
}
while getopts "hi:f:" opt; do
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
if [ -z $i ] || [ ! -d $i ]; then
  printf "Please provide the directory of fastq files\n"
  show_help
  exit 1
fi



if [ -d "$i" ] && [ -z "$f" ]; then
  printf "Please provide the fastq format.\n"
  show_help
  exit 1
else
  i=$(get_abs_filename $i)
fi

tmp_dir=`mktemp -d`
t="fastq"

base=$(basename $i)
dir=$(dirname $i)
no_format=$(echo $base | sed -e "s/$t//" | sed -e "s/\.$//")



if [ "${f}" == "single-end" ]; then
    printf "sample-id\tabsolute-filepath\n" > $dir/"${no_format}"/"manifest.csv"
    for x in `find $i -type f -name "*.fastq*"`; do
      forw=$(get_abs_filename $x)
      sampleID=$(basename $x | sed -e 's/.fastq.*//')
      printf "$sampleID\t$forw\n" >> $dir/"${no_format}"/"manifest.csv"
    done
  l=`cat "${dir}"/"${no_format}"/"manifest.csv" | wc -l`
  l=$(( $l - 1 ))
  if [  $l -lt 1 ]; then
    printf "No fastq files found! Please double check the paths!\n"
    show_help
    exit 1
  else
    printf "The number of fastq files is $l.\n"
  fi
  while read r; do
    header=$(echo $r | grep "absolute-filepath")
    if [ "$header" == "" ]; then
      p=$(echo $r | awk '{print $2}')
      if [ ! -s $p ]; then
        printf "There is something wrong with the fastq file $p\n"
      fi
    fi
  done < $dir/"${no_format}"/"manifest.csv"
elif [ ${f} == "paired-end" ]; then
    printf "sample-id\tforward-absolute-filepath\treverse-absolute-filepath\n" > $dir/"${no_format}"/"manifest.csv"
    for x in `find $i -type f -regex  ".*\(R1\|forward\|r1\).*.fastq.*$" |  grep "fastq"`; do
      forw=$(get_abs_filename $x)
      echo $forw
      sampleID=$(basename $x | sed -e 's/.fastq.*//' | sed -e 's/\(-\|_\|\.\)r1//' | sed -e 's/\(-\|_\|\.\)R1//' | sed -e 's/\(-\|_\|\.\)forward//')
      revs=$(echo $forw | sed -e 's/R1/R2/' | sed -e 's/r1/r2/' | sed -e 's/forward/reverse/')
      if [ ! -s "$forw" ]; then
        printf "There is something wrong with the file $forw! Forward files should end with R1.fastq.gz or R1.fastq or forward.fastq.gz or forward.fastq.\n";
        show_help
        exit 1
      fi
      if [ ! -s "$revs" ]; then
        printf "There is something wrong with the file $revs! Reverse files should end with R2.fastq.gz or R2.fastq or reverse.fastq.gz or reverse.fastq.\n";
        show_help
        exit 1
      fi
      printf "$sampleID\t$forw\t$revs\n" >> $dir/"${no_format}"/"manifest.csv"
    done
    l=`cat "${dir}"/"${no_format}"/"manifest.csv" | wc -l`
    l=$(( $l - 1 ))
    if [  $l -lt 1 ]; then
      printf "No fastq files found! Please double check the paths!\n"
      show_help
      exit 1
    else
      printf "The number of fastq files is $l.\n"
    fi
    while read r; do
      header=$(echo $r | grep "absolute-filepath" )
      if [ "$header" == "" ]; then
        pf=$(echo $r | awk '{print $2}')
        pr=$(echo $r | awk '{print $3}')
        if [ ! -s $pf ]; then
          printf "There is something wrong with the forward fastq file $p\n"
        fi
        if [ ! -s $pr ];then
          printf "There is something wrong with the backward fastq file $p\n"
        fi
      fi
    done < $dir/"${no_format}"/"manifest.csv"
else
  printf "The input FASTQ files should be either single-end or paired-end, but $f was passed.\n"
  show_help
  exit 1
fi
printf "The manifest file is created and available at $dir/${no_format}/manifest.csv\n"
