
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - ajout des constantes de base pour les extensions à la GLib
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#include <i18n.h>
#include <gtkext/graph/edge.h>


#include "../../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes relatives aux liens de graphiques.    *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_graph_edge_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "DEFAULT", EGC_DEFAULT);
    if (result) result = add_const_to_group(values, "GREEN", EGC_GREEN);
    if (result) result = add_const_to_group(values, "RED", EGC_RED);
    if (result) result = add_const_to_group(values, "BLUE", EGC_BLUE);
    if (result) result = add_const_to_group(values, "DASHED_GRAY", EGC_DASHED_GRAY);
    if (result) result = add_const_to_group(values, "COUNT", EGC_COUNT);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "EdgeColor", values,
                                            "Rendering color for graphical edges.");

 exit:

    return result;

}
