
/* Chrysalide - Outil d'analyse de fichiers binaires
 * block.c - équivalent Python du fichier "analysis/disass/block.c"
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


#include "block.h"


#include <pygobject.h>


#include <analysis/disass/block.h>


#include "../block.h"
#include "../../access.h"
#include "../../helpers.h"



/* ------------------------ MISE EN PLACE DES BLOCS BASIQUES ------------------------ */


/* Fournit les instructions limites d'un bloc basique. */
static PyObject *py_basic_block_get_boundaries(PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                          MISE EN PLACE DES BLOCS BASIQUES                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les instructions limites d'un bloc basique.          *
*                                                                             *
*  Retour      : Première et dernière instructions du bloc.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_basic_block_get_boundaries(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GBasicBlock *block;                     /* Bloc de code à consulter    */
    GArchInstruction *first;                /* Première instruction de bloc*/
    GArchInstruction *last;                 /* Dernière instruction de bloc*/

    block = G_BASIC_BLOCK(pygobject_get(self));

    g_basic_block_get_boundaries(block, &first, &last);

    result = PyTuple_New(2);

    PyTuple_SetItem(result, 0, pygobject_new(G_OBJECT(first)));
    PyTuple_SetItem(result, 1, pygobject_new(G_OBJECT(last)));

    g_object_unref(G_OBJECT(first));
    g_object_unref(G_OBJECT(last));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit un accès à une définition de type à diffuser.        *
*                                                                             *
*  Retour      : Définition d'objet pour Python.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyTypeObject *get_python_basic_block_type(void)
{
    static PyMethodDef py_basic_block_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_basic_block_getseters[] = {
        {
            "boundaries", py_basic_block_get_boundaries, NULL,
            "First and last instructions of the basic block.", NULL
        },
        { NULL }
    };

    static PyTypeObject py_basic_block_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.disass.BasicBlock",

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "PyChrysalide basic block",

        .tp_methods     = py_basic_block_methods,
        .tp_getset      = py_basic_block_getseters,

    };

    return &py_basic_block_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....BasicBlock'.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_basic_block_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'InstrBlock'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_basic_block_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.disass");

        dict = PyModule_GetDict(module);

        if (!ensure_python_code_block_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_BASIC_BLOCK, type))
            return false;

    }

    return true;

}
