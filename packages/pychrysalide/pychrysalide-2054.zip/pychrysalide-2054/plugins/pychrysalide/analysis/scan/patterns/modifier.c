
/* Chrysalide - Outil d'analyse de fichiers binaires
 * modifier.c - équivalent Python du fichier "analysis/scan/modifier.c"
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#include "modifier.h"


#include <pygobject.h>


#include <analysis/scan/patterns/modifier-int.h>


#include "../../../access.h"
#include "../../../helpers.h"



CREATE_DYN_ABSTRACT_CONSTRUCTOR(scan_token_modifier, G_TYPE_SCAN_TOKEN_MODIFIER, NULL);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_scan_token_modifier_init(PyObject *, PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet à initialiser (théoriquement).                  *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Initialise une instance sur la base du dérivé de GObject.    *
*                                                                             *
*  Retour      : 0.                                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_scan_token_modifier_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan de lecture des args.  */

#define SCAN_TOKEN_MODIFIER_DOC                                     \
    "An *TokenModifier* object is the root class of all modifiers"  \
    " for byte patterns."

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = tampon de données à consulter.                        *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Transforme une séquence d'octets pour motif de recherche.    *
*                                                                             *
*  Retour      : Liste des nouvelle(s) séquence(s) d'octets obtenue(s).       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_token_modifier_transform(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à faire remonter      */
    const char *data;                       /* Séquence d'octets à traiter */
    Py_ssize_t len;                         /* Quantité de ces données     */
    int ret;                                /* Bilan de lecture des args.  */
    sized_binary_t src;                     /* Entrée au format adapté     */
    GScanTokenModifier *modifier;           /* Version native de l'instance*/
    sized_binary_t *dest;                   /* Liste des nouvelles chaînes */
    size_t count;                           /* Taille de cette liste       */
    bool status;                            /* Bilan de l'opération        */
    size_t i;                               /* Boucle de parcours          */

#define SCAN_TOKEN_MODIFIER_TRANSFORM_METHOD PYTHON_METHOD_DEF      \
(                                                                   \
    transform, "$self, data",                                       \
    METH_VARARGS, py_scan_token_modifier,                           \
    "Transform data from a byte pattern for an incoming scan.\n"    \
    "\n"                                                            \
    "The data has to be provided as bytes.\n"                       \
    "\n"                                                            \
    "The method returns a tuple of transformed data as bytes, or"   \
    " *None* in case of error."                                     \
)

    ret = PyArg_ParseTuple(args, "s#", &data, &len);
    if (!ret) return NULL;

    src.data = (char *)data;
    src.len = len;

    modifier = G_SCAN_TOKEN_MODIFIER(pygobject_get(self));

    status = g_scan_token_modifier_transform(modifier, &src, &dest, &count);

    if (status)
    {
        result = PyTuple_New(count);

        for (i = 0; i < count; i++)
        {
            PyTuple_SetItem(result, i, PyBytes_FromStringAndSize(dest[i].data, dest[i].len));
            exit_szstr(&dest[i]);
        }

        free(dest);

    }

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un composant nommé à manipuler.*
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le désignation associée à un composant nommé.        *
*                                                                             *
*  Retour      : Description courante.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_scan_token_modifier_get_name(PyObject *self, void *closure)
{
    PyObject *result;                       /* Décompte à retourner        */
    GScanTokenModifier *modifier;           /* Version native              */
    char *name;                             /* Désignation à convertir     */

#define SCAN_TOKEN_MODIFIER_NAME_ATTRIB PYTHON_GET_DEF_FULL \
(                                                           \
    name, py_scan_token_modifier,                           \
    "Call name for the modifier.\n"                         \
    "\n"                                                    \
    "The result is a string."                               \
)

    modifier = G_SCAN_TOKEN_MODIFIER(pygobject_get(self));

    name = g_scan_token_modifier_get_name(modifier);

    if (name == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }
    else
    {
        result = PyUnicode_FromString(name);
        free(name);
    }

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

PyTypeObject *get_python_scan_token_modifier_type(void)
{
    static PyMethodDef py_scan_token_modifier_methods[] = {
        SCAN_TOKEN_MODIFIER_TRANSFORM_METHOD,
        { NULL }
    };

    static PyGetSetDef py_scan_token_modifier_getseters[] = {
        SCAN_TOKEN_MODIFIER_NAME_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_scan_token_modifier_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.scan.patterns.TokenModifier",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = SCAN_TOKEN_MODIFIER_DOC,

        .tp_methods     = py_scan_token_modifier_methods,
        .tp_getset      = py_scan_token_modifier_getseters,

        .tp_init        = py_scan_token_modifier_init,
        .tp_new         = py_scan_token_modifier_new,

    };

    return &py_scan_token_modifier_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....TokenModifier'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_scan_token_modifier_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'TokenModifier' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_scan_token_modifier_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.scan");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_SCAN_TOKEN_MODIFIER, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en transformation de séquence d'octets.   *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_scan_token_modifier(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_scan_token_modifier_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to token modifier");
            break;

        case 1:
            *((GScanTokenModifier **)dst) = G_SCAN_TOKEN_MODIFIER(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
