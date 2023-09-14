
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire types en tant que module
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


#include <assert.h>


#include "array.h"
#include "basic.h"
#include "cse.h"
#include "encaps.h"
#include "expr.h"
#include "literal.h"
#include "override.h"
#include "proto.h"
#include "template.h"
#include "../../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'analysis.types' à un module Python.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_analysis_types_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

    static PyModuleDef py_chrysalide_analysis_types_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.analysis.types",
        .m_doc = "Python module for Chrysalide.analysis.types",

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_analysis_types_module);

    result = (module != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'analysis.types'.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_analysis_types_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = ensure_python_array_type_is_registered();
    if (result) result = ensure_python_basic_type_is_registered();
    if (result) result = ensure_python_class_enum_type_is_registered();
    if (result) result = ensure_python_expr_type_is_registered();
    if (result) result = ensure_python_encapsulated_type_is_registered();
    if (result) result = ensure_python_literal_type_is_registered();
    if (result) result = ensure_python_override_type_is_registered();
    if (result) result = ensure_python_proto_type_is_registered();
    if (result) result = ensure_python_template_type_is_registered();

    assert(result);

    return result;

}
