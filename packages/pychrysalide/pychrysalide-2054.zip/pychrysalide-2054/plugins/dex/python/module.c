
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire dex en tant que module
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "class.h"
#include "field.h"
#include "format.h"
#include "method.h"
#include "pool.h"
#include "routine.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Ajoute le module 'format.dex' au module Python.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_format_dex_module_to_python_module(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *super;                        /* Module à compléter          */
    PyObject *module;                       /* Sous-module mis en place    */

#define DEX_MODULE_DOC                                                          \
    "This module provides several features to deal with the Dalvik Executable"  \
    " (DEX) format.\n"                                                          \
    "\n"                                                                        \
    "The layout of such a format is described at:"                              \
    " https://source.android.com/devices/tech/dalvik/dex-format"


    static PyModuleDef py_chrysalide_dex_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.format.dex",
        .m_doc = DEX_MODULE_DOC,

        .m_size = -1,

    };

    result = false;

    super = get_access_to_python_module("pychrysalide.format");

    module = build_python_module(super, &py_chrysalide_dex_module);

    result = (module != NULL);

    if (result) result = register_python_dex_class(module);
    if (result) result = register_python_dex_field(module);
    if (result) result = register_python_dex_format(module);
    if (result) result = register_python_dex_method(module);
    if (result) result = register_python_dex_pool(module);
    if (result) result = register_python_dex_routine(module);

    assert(result);

    return result;

}
