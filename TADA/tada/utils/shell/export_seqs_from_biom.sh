#!/bin/bash
get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pyDIR=$(get_abs_filename $DIR/../python/)

# set -x
show_help(){
cat << EOF
USAGE: ${0##*/} [-h] [-i input data path in Qiime2 format (.qza)] [-o output directory]
EOF
}
c=0
while getopts "hi:" opt; do
        case $opt in
        h)
                show_help
                exit 0
                ;;
        i)
                i=$OPTARG
                ;;
        o)
                o=$OPTARG
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
if [ -z "$o" ]; then
    printf "Enter the output directory path\n"
    show_help
    exit 1
fi
if [ ! -d "$o" ]; then
    printf "The output directory path doesn't exist\n"
    show_help
    exit 1
fi
if [ ! -f "$i" ]; then
        printf "$i doesn't exist! Please double check the path.\n"
        show_help
        exit 1
else
        i=$(get_abs_filename $i)
fi
o=$(get_abs_filename $o)
tmp_dir=`mktemp -d`
qiime tools export --input-path $i --output-path $tmp_dir
biom table-ids -i $tmp_dir/feature-table.biom --observations | xargs -I@ sh -c 'echo ">@"; echo "@"' > $tmp_dir/orig_dna_sequences.fna
python $pyDIR/relabel_seq_names.py $tmp_dir/orig_dna_sequences.fna $tmp_dir/dna-sequences.fna


orig_path=`pwd`

cd $tmp_dir

python $pyDIR/update_ids_biom.py feature-table.biom dna-sequences.fna

$DIR/import_to_qiime.sh -i `pwd`/relabeled.feature-table.biom

$DIR/import_to_qiime.sh -i `pwd`/dna-sequences.fna

cp `pwd`/dna-sequences.fna  $o/relabeled.dna-sequences.fna
cp `pwd`/dna-sequences.qza $o/relabeled.dna-sequences.qza
cp `pwd`/relabeled.feature-table.qza $o/
cp `pwd`/relabeled.feature-table.biom $o/
