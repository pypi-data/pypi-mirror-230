
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format.c - équivalent Python du fichier "plugins/dex/format.c"
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "format.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/binary.h>
#include <plugins/pychrysalide/analysis/content.h>
#include <plugins/pychrysalide/format/executable.h>


#include "constants.h"
#include "translate.h"
#include "../class.h"
#include "../dex-int.h"
#include "../format.h"



/* Crée un nouvel objet Python de type 'DexFormat'. */
static PyObject *py_dex_format_new(PyTypeObject *, PyObject *, PyObject *);

/* Fournit la table des ressources associée au format Dex. */
static PyObject *py_dex_format_get_pool(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'DexFormat'.             *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_format_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinContent *content;                   /* Instance GLib du contenu    */
    int ret;                                /* Bilan de lecture des args.  */
    GExeFormat *format;                     /* Création GLib à transmettre */

#define DEX_FORMAT_DOC                                                  \
    "DexFormat deals with DEX format.\n"                                \
    "\n"                                                                \
    "Instances can be created using the following constructor:\n"       \
    "\n"                                                                \
    "    DexFormat(content)"                                            \
    "\n"                                                                \
    "Where content is a pychrysalide.analysis.BinContent object."       \

    ret = PyArg_ParseTuple(args, "O&", convert_to_binary_content, &content);
    if (!ret) return NULL;

    format = g_dex_format_new(content);

    if (format == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        result = pygobject_new(G_OBJECT(format));
        g_object_unref(format);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet représentant un format de fichier Dex.          *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Procède à la lecture d'une liste de types DEX.               *
*                                                                             *
*  Retour      : Instance mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_format_read_type_list(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned int offset;                    /* Position de l'élément visé  */
    int ret;                                /* Bilan de lecture des args.  */
    GDexFormat *format;                     /* Format de fichier Dex       */
    vmpa2t addr;                            /* Tête de lecture générique   */
    type_list list;                         /* Elément à transmettre       */
    bool status;                            /* Bilan de l'opération        */
    uint32_t i;                             /* Boucle de parcours          */

#define DEX_POOL_READ_TYPE_LIST_METHOD PYTHON_METHOD_DEF                                    \
(                                                                                           \
    read_type_list, "$self, offset, /",                                                     \
    METH_VARARGS, py_dex_format,                                                            \
    "Provide the raw data of a given type list as an array of pychrysalide.StructObject"    \
    " instances."                                                                           \
    "\n"                                                                                    \
    "All the items are fields extracted from the Dex *type_list* structure:\n"              \
    "* type_idx: index into the *type_ids* list.\n"                                         \
    "\n"                                                                                    \
    "In case of error, the function returns None."                                          \
)

    ret = PyArg_ParseTuple(args, "I", &offset);
    if (!ret) return NULL;

    format = G_DEX_FORMAT(pygobject_get(self));

    init_vmpa(&addr, offset, VMPA_NO_VIRTUAL);

    status = read_dex_type_list(format, &addr, &list);

    if (status)
    {
        result = PyTuple_New(list.size);

        for (i = 0; i < list.size; i++)
        {
#ifndef NDEBUG
            ret = PyTuple_SetItem(result, i, translate_dex_type_item_to_python(&list.list[i]));
            assert(ret == 0);
#else
            PyTuple_SetItem(result, i, translate_dex_type_item_to_python(&list.list[i]));
#endif
        }

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
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la table des ressources associée au format Dex.      *
*                                                                             *
*  Retour      : Table de ressources mise en place ou None si aucune.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_format_get_pool(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexFormat *format;                     /* Version native              */
    GDexPool *pool;                         /* Table de ressources associée*/

#define DEX_FORMAT_POOL_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                       \
    pool, py_dex_format,                                \
    "Resource pool of the Dex format."                  \
)

    format = G_DEX_FORMAT(pygobject_get(self));

    pool = g_dex_format_get_pool(format);

    result = pygobject_new(G_OBJECT(pool));

    g_object_unref(G_OBJECT(pool));

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

PyTypeObject *get_python_dex_format_type(void)
{
    static PyMethodDef py_dex_format_methods[] = {
        DEX_POOL_READ_TYPE_LIST_METHOD,
        { NULL }
    };

    static PyGetSetDef py_dex_format_getseters[] = {
        DEX_FORMAT_POOL_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_dex_format_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.dex.DexFormat",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = DEX_FORMAT_DOC,

        .tp_methods     = py_dex_format_methods,
        .tp_getset      = py_dex_format_getseters,
        .tp_new         = py_dex_format_new

    };

    return &py_dex_format_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.dex.DexFormat'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_dex_format(PyObject *module)
{
    PyTypeObject *type;                     /* Type Python 'DexFormat'     */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_dex_format_type();

    dict = PyModule_GetDict(module);

    if (!ensure_python_executable_format_is_registered())
        return false;

    if (!register_class_for_pygobject(dict, G_TYPE_DEX_FORMAT, type))
        return false;

    if (!define_python_dex_format_common_constants(type))
        return false;

    return true;

}
