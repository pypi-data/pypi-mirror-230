
/* Chrysalide - Outil d'analyse de fichiers binaires
 * stream.h - équivalent Python du fichier "plugins/kaitai/stream.h"
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


#include "stream.h"


#include <pygobject.h>


#include <i18n.h>
#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/content.h>
#include <plugins/pychrysalide/arch/vmpa.h>


#include "../stream-int.h"



CREATE_DYN_CONSTRUCTOR(kaitai_stream, G_TYPE_KAITAI_STREAM);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_kaitai_stream_init(PyObject *, PyObject *, PyObject *);

/* Détermine si la fin des données a été atteinte. */
static PyObject *py_kaitai_stream_get_eof(PyObject *, void *);



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

static int py_kaitai_stream_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GBinContent *content;                   /* Contenu binaire manipulé    */
    vmpa2t *pos;                            /* Tête de lecture courante    */
    int ret;                                /* Bilan de lecture des args.  */
    GKaitaiStream *stream;                  /* Création GLib à transmettre */

#define KAITAI_STREAM_DOC                                                       \
    "KaitaiStream collects all the information useful for the processing of"    \
    " binary data."                                                             \
    "\n"                                                                        \
    "Instances can be created using following constructor:\n"                   \
    "\n"                                                                        \
    "    KaitaiStream(content, pos)"                                            \
    "\n"                                                                        \
    "Where *content* is a pychrysalide.analysis.BinContent instance providing"  \
    " the processed data and *pos* defines the current reading location, as a"  \
    " pychrysalide.arch.vmpa value."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&O&", convert_to_binary_content, &content, convert_any_to_vmpa, &pos);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    stream = G_KAITAI_STREAM(pygobject_get(self));

    if (!g_kaitai_stream_create(stream, content, pos))
    {
        clean_vmpa_arg(pos);

        PyErr_SetString(PyExc_ValueError, _("Unable to create Kaitai stream."));
        return -1;

    }

    clean_vmpa_arg(pos);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Détermine si la fin des données a été atteinte.              *
*                                                                             *
*  Retour      : True si la tête de lecture est en position finale, ou False. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_kaitai_stream_get_eof(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GKaitaiStream *stream;                  /* Version native dyu flux     */
    bool status;                            /* Etat de la position courante*/

#define KAITAI_STREAM_EOF_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                       \
    eof, py_kaitai_stream,                              \
    "Boolean value stating if the end of the stream"    \
    " has been reached or not."                         \
)

    stream = G_KAITAI_STREAM(pygobject_get(self));

    status = g_kaitai_stream_has_reached_eof(stream);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

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

PyTypeObject *get_python_kaitai_stream_type(void)
{
    static PyMethodDef py_kaitai_stream_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_kaitai_stream_getseters[] = {
        KAITAI_STREAM_EOF_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_kaitai_stream_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.plugins.kaitai.KaitaiStream",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = KAITAI_STREAM_DOC,

        .tp_methods     = py_kaitai_stream_methods,
        .tp_getset      = py_kaitai_stream_getseters,

        .tp_init        = py_kaitai_stream_init,
        .tp_new         = py_kaitai_stream_new,

    };

    return &py_kaitai_stream_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.plugins...KaitaiStream.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_kaitai_stream_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'KaitaiStream'  */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_kaitai_stream_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.plugins.kaitai");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_KAITAI_STREAM, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en flux de données pour Kaitai.           *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_kaitai_stream(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_kaitai_stream_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to Kaitai stream");
            break;

        case 1:
            *((GKaitaiStream **)dst) = G_KAITAI_STREAM(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
