
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - ajout des constantes liées aux bases de données
 *
 * Copyright (C) 2019-2020 Cyrille Bagard
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


#include "constants.h"


#include <analysis/db/analyst.h>
#include <analysis/db/item.h>
#include <analysis/db/server.h>


#include "../../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes relatives au protocole.               *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_db_protocol_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "BOOKMARKS", DBF_BOOKMARKS);
    if (result) result = add_const_to_group(values, "COMMENTS", DBF_COMMENTS);
    if (result) result = add_const_to_group(values, "MOVES", DBF_MOVES);
    if (result) result = add_const_to_group(values, "DISPLAY_SWITCHERS", DBF_DISPLAY_SWITCHERS);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "DBFeatures", values,
                                            "Features provided by database items.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes pour les éléments de base de données. *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_db_item_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "NONE", DIF_NONE);
    if (result) result = add_const_to_group(values, "ERASER", DIF_ERASER);
    if (result) result = add_const_to_group(values, "UPDATED", DIF_UPDATED);
    if (result) result = add_const_to_group(values, "VOLATILE", DIF_VOLATILE);
    if (result) result = add_const_to_group(values, "BROKEN", DIF_BROKEN);
    if (result) result = add_const_to_group(values, "DISABLED", DIF_DISABLED);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "DbItemFlags", values,
                                            "Properties of a database item.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes pour les serveurs de données.         *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_hub_server_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "FAILURE", SSS_FAILURE);
    if (result) result = add_const_to_group(values, "SUCCESS", SSS_SUCCESS);
    if (result) result = add_const_to_group(values, "ALREADY_RUNNING", SSS_ALREADY_RUNNING);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "ServerStartStatus", values,
                                            "Status of a server start.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes pour les indications de chargement.   *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_loading_status_hint_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "READY", LSH_READY);
    if (result) result = add_const_to_group(values, "ON_WAIT_LIST", LSH_ON_WAIT_LIST);
    if (result) result = add_const_to_group(values, "NEED_CONTENT", LSH_NEED_CONTENT);
    if (result) result = add_const_to_group(values, "NEED_FORMAT", LSH_NEED_FORMAT);
    if (result) result = add_const_to_group(values, "NEED_ARCH", LSH_NEED_ARCH);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type_with_pyg_enum(type, false, "LoadingStatusHint", values,
                                                          "Indication about a loading process state.",
                                                          G_TYPE_LOADING_STATUS_HINT);

 exit:

    return result;

}
