#§/bin/sh


if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <type>"
    exit
fi

rm -rf testcase_dir findings_dir

mkdir testcase_dir findings_dir

n=0

for enc in $( cat ../../tests/mangling/$1.py | grep decode_routine | cut -d\' -f 2 );
do

    echo -n $enc > testcase_dir/$( printf "%03d" $n )

    n=$(( n + 1 ))

done


#echo -n '_Z4makeI7FactoryiET_IT0_Ev' > testcase_dir/00

afl-fuzz -t 100 -m 4096 -i testcase_dir -o findings_dir -- ./$1
