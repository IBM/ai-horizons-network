#!/bin/bash
get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

# set -x
show_help(){
cat << EOF
USAGE: ${0##*/} [-h] [-i input data path]
                [-f format of fastq file (optional) to be used if input to
                import code is a manifest format, options are:
                              EMPSingleEnd,
                              EMPPairedEnd,
                              CasavaSingleEnd,
                              CasavaPairedEnd,
                              ManifestSingleEnd33,
                              ManifestSingleEnd64,
                              ManifestPairedEndP33,
                              ManifestPairedEndP64]
                [-m manifest file in csv format (optional, to be used with manifest formats)]
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
        m)
                m=$OPTARG
                ;;
        '?')
                printf "Unknown input option\n"
                show_help
                ;;
        esac
done

if [ -z "$i" ]; then
  printf "Enter data path\n"
  show_help
  exit 1
fi
if [ ! -f "$i" ] && [ ! -d "$i" ]; then
  printf "$i doesn't exist! Please double check the path.\n"
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
t=""
if [ -z "$t" ]; then
  gfq=$(echo "${i}" | grep ".fastq\|.fastq.gz" )
  gtr=$(echo "${i}" | grep ".tre\|.tree")
  gfs=$(echo "${i}" | grep ".fasta\|.fas\|.fna")
  gbm=$(echo "${i}" | grep ".biom")

  if [ -d "${i}" ] ; then
    echo "$i is a directory";
    t="fastq"
    manfest=$(echo $f | grep "Manifest")
    if [ "$manfest" != "" ] && [ -z "$m" ]; then
      printf "Please provide the manifest csv file. For more information regarding this format please visit
      https://docs.qiime2.org/2019.4/tutorials/importing/#fastq-manifest-formats.\n"
      show_help
    elif [ "$manfest" != "" ] && [ ! -s "$m" ]; then
      printf "Please provide the manifest csv file. For more information regarding this format please visit
      https://docs.qiime2.org/2019.4/tutorials/importing/#fastq-manifest-formats.\n"
      show_help
    fi
  elif [ ! -z $gfs ]; then
    t="fasta"
    echo "The input format is recognized! $i is a fasta file."
  elif [ ! -z $gtr ]; then
    t="phylo"
    echo "The input format is recognized! $i is a phylogeny file."
  elif [ ! -z $gbm ]; then
    t="biom"
    echo "The input format is recognized! $i is a biom file."

  else
    echo "The input file format is not recognizable!
    The options are directory (checks if exists, this works for fastq files),
    fastq file format (should be a directory),
    fasta file format (ending with .fas, .fna, or .fasta),
    phylogeny (ending in .tre or .tree), or biom format (ending in .biom)."
  fi
fi

base=$(basename $i)
dir=$(dirname $i)
no_format=$(echo $base | sed -e "s/$t//" | sed -e "s/\.$//")


if [ "${t}" == "fasta" ]; then
  qiime tools import --input-path $i --output-path $dir/"${no_format}".fasta.qza --type 'FeatureData[Sequences]'
  printf "The output is written on file $dir/${no_format}.fasta.qza\n"

elif [ "${t}" == "phylo" ]; then
  qiime tools import --input-path $i --output-path $dir/"${no_format}".phylo.qza --type 'Phylogeny[Rooted]'
  printf "The output is written on file $dir/${no_format}.phylo.qza\n"
elif [ "${t}" == "biom" ]; then
  qiime tools import --input-path $i --output-path $dir/"${no_format}".biom.qza --type 'FeatureTable[Frequency]' --input-format "BIOMV210Format"
  printf "The output is written on file $dir/${no_format}.biom.qza.\n"

elif [ "${t}" == "fastq" ]; then
  if [ "${f}" == "EMPSingleEnd" ]; then
    qiime tools import --input-path $i --output-path $dir/${no_format}/emp_single_end.qza --type EMPSingleEndSequences
    printf "The output is written on file $dir/${no_format}/emp_single_end.qza\n"
  elif [ "${f}" == "EMPPairedEnd" ]; then
    qiime tools import --input-path $i --output-path $dir/${no_format}/emp_paired_end.qza --type EMPPairedEndSequences
    printf "The output is written on file $dir/${no_format}/emp_paired_end.qza\n"
  elif [ "${f}" == "CasavaSingleEnd" ]; then
    qiime tools import --input-path $i --output-path $dir/${no_format}/casava_demux_single_end.qza --type 'SampleData[SequencesWithQuality]' --input-format 'CasavaOneEightSingleLanePerSampleDirFmt'

    printf "The output is written on file $dir/${no_format}/casava_demux_single_end.qza\n"
  elif [ "${f}" == "CasavaPairedEnd" ]; then
    qiime tools import --input-path $i --output-path $dir/${no_format}/casava_demux_paired_end.qza --type 'SampleData[PairedEndSequencesWithQuality]' --input-format 'CasavaOneEightSingleLanePerSampleDirFmt'
    printf "The output is written on file $dir/${no_format}/casava_demux_paired_end.qza\n"
  elif [ "${f}" == "ManifestSingleEnd33" ] || [ "${f}" == "ManifestSingleEnd64" ] || [ "${f}" == "ManifestPairedEndP33" ] || [ "${f}" == "ManifestPairedEndP64" ]; then

    if [ "${f}" == "ManifestSingleEnd33" ] || [ "${f}" == "ManifestSingleEnd64" ]; then
      if [ "${f}" == "ManifestSingleEnd33" ] ; then
        format='SingleEndFastqManifestPhred33V2'
      else
        format='SingleEndFastqManifestPhred64V2'
      fi
      typed='SampleData[SequencesWithQuality]'
      out='manifest_single_end_demux'
    else
      typed="SampleData[PairedEndSequencesWithQuality]"
      if [ "${f}" == "ManifestPairedEndP33" ]; then
        out='manifest_paired_end_demux_33'
        format='PairedEndFastqManifestPhred33V2'
      else
        out='manifest_paired_end_demux_64'
        format='PairedEndFastqManifestPhred64V2'
      fi
    fi
    cp $(get_abs_filename $m)  $dir/"${no_format}"/"manifest.csv"
    qiime tools import --type $typed --input-path $dir/"${no_format}"/"manifest.csv" --output-path $dir/"${no_format}"/"${out}".qza   --input-format $format
    printf "The output is written on file $dir/${no_format}/${out}.qza\n"
  else
    printf "The fastq file format is not recognized. The options are EMPSingleEnd, EMPPairedEnd, CasavaSingleEnd, CasavaPairedEnd, ManifestSingleEnd33, ManifestSingleEnd64, ManifestPairedEndP33, ManifestPairedEndP64\n"
    show_help
    exit 1
  fi
fi
