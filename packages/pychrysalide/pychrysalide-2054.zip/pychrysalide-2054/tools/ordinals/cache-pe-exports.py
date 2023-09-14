
import argparse
import hashlib
import os

import pychrysalide
from pychrysalide.analysis.contents import FileContent
from pychrysalide.format import BinSymbol
from pychrysalide.format.pe import PeFormat



def write_header(directory, name):
    """Ecrit le fichier d'entête pour la transcription d'ordinaux."""

    content = '''
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cache_%s.h - prototypes pour la fourniture des ordinaux du fichier %s.dll
 *
 * Copyright (C) 2021 Cyrille Bagard
 *
 *  This file is part of Chrysalide.
 *
 *  Chrysalide is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  Chrysalide is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _PLUGINS_WINORDINALS_CACHE_%s_H
#define _PLUGINS_WINORDINALS_CACHE_%s_H


#include <stdint.h>



/* Indique la liste de bibliothèques enregistrées avec ordinaux. */
const char *find_%s_name_for_ordinal(uint16_t);



#endif  /* _PLUGINS_WINORDINALS_CACHE_%s_H */
''' \
    % (name, name, name.upper(), name.upper(), name, name.upper())

    with open(os.path.join(directory, 'cache_%s.h' % name), 'w') as fd:
        fd.write(content)


def write_code(directory, name, hashes, exported):
    """Ecrit le fichier d'entête pour la transcription d'ordinaux."""

    content_prologue = '''
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cache_%s.c - fourniture des ordinaux du fichier %s.dll
 *
 * Copyright (C) 2021 Cyrille Bagard
 *
 *  This file is part of Chrysalide.
 *
 *  Chrysalide is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  Chrysalide is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "cache_%s.h"


#include <stddef.h>



/**
 * Empreintes du fichier %s.dll :
 *
 *   - MD5 : %s
 *   - SHA1 : %s
 *   - SHA256 : %s
 */


/* Liste des ordinaux référencés */
''' \
    % (name, name, name, name, hashes['md5'], hashes['sha1'], hashes['sha256'])


    content_epilogue = '''


/******************************************************************************
*                                                                             *
*  Paramètres  : ordinal = valeur ordinale à considérer.                      *
*                                                                             *
*  Description : Fournit le nom du symbole associé à un ordinal donné.        *
*                                                                             *
*  Retour      : Désignation du symbole trouvé ou NULL en cas d'échec.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *find_%s_name_for_ordinal(uint16_t ordinal)
{
    const char *result;                     /* Désignation à renvoyer      */

    if (ordinal >= %u)
        result = NULL;

    else
        result = _%s_ordinals[ordinal];

    return result;

}
''' % (name, exported[-1][0] + 1, name)

    with open(os.path.join(directory, 'cache_%s.c' % name), 'w') as fd:

        fd.write(content_prologue)

        fd.write('static const char *_%s_ordinals[%u] = {\n' % (name, exported[-1][0] + 1))

        for e in exported:

            fd.write('    [%u] = "%s",\n' % (e[0], e[1]))

        fd.write('};\n')

        fd.write(content_epilogue)


def get_internal_name(filename):
    """Fournit le nom de la bibliothèque pour les désignations internes."""

    name = os.path.basename(filename)

    idx = name.find('.')

    name = name[:idx].lower()

    return name


def compute_hashs(filename):
    """Calcule les empreintes du fichier analysé."""

    with open(filename, 'rb') as fd:
        data = fd.read()

    hashes = {
        'md5': hashlib.md5(data).hexdigest(),
        'sha1': hashlib.sha1(data).hexdigest(),
        'sha256': hashlib.sha256(data).hexdigest(),
    }

    return hashes


def retrieve_ordinals(filename):
    """Etablit une liste ordonnée d'ordinaux."""

    cnt = FileContent(filename)

    fmt = PeFormat(cnt)
    fmt.analyze()

    exported = []

    for s in fmt.symbols:

        if s.status == BinSymbol.SymbolStatus.EXPORTED:

            exported.append([ s.ordinal, s.name ])

    exported = sorted(exported, key=lambda sym: sym[0])

    return exported


if __name__ == '__main__':
    """Point d'entrée du script."""

    parser = argparse.ArgumentParser()

    parser.add_argument('dll', help='path to the library to process')
    parser.add_argument('dir', help='output directory for the final C files')

    args = parser.parse_args()

    name = get_internal_name(args.dll)

    hashes = compute_hashs(args.dll)

    exported = retrieve_ordinals(args.dll)

    write_header(args.dir, name)

    write_code(args.dir, name, hashes, exported)
