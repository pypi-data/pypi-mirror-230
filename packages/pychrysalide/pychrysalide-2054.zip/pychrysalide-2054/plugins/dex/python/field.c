
/* Chrysalide - Outil d'analyse de fichiers binaires
 * field.c - équivalent Python du fichier "plugins/dex/field.c"
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


#include "field.h"


#include <pygobject.h>


#include <plugins/pychrysalide/helpers.h>


#include "translate.h"
#include "../field.h"



#define DEX_FIELD_DOC                                               \
    "The DexField object handles a field linked to a DEX class."


/* Fournit les indications Dex concernant le champ de classe. */
static PyObject *py_dex_field_get_encoded(PyObject *, void *);

/* Fournit la variable Chrysalide correspondant au champ. */
static PyObject *py_dex_field_get_variable(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les indications Dex concernant le champ de classe.   *
*                                                                             *
*  Retour      : Données brutes du binaire.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_field_get_encoded(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexField *field;                       /* Version native              */
    const encoded_field *info;              /* Elément à traiter           */

#define DEX_FIELD_ENCODED_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                       \
    encoded, py_dex_field,                              \
    "Encoded information about the Dex field."          \
)

    field = G_DEX_FIELD(pygobject_get(self));

    info = g_dex_field_get_dex_info(field);

    result = translate_dex_field_info_to_python(info);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la variable Chrysalide correspondant au champ.       *
*                                                                             *
*  Retour      : Instance de routine mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_field_get_variable(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexField *field;                       /* Version native              */
    GBinVariable *variable;                 /* Variable correspondante     */

#define DEX_FIELD_VARIABLE_ATTRIB PYTHON_GET_DEF_FULL   \
(                                                       \
    variable, py_dex_field,                             \
    "Chrysalide variable for the Dex field."            \
)

    field = G_DEX_FIELD(pygobject_get(self));

    variable = g_dex_field_get_variable(field);

    result = pygobject_new(G_OBJECT(variable));

    g_object_unref(G_OBJECT(variable));

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

PyTypeObject *get_python_dex_field_type(void)
{
    static PyMethodDef py_dex_field_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_dex_field_getseters[] = {
        DEX_FIELD_ENCODED_ATTRIB,
        DEX_FIELD_VARIABLE_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_dex_field_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.dex.DexField",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = DEX_FIELD_DOC,

        .tp_methods     = py_dex_field_methods,
        .tp_getset      = py_dex_field_getseters

    };

    return &py_dex_field_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.dex.DexField'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_dex_field(PyObject *module)
{
    PyTypeObject *type;                     /* Type Python 'DexField'     */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_dex_field_type();

    dict = PyModule_GetDict(module);

    if (!register_class_for_pygobject(dict, G_TYPE_DEX_FIELD, type))
        return false;

    return true;

}
