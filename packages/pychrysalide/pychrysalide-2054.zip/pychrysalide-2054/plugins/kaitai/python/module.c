
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire kaitai en tant que module
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include <Python.h>


#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>


#include "array.h"
#include "parser.h"
#include "record.h"
#include "scope.h"
#include "stream.h"
#include "parsers/module.h"
#include "records/module.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Ajoute le module 'plugins.kaitai' au module Python.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_kaitai_module_to_python_module(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *super;                        /* Module à compléter          */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_PLUGINS_KAITAI_DOC                                                         \
    "kaitai is a module trying to reverse some of the effects produced by ProGuard.\n"          \
    "\n"                                                                                        \
    "Its action is focused on reverting name obfuscation by running binary diffing against"     \
    " OpenSource packages from the AOSP."

    static PyModuleDef py_chrysalide_kaitai_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.plugins.kaitai",
        .m_doc = PYCHRYSALIDE_PLUGINS_KAITAI_DOC,

        .m_size = -1,

    };

    result = false;

    super = get_access_to_python_module("pychrysalide.plugins");

    module = build_python_module(super, &py_chrysalide_kaitai_module);

    result = (module != NULL);

    assert(result);

    if (result) result = add_kaitai_parsers_module();
    if (result) result = add_kaitai_records_module();

    if (!result)
        Py_XDECREF(module);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'plugins.kaitai'.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_kaitai_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = ensure_python_kaitai_array_is_registered();
    if (result) result = ensure_python_kaitai_parser_is_registered();
    if (result) result = ensure_python_match_record_is_registered();
    if (result) result = ensure_python_kaitai_scope_is_registered();
    if (result) result = ensure_python_kaitai_stream_is_registered();

    if (result) result = populate_kaitai_parsers_module();
    if (result) result = populate_kaitai_records_module();

    assert(result);

    return result;

}
