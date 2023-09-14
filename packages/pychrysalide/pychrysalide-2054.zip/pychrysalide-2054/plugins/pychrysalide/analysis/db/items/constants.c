
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.c - ajout des constantes liées aux éléments de base
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
#include <analysis/db/items/comment.h>


#include "../../../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dont le dictionnaire est à compléter.            *
*                                                                             *
*  Description : Définit les constantes relatives aux commentaires de base.   *
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_db_comment_constants(PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *values;                       /* Groupe de valeurs à établir */

    values = PyDict_New();

    result = add_const_to_group(values, "INLINED", CET_INLINED);
    if (result) result = add_const_to_group(values, "REPEATED", CET_REPEATED);
    if (result) result = add_const_to_group(values, "BEFORE", CET_BEFORE);
    if (result) result = add_const_to_group(values, "AFTER", CET_AFTER);

    if (!result)
    {
        Py_DECREF(values);
        goto exit;
    }

    result = attach_constants_group_to_type(type, false, "CommentEmbeddingType", values,
                                            "Kinds of insertion for comments.");

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en constante CommentEmbeddingType.        *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_comment_embedding_type(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */
    unsigned long value;                    /* Valeur récupérée            */

    result = PyObject_IsInstance(arg, (PyObject *)&PyLong_Type);

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to CommentEmbeddingType");
            break;

        case 1:
            value = PyLong_AsUnsignedLong(arg);

            if (value >= CET_COUNT)
            {
                PyErr_SetString(PyExc_TypeError, "invalid value to convert to CommentEmbeddingType");
                result = 0;
            }

            else
                *((CommentEmbeddingType *)dst) = value;

            break;

        default:
            assert(false);
            break;

    }

    return result;

}
