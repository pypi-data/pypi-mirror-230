#!/bin/sh


arch=$1
header="opcodes/${arch}_opcodes.h"
headertmp="opcodes/opcodes_tmp_$arch.h"

echo "#ifndef ${arch}_def_tmp_h" > $headertmp
echo "#define ${arch}_def_tmp_h" >> $headertmp

target=armv7_read_${arch}_instr

needed=`grep $target $arch.c | sed "s/.*\(${target}_[^(]*\).*/\1/" | sort | uniq`

for n in $needed; do

	echo "  $n..."

	test -f $header && grep -q "$n(" $header
	if [ $? -ne 0 ]; then

		if [ $arch = "simd" ]; then
			echo "#define $n(r, a) NULL" >> $headertmp
		else
			echo "#define $n(r) NULL" >> $headertmp
		fi

	else

		echo "$n found in $header"

	fi

done

echo "#endif" >> $headertmp



