
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire common en tant que module
 *
 * Copyright (C) 2018 Cyrille Bagard
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "module.h"


#include "bits.h"
#include "fnv1a.h"
#include "hex.h"
#include "itoa.h"
#include "leb128.h"
#include "packed.h"
#include "pathname.h"
#include "pearson.h"
#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'common' à un module Python.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_common_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_COMMON_DOC                                         \
    "This module provides some tiny helpers for different use cases.\n" \
    "\n"                                                                \
    "The code for these features is shared between various parts of"    \
    " Chrysalide."

    static PyModuleDef py_chrysalide_common_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.common",
        .m_doc  = PYCHRYSALIDE_COMMON_DOC,

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_common_module);

    result = (module != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'common'.                       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_common_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = populate_common_module_with_fnv1a();
    if (result) result = populate_common_module_with_hex();
    if (result) result = populate_common_module_with_itoa();
    if (result) result = populate_common_module_with_leb128();
    if (result) result = populate_common_module_with_pathname();
    if (result) result = populate_common_module_with_pearson();

    if (result) result = ensure_python_bitfield_is_registered();
    if (result) result = ensure_python_packed_buffer_is_registered();

    assert(result);

    return result;

}
