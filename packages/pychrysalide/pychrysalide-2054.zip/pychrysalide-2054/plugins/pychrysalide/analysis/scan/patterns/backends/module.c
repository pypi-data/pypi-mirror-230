
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire backends en tant que module
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#include "acism.h"
#include "bitap.h"
#include "../../../../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'analysis.....backends' à un module Python. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_analysis_scan_patterns_backends_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_ANALYSIS_SCAN_PATTERNS_BACKENDS_MODULE_DOC                   \
    "This module provide all the features useful for scanning"  \
    " binary contents."

    static PyModuleDef py_chrysalide_analysis_scan_patterns_backends_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.analysis.scan.patterns.backends",
        .m_doc = PYCHRYSALIDE_ANALYSIS_SCAN_PATTERNS_BACKENDS_MODULE_DOC,

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_analysis_scan_patterns_backends_module);

    result = (module != NULL);

    if (!result)
        Py_XDECREF(module);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'analysis....patterns.backends'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_analysis_scan_patterns_backends_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = ensure_python_acism_backend_is_registered();
    if (result) result = ensure_python_bitap_backend_is_registered();

    assert(result);

    return result;

}
