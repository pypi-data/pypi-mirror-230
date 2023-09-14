
/* Chrysalide - Outil d'analyse de fichiers binaires
 * method.c - équivalent Python du fichier "plugins/dex/method.c"
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


#include "method.h"


#include <pygobject.h>


#include <plugins/pychrysalide/helpers.h>


#include "translate.h"
#include "../method.h"



#define DEX_METHOD_DOC                                                  \
    "The DexMethod handles a method defined in a DEX format."           \



/* Fournit les identifiants Dex concernant la méthode. */
static PyObject *py_dex_method_get_id_item(PyObject *, void *);

/* Fournit les indications Dex concernant la méthode. */
static PyObject *py_dex_method_get_encoded(PyObject *, void *);

/* Fournit les indications Dex relatives au corps de la méthode. */
static PyObject *py_dex_method_get_code_item(PyObject *, void *);

/* Fournit la routine Chrysalide correspondant à la méthode. */
static PyObject *py_dex_method_get_routine(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les identifiants Dex concernant la méthode.          *
*                                                                             *
*  Retour      : Données brutes issues du binaire chargé.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_method_get_id_item(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexMethod *method;                     /* Version native              */
    const method_id_item *id_item;          /* Elément à traiter           */

#define DEX_METHOD_ID_ITEM_ATTRIB PYTHON_GET_DEF_FULL                                   \
(                                                                                       \
    id_item, py_dex_method,                                                             \
    "pychrysalide.StructObject instance of identifiers used by the method.\n"           \
    "\n"                                                                                \
    "All the fields are extracted from the Dex *method_id_item* structure:\n"           \
    "* class_idx: index into the *type_ids* list for the definer of the method ;\n"     \
    "* proto_idx: index into the *proto_ids* list for the prototype of the method ;\n"  \
    "* name_idx: index into the *string_ids* list for the name of the method."          \
)

    method = G_DEX_METHOD(pygobject_get(self));

    id_item = g_dex_method_get_dex_id_item(method);

    result = translate_dex_method_id_to_python(id_item);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les indications Dex concernant la méthode.           *
*                                                                             *
*  Retour      : Données brutes issues du binaire chargé.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_method_get_encoded(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexMethod *method;                     /* Version native              */
    const encoded_method *info;             /* Elément à traiter           */

#define DEX_METHOD_ENCODED_ATTRIB PYTHON_GET_DEF_FULL                                           \
(                                                                                               \
    encoded, py_dex_method,                                                                     \
    "pychrysalide.StructObject instance for encoded information about the Dex method.\n"        \
    "\n"                                                                                        \
    "All the fields are extracted from the Dex *encoded_method* structure:\n"                   \
    "* method_idx_diff: index into the *method_ids* list for the identity of the method ;\n"    \
    "* access_flags: access flags for the method ;\n"                                           \
    "* code_off: offset from the start of the file to the code structure for the method."       \
)

    method = G_DEX_METHOD(pygobject_get(self));

    info = g_dex_method_get_dex_info(method);

    result = translate_dex_method_info_to_python(info);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les indications Dex relatives au corps de la méthode.*
*                                                                             *
*  Retour      : Données brutes du binaire, ou None si aucunes.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_method_get_code_item(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexMethod *method;                     /* Version native              */
    const code_item *body;                  /* Elément à traiter           */

#define DEX_METHOD_CODE_ITEM_ATTRIB PYTHON_GET_DEF_FULL                                         \
(                                                                                               \
    code_item, py_dex_method,                                                                   \
    "pychrysalide.StructObject instance of code information about the Dex method,"              \
    " or None if none.\n"                                                                       \
    "\n"                                                                                        \
    "All the fields are extracted from the Dex *code_item* structure:\n"                        \
    "* registers_size: the number of registers used by the code ;\n"                            \
    "* ins_size: number of words of incoming arguments to the method that the code is for ;\n"  \
    "* outs_size: number of words of outgoing argument space required for invocation ;\n"       \
    "* tries_size: number of *try_items* for the instance ;\n"                                  \
    "* debug_info_off: offset from the start of the file to the debug info sequence"            \
    " for this code, or 0 no such information ;\n"                                              \
    "* insns_size: size of the instructions list, in 16-bit code units."                        \
)

    method = G_DEX_METHOD(pygobject_get(self));

    body = g_dex_method_get_dex_body(method);

    if (body == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
        result = translate_dex_method_body_to_python(body);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la routine Chrysalide correspondant à la méthode.    *
*                                                                             *
*  Retour      : Instance de routine mise en place.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_method_get_routine(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexMethod *method;                     /* Version native              */
    GBinRoutine *routine;                   /* Routine correspondante      */

#define DEX_METHOD_ROUTINE_ATTRIB PYTHON_GET_DEF_FULL                       \
(                                                                           \
    routine, py_dex_method,                                                 \
    "DEX method as seen from Chrysalide.\n"                                 \
    "\n"                                                                    \
    "The result is a pychrysalide.analysis.BinRoutine instance or None."    \
)

    method = G_DEX_METHOD(pygobject_get(self));

    routine = g_dex_method_get_routine(method);

    result = pygobject_new(G_OBJECT(routine));

    g_object_unref(G_OBJECT(routine));

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

PyTypeObject *get_python_dex_method_type(void)
{
    static PyMethodDef py_dex_method_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_dex_method_getseters[] = {
        DEX_METHOD_ID_ITEM_ATTRIB,
        DEX_METHOD_ENCODED_ATTRIB,
        DEX_METHOD_CODE_ITEM_ATTRIB,
        DEX_METHOD_ROUTINE_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_dex_method_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.dex.DexMethod",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = DEX_METHOD_DOC,

        .tp_methods     = py_dex_method_methods,
        .tp_getset      = py_dex_method_getseters

    };

    return &py_dex_method_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.dex.DexMethod'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_dex_method(PyObject *module)
{
    PyTypeObject *type;                     /* Type Python 'DexMethod'     */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_dex_method_type();

    dict = PyModule_GetDict(module);

    if (!register_class_for_pygobject(dict, G_TYPE_DEX_METHOD, type))
        return false;

    return true;

}
