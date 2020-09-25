#!/bin/bash
#$ -cwd
#$ -l h_vmem=16G
#$ -m abe
#$ -j y

set -e;

usage(){
cat << EOF
USAGE: $0 -i <FASTQ> -d <DATABASE> -o <OUTDIR> -p <PREFIX> [OPTIONS]

OPTIONS:
   -i      Input a FASTQ file (singleton or pair-end sequences separated by comma)
   -d      Database
   -n      Additional options for centrifuge
   -o      Output directory
   -p      Output prefix
   -t      Number of threads (default: 24)
   -h      help
EOF
}

rootdir=$( cd $(dirname $0) ; pwd -P )

FASTQ=
REFDB=/data/centrifuge/p_compressed+h+v
PREFIX=
OUTPATH=
THREADS=1
OPTIONS=

while getopts "i:d:o:p:t:n:h" OPTION
do
     case $OPTION in
        i) FASTQ=$OPTARG
           ;;
        d) REFDB=$OPTARG
           ;;
        o) OUTPATH=$OPTARG
           ;;
        p) PREFIX=$OPTARG
           ;;
        t) THREADS=$OPTARG
           ;;
        n) OPTIONS=$OPTARG
           ;;
        h) usage
           exit
           ;;
     esac
done

if [[ -z "$FASTQ" || -z "$OUTPATH" || -z "$PREFIX" ]]
then
     usage;
     exit 1;
fi

rootdir=$( cd $(dirname $0) ; pwd -P )
export PATH=$rootdir:$PATH;

mkdir -p $OUTPATH

echo "[BEGIN]"

set -x;
time centrifuge -x $REFDB $OPTIONS -p $THREADS -U $FASTQ -S $OUTPATH/$PREFIX.classification.csv --report-file $OUTPATH/$PREFIX.report.txt
time centrifuge-kreport -x $REFDB $OUTPATH/$PREFIX.classification.csv > $OUTPATH/$PREFIX.kreport.csv
set +e;

#generate out.list
convert_krakenRep2list.pl < $OUTPATH/$PREFIX.kreport.csv > $OUTPATH/$PREFIX.out.list
convert_krakenRep2tabTree.pl < $OUTPATH/$PREFIX.kreport.csv > $OUTPATH/$PREFIX.out.tab_tree

# Make Krona plot
ktImportText  $OUTPATH/$PREFIX.out.tab_tree -o $OUTPATH/$PREFIX.krona.html

#generate Tree Dendrogram
phylo_dot_plot.pl -i $OUTPATH/$PREFIX.out.tab_tree -p $OUTPATH/$PREFIX.tree -t 'Centrifuge'

# This is old 101817. See above for current Krona plot creation (consistent with the method used for other tools).
#generate krona plot
#cat $OUTPATH/$PREFIX.out.list | awk -F\\t "{if(\$4>0 && \$4!=\"ASSIGNED\") print \$5\"\t\"\$4}" > $OUTPATH/$PREFIX.out.krona
#ktImportTaxonomy -t 1 -s 2 -o $OUTPATH/$PREFIX.krona.html $OUTPATH/$PREFIX.out.krona

#preparing megan CSV file
cat $OUTPATH/$PREFIX.out.list | awk -F\\t "{if(\$4>0 && \$4!=\"ASSIGNED\") print \$2\"\t\"\$4}" > $OUTPATH/$PREFIX.out.megan

set +x;
echo "";
echo "[END] $OUTPATH $PREFIX";
