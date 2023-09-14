
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - équivalent Python partiel du fichier "plugins/dex/dex_def.h"
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


#include "constants.h"


#include <plugins/pychrysalide/helpers.h>


#include "../dex_def.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes communes pour le format Dex.          *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_python_dex_format_common_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "PUBLIC", ACC_PUBLIC);
    if (result) result = add_const_to_group(values, "PRIVATE", ACC_PRIVATE);
    if (result) result = add_const_to_group(values, "PROTECTED", ACC_PROTECTED);
    if (result) result = add_const_to_group(values, "STATIC", ACC_STATIC);
    if (result) result = add_const_to_group(values, "FINAL", ACC_FINAL);
    if (result) result = add_const_to_group(values, "SYNCHRONIZED", ACC_SYNCHRONIZED);
    if (result) result = add_const_to_group(values, "VOLATILE", ACC_VOLATILE);
    if (result) result = add_const_to_group(values, "BRIDGE", ACC_BRIDGE);
    if (result) result = add_const_to_group(values, "TRANSIENT", ACC_TRANSIENT);
    if (result) result = add_const_to_group(values, "VARARGS", ACC_VARARGS);
    if (result) result = add_const_to_group(values, "NATIVE", ACC_NATIVE);
    if (result) result = add_const_to_group(values, "INTERFACE", ACC_INTERFACE);
    if (result) result = add_const_to_group(values, "ABSTRACT", ACC_ABSTRACT);
    if (result) result = add_const_to_group(values, "STRICT", ACC_STRICT);
    if (result) result = add_const_to_group(values, "SYNTHETIC", ACC_SYNTHETIC);
    if (result) result = add_const_to_group(values, "ANNOTATION", ACC_ANNOTATION);
    if (result) result = add_const_to_group(values, "ENUM", ACC_ENUM);
    if (result) result = add_const_to_group(values, "CONSTRUCTOR", ACC_CONSTRUCTOR);
    if (result) result = add_const_to_group(values, "DECLARED_SYNCHRONIZED", ACC_DECLARED_SYNCHRONIZED);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, true, "AccessFlags", values,
                                            "Accessibility and overall properties of classes and class members.");

 exit:

    return result;

}
