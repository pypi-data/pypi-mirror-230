
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bufferline.c - équivalent Python du fichier "glibext/bufferline.h"
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


#include "bufferline.h"


#include <assert.h>
#include <malloc.h>
#include <pygobject.h>


#include <i18n.h>
#include <glibext/bufferline.h>
#include <plugins/dt.h>


#include "constants.h"
#include "../access.h"
#include "../helpers.h"
#include "../arch/vmpa.h"



/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_buffer_line_new(PyTypeObject *, PyObject *, PyObject *);

/* Ajoute du texte à formater dans une ligne donnée. */
static PyObject *py_buffer_line_append_text(PyObject *, PyObject *);

/* Reconstruit et fournit le texte présent sur une ligne tampon. */
static PyObject *py_buffer_line_get_text(PyObject *, PyObject *);

/* Renseigne sur les propriétés particulières liées à une ligne. */
static PyObject *py_buffer_line_get_flags(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type du nouvel objet à mettre en place.               *
*                args = éventuelle liste d'arguments.                         *
*                kwds = éventuel dictionnaire de valeurs mises à disposition. *
*                                                                             *
*  Description : Accompagne la création d'une instance dérivée en Python.     *
*                                                                             *
*  Retour      : Nouvel objet Python mis en place ou NULL en cas d'échec.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_line_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

#define BUFFER_LINE_DOC                                                     \
    "The BufferLine object is used to display processed data: disassembled" \
    " instruction, binary content in hexadecimal form, aso.\n"              \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    BufferLine()"                                                      \
    "\n"                                                                    \
    "Such objets aim to be created from the Chrysalide core only, and"      \
    " then get populated on demand. Thus, these lines can be viewed as"     \
    " cached lines and their properties have to be set through the"         \
    " pychrysalide.glibext.BufferCache instance which contains them."

    /* Validations diverses */

    base = get_python_buffer_line_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_BUFFER_LINE, type->tp_name, NULL, NULL, NULL);

    if (first_time)
    {
        status = register_class_for_dynamic_pygobject(gtype, type);

        if (!status)
        {
            result = NULL;
            goto exit;
        }

    }

    /* On crée, et on laisse ensuite la main à PyGObject_Type.tp_init() */

 simple_way:

    result = PyType_GenericNew(type, args, kwds);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant une ligne de tampon.              *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Ajoute du texte à formater dans une ligne donnée.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_line_append_text(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    size_t column;                          /* Indice de colonne           */
    const char *text;                       /* Texte à ajouter             */
    RenderingTagType type;                  /* Type de rendu attendu       */
    GObject *creator;                       /* Eventuel créateur à associer*/
    int ret;                                /* Bilan de lecture des args.  */
    GBufferLine *line;                      /* Version native              */

#define BUFFER_LINE_APPEND_TEXT_METHOD PYTHON_METHOD_DEF            \
(                                                                   \
    append_text, "$self, column, text, tag, /, creator=None",       \
    METH_VARARGS, py_buffer_line,                                   \
    "Append some text to a line at a given column index. The"       \
    " expected rendering for this text is defined by the tag, which"\
    " must be a pychrysalide.glibext.BufferLine.RenderingTagType"   \
    " value."                                                       \
    "\n"                                                            \
    "An optional GObject instance may be provided as origin of the" \
    " creation."                                                    \
)

    creator = NULL;

    ret = PyArg_ParseTuple(args, "nsO&|O&", &column, &text,
                           convert_to_rendering_tag_type, &type, convert_to_gobject, &creator);
    if (!ret) return NULL;

    line = G_BUFFER_LINE(pygobject_get(self));

    g_buffer_line_append_text(line, column, text, strlen(text), type, creator);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant une ligne de tampon.              *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Reconstruit et fournit le texte présent sur une ligne tampon.*
*                                                                             *
*  Retour      : Texte reconstruit pour l'occasion.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_line_get_text(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    size_t first;                           /* Première colonne à parcourir*/
    size_t end;                             /* Dernière colonne à parcourir*/
    int markup;                             /* Besoin de décorations ?     */
    int ret;                                /* Bilan de lecture des args.  */
    GBufferLine *line;                      /* Version native              */
    char *text;                             /* Texte reconstruit à libérer */

    ret = PyArg_ParseTuple(args, "IIp", &first, &end, &markup);
    if (!ret) return NULL;

    line = G_BUFFER_LINE(pygobject_get(self));
    text = g_buffer_line_get_text(line, first, end, markup);

    if (text != NULL)
    {
        result = PyUnicode_FromString(text);
        free(text);
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
*  Description : Renseigne sur les propriétés particulières liées à une ligne.*
*                                                                             *
*  Retour      : Propriétés intégrées.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_line_get_flags(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBufferLine *line;                      /* Elément à consulter         */
    BufferLineFlags flags;                  /* Drapeaux à exporter         */

    line = G_BUFFER_LINE(pygobject_get(self));
    flags = g_buffer_line_get_flags(line);

    result = PyLong_FromLong(flags);

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

PyTypeObject *get_python_buffer_line_type(void)
{
    static PyMethodDef py_buffer_line_methods[] = {
        BUFFER_LINE_APPEND_TEXT_METHOD,
        {
            "get_text", py_buffer_line_get_text,
            METH_VARARGS,
            "get_text($self, first_col, last_col, markup, /)\n--\n\nProvide the text of a buffer line."
        },
        { NULL }
    };

    static PyGetSetDef py_buffer_line_getseters[] = {
        {
            "flags", py_buffer_line_get_flags, NULL,
            "Current flags of the buffer line.", NULL
        },
        { NULL }
    };

    static PyTypeObject py_buffer_line_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.BufferLine",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = BUFFER_LINE_DOC,

        .tp_methods     = py_buffer_line_methods,
        .tp_getset      = py_buffer_line_getseters,

        .tp_new         = py_buffer_line_new

    };

    return &py_buffer_line_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.glibext.BufferLine'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_buffer_line_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BufferLine'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_buffer_line_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_BUFFER_LINE, type))
            return false;

        if (!define_line_segment_constants(type))
            return false;

        if (!define_buffer_line_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en ligne de tampon.                       *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_buffer_line(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_buffer_line_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to buffer line");
            break;

        case 1:
            *((GBufferLine **)dst) = G_BUFFER_LINE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
