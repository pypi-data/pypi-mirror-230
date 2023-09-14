
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire db en tant que module
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include "admin.h"
#include "analyst.h"
#include "certs.h"
#include "client.h"
#include "collection.h"
#include "item.h"
#include "server.h"
#include "items/module.h"
#include "../../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'analysis.db' à un module Python.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_analysis_db_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

    static PyModuleDef py_chrysalide_analysis_db_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.analysis.db",
        .m_doc = "Python module for Chrysalide.analysis.db",

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_analysis_db_module);

    result = (module != NULL);

    if (result) result = add_analysis_db_items_module(module);

    if (!result)
        Py_XDECREF(module);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'analysis.db'.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_analysis_db_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = ensure_python_admin_client_is_registered();
    if (result) result = ensure_python_analyst_client_is_registered();
    if (result) result = ensure_python_certs_is_registered();
    if (result) result = ensure_python_hub_client_is_registered();
    if (result) result = ensure_python_db_collection_is_registered();
    if (result) result = ensure_python_db_item_is_registered();
    if (result) result = ensure_python_hub_server_is_registered();

    if (result) result = populate_analysis_db_items_module();

    assert(result);

    return result;

}
