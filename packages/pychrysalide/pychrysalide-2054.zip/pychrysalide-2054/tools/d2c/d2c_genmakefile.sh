#!/bin/sh

if [ $# -lt 2 ]; then

    echo "Usage: $0 <opcodes dir> <arch [arch [arch ...]]"
    exit 1

fi

workingdir=$1

shift 1

OLDPWD=$PWD

MAKEFILE_TMP=gencode.mk.tmp
MAKEFILE_EXT=gencode.mk

cd ${workingdir}

echo=`which echo`

rm -f ${MAKEFILE_TMP}


# Génération de la liste des sources

$echo >> ${MAKEFILE_TMP}

$echo -n "GENERATED_FILES = " >> ${MAKEFILE_TMP}


# Avec ou sans multiples architectures, ces fichiers sont la base !

SOURCES=`find . -type f -and \( -name "descriptions.h" -or -name "hooks.h" -or -name "identifiers.h" -or -name "keywords.h" -or -name "subidentifiers.h" \) -exec basename {} \; | sort`

for src in $SOURCES;
do
    $echo -ne " \\" >> ${MAKEFILE_TMP}
    $echo -ne "\n\t${src}" >> ${MAKEFILE_TMP}

done


for arch in $*;
do
    if [ ${arch} = "-" ]; then
        arch_name=""
    else
        arch_name="${arch}_"
    fi

    SOURCES=`find . -type f -name "${arch_name}opcodes.h" -exec basename {} \; | sort`

    for src in $SOURCES;
    do
        $echo -ne " \\" >> ${MAKEFILE_TMP}
        $echo -ne "\n\t${src}" >> ${MAKEFILE_TMP}

    done

    SOURCES=`find . -type f -name "${arch_name}*.c" -exec basename {} \; | sort`

    for src in $SOURCES;
    do
        $echo -ne " \\" >> ${MAKEFILE_TMP}
        $echo -ne "\n\t${src}" >> ${MAKEFILE_TMP}

    done

done

$echo >> ${MAKEFILE_TMP}

$echo >> ${MAKEFILE_TMP}


# Validation finale

if [ ! -f ${MAKEFILE_EXT} ]; then

    mv ${MAKEFILE_TMP} ${MAKEFILE_EXT}

else

    hash_tmp=`md5sum ${MAKEFILE_TMP} | cut -d ' ' -f 1`
    hash_ext=`md5sum ${MAKEFILE_EXT} | cut -d ' ' -f 1`

    if [ "${hash_tmp}" = "${hash_ext}" ]; then

        rm -f ${MAKEFILE_TMP}

        echo "${MAKEFILE_EXT} is up to date."

    else

        rm -f ${MAKEFILE_EXT}
        mv ${MAKEFILE_TMP} ${MAKEFILE_EXT}

        echo "${MAKEFILE_EXT} is updated."

    fi

fi

cd ${OLDPWD}
