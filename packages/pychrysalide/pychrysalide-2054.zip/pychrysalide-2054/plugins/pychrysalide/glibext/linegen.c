
/* Chrysalide - Outil d'analyse de fichiers binaires
 * linegen.c - équivalent Python du fichier "glibext/linegen.h"
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


#include "linegen.h"


#include <pygobject.h>


#include <glibext/linegen-int.h>


#include "bufferline.h"
#include "constants.h"
#include "linecursor.h"
#include "../access.h"
#include "../helpers.h"
#include "../analysis/content.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Procède à l'initialisation de l'interface de génération. */
static void py_line_generator_interface_init(GLineGeneratorIface *, gpointer *);

/* Indique le nombre de ligne prêtes à être générées. */
static size_t py_line_generator_count_lines_wrapper(const GLineGenerator *);

/* Retrouve l'emplacement correspondant à une position donnée. */
static void py_line_generator_compute_cursor_wrapper(const GLineGenerator *, gint, size_t, size_t, GLineCursor **);

/* Détermine si le conteneur s'inscrit dans une plage donnée. */
static int py_line_generator_contain_cursor_wrapper(const GLineGenerator *, size_t, size_t, const GLineCursor *);

/* Renseigne sur les propriétés liées à un générateur. */
static BufferLineFlags py_line_generator_get_flags_wrapper(const GLineGenerator *, size_t, size_t);

/* Imprime dans une ligne de rendu le contenu représenté. */
static void py_line_generator_print_wrapper(GLineGenerator *, GBufferLine *, size_t, size_t, const GBinContent *);



/* ------------------------- CONNEXION AVEC L'API DE PYTHON ------------------------- */


/* Retrouve l'emplacement correspondant à une position donnée. */
static PyObject *py_line_generator_compute_cursor(PyObject *, PyObject *);

/* Détermine si le conteneur s'inscrit dans une plage donnée. */
static PyObject *py_line_generator_contain_cursor(PyObject *, PyObject *);

/* Renseigne sur les propriétés liées à un générateur. */
static PyObject *py_line_generator_get_flags(PyObject *, PyObject *);

/* Imprime dans une ligne de rendu le contenu représenté. */
static PyObject *py_line_generator_print(PyObject *, PyObject *);

/* Indique le nombre de ligne prêtes à être générées. */
static PyObject *py_line_generator_get_lines_count(PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : iface  = interface GLib à initialiser.                       *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de génération.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_line_generator_interface_init(GLineGeneratorIface *iface, gpointer *unused)
{

#define LINE_GENERATOR_DOC                                                  \
    "LineGenerator gives an interface to all objects which aim to produce"  \
    " content for rendering lines. Such lines can be exported to graphical" \
    " interfaces or text files.\n"                                          \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, LineGenerator):\n"                 \
    "        ...\n"                                                         \
    "\n"                                                                    \
    "The following methods have to be defined for new implementations:\n"   \
    "* pychrysalide.glibext.LineGenerator._count_lines();\n"                \
    "* pychrysalide.glibext.LineGenerator._compute_cursor();\n"             \
    "* pychrysalide.glibext.LineGenerator._contain_cursor();\n"             \
    "* pychrysalide.glibext.LineGenerator._get_flags();\n"                  \
    "* pychrysalide.glibext.LineGenerator._print();\n"                      \

    iface->count = py_line_generator_count_lines_wrapper;
    iface->compute = py_line_generator_compute_cursor_wrapper;
    iface->contain = py_line_generator_contain_cursor_wrapper;
    iface->get_flags = py_line_generator_get_flags_wrapper;
    iface->print = py_line_generator_print_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à consulter.                          *
*                                                                             *
*  Description : Indique le nombre de ligne prêtes à être générées.           *
*                                                                             *
*  Retour      : Nombre de lignes devant apparaître au final.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t py_line_generator_count_lines_wrapper(const GLineGenerator *generator)
{
    size_t result;                          /* Décompte à retourner        */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Bilan d'une conversion      */

#define LINE_GENERATOR_COUNT_LINES_WRAPPER PYTHON_WRAPPER_DEF       \
(                                                                   \
    _count_lines, "$self, /",                                       \
    METH_NOARGS,                                                    \
    "Abstract method used to count the number of lines produced"    \
    " by the current generator."                                    \
)

    result = 0;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(generator));

    if (has_python_method(pyobj, "_count_lines"))
    {
        pyret = run_python_method(pyobj, "_count_lines", NULL);

        if (pyret != NULL)
        {
            ret = PyLong_Check(pyret);

            if (ret)
                result = PyLong_AsSize_t(pyret);

            Py_DECREF(pyret);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à consulter.                          *
*                x         = position géographique sur la ligne concernée.    *
*                index     = indice de cette même ligne dans le tampon global.*
*                repeat    = indice d'utilisations successives du générateur. *
*                                                                             *
*  Description : Retrouve l'emplacement correspondant à une position donnée.  *
*                                                                             *
*  Retour      : Emplacement constitué.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_line_generator_compute_cursor_wrapper(const GLineGenerator *generator, gint x, size_t index, size_t repeat, GLineCursor **cursor)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Bilan d'une conversion      */

#define LINE_GENERATOR_COMPUTE_CURSOR_WRAPPER PYTHON_WRAPPER_DEF    \
(                                                                   \
    _compute_cursor, "$self, x, index, repeat, /",                  \
    METH_VARARGS,                                                   \
    "Abstract method used to create a new cursor for a given"       \
    " location inside displayed lines.\n"                           \
    "\n"                                                            \
    "The position on the horizontal axis, the line index and the"   \
    " number of repetitions (only relevant if the generator"        \
    " produces several lines) give indications about the active"    \
    " position.\n"                                                  \
    "\n"                                                            \
    "The result has to be a pychrysalide.glibext.LineCursor"        \
    " instance."                                                    \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(generator));

    if (has_python_method(pyobj, "_compute_cursor"))
    {
        args = PyTuple_New(3);
        PyTuple_SetItem(args, 0, PyLong_FromSize_t(x));
        PyTuple_SetItem(args, 1, PyLong_FromSize_t(index));
        PyTuple_SetItem(args, 2, PyLong_FromSize_t(repeat));

        pyret = run_python_method(pyobj, "_compute_cursor", args);

        if (pyret != NULL)
        {
            ret = convert_to_line_cursor(pyret, cursor);

            if (ret != 1)
                *cursor = NULL;

            Py_DECREF(pyret);

        }

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à consulter.                          *
*                index     = indice de cette même ligne dans le tampon global.*
*                repeat    = indice d'utilisations successives du générateur. *
*                cursor    = emplacement à analyser.                          *
*                                                                             *
*  Description : Détermine si le conteneur s'inscrit dans une plage donnée.   *
*                                                                             *
*  Retour      : Bilan de la détermination, utilisable en comparaisons.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_line_generator_contain_cursor_wrapper(const GLineGenerator *generator, size_t index, size_t repeat, const GLineCursor *cursor)
{
    int result;                             /* Bilan d'analyse à retourner */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Bilan d'une conversion      */

#define LINE_GENERATOR_CONTAIN_CURSOR_WRAPPER PYTHON_WRAPPER_DEF    \
(                                                                   \
    _contain_cursor, "$self, index, repeat, cursor, /",             \
    METH_VARARGS,                                                   \
    "Abstract method used to check the position of a cursor in"     \
    " relation to rendering lines.\n"                               \
    "\n"                                                            \
    "The line index and the number of repetitions (only relevant"   \
    " if the generator produces several lines) give indications"    \
    " about the active position. The cursor is a"                   \
    " pychrysalide.glibext.LineCursor instance.\n"                  \
    "\n"                                                            \
    "The result has to be an integer less than, equal to, or"       \
    " greater than zero if the cursor is, respectively, before,"    \
    " inside or after the area covered by the generator."           \
)

    result = 0;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(generator));

    if (has_python_method(pyobj, "_contain_cursor"))
    {
        args = PyTuple_New(3);
        PyTuple_SetItem(args, 0, PyLong_FromSize_t(index));
        PyTuple_SetItem(args, 1, PyLong_FromSize_t(repeat));
        PyTuple_SetItem(args, 2, pygobject_new(G_OBJECT(cursor)));

        pyret = run_python_method(pyobj, "_contain_cursor", args);

        if (pyret != NULL)
        {
            ret = PyLong_Check(pyret);

            if (ret)
                result = PyLong_AsLong(pyret);

            Py_DECREF(pyret);

        }

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à consulter.                          *
*                index     = indice de cette même ligne dans le tampon global.*
*                repeat    = indice d'utilisations successives du générateur. *
*                                                                             *
*  Description : Renseigne sur les propriétés liées à un générateur.          *
*                                                                             *
*  Retour      : Propriétés particulières associées.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static BufferLineFlags py_line_generator_get_flags_wrapper(const GLineGenerator *generator, size_t index, size_t repeat)
{
    BufferLineFlags result;                 /* Fanions à retourner         */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Bilan d'une conversion      */

#define LINE_GENERATOR_GET_FLAGS_WRAPPER PYTHON_WRAPPER_DEF         \
(                                                                   \
    _get_flags, "$self, index, repeat, /",                          \
    METH_VARARGS,                                                   \
    "Abstract method used to provide flags for a given rendering"   \
    " line.\n"                                                      \
    "\n"                                                            \
    "The line index and the number of repetitions (only relevant"   \
    " if the generator produces several lines) give indications"    \
    " about the active position.\n"                                 \
    "\n"                                                            \
    "The result has to be a"                                        \
    " pychrysalide.glibext.BufferLine.BufferLineFlags value.\n"     \
)

    result = BLF_NONE;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(generator));

    if (has_python_method(pyobj, "_get_flags"))
    {
        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, PyLong_FromSize_t(index));
        PyTuple_SetItem(args, 1, PyLong_FromSize_t(repeat));

        pyret = run_python_method(pyobj, "_get_flags", args);

        if (pyret != NULL)
        {
            ret = convert_to_buffer_line_flags(pyret, &result);

            if (ret != 1)
                result = BLF_NONE;

            Py_DECREF(pyret);

        }

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à utiliser pour l'impression.         *
*                line      = ligne de rendu à compléter.                      *
*                index     = indice de cette même ligne dans le tampon global.*
*                repeat    = indice d'utilisations successives du générateur. *
*                content   = éventuel contenu binaire brut à imprimer.        *
*                                                                             *
*  Description : Imprime dans une ligne de rendu le contenu représenté.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_line_generator_print_wrapper(GLineGenerator *generator, GBufferLine *line, size_t index, size_t repeat, const GBinContent *content)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define LINE_GENERATOR_PRINT_WRAPPER PYTHON_WRAPPER_DEF             \
(                                                                   \
    _print, "$self, line, index, repeat, content, /",               \
    METH_VARARGS,                                                   \
    "Abstract method used to generate content into a rendering"     \
    " line, which is a provided pychrysalide.glibext.BufferLine"    \
    " instance.\n"                                                  \
    "\n"                                                            \
    "The line index and the number of repetitions (only relevant"   \
    " if the generator produces several lines) give indications"    \
    " about the current rendering position.\n"                      \
    "\n"                                                            \
    "If set, the content is a pychrysalide.analysis.BinContent"     \
    " instance providing access to the processed binary data."      \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(generator));

    if (has_python_method(pyobj, "_print"))
    {
        args = PyTuple_New(4);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(line)));
        PyTuple_SetItem(args, 1, PyLong_FromSize_t(index));
        PyTuple_SetItem(args, 2, PyLong_FromSize_t(repeat));
        PyTuple_SetItem(args, 3, pygobject_new(G_OBJECT(content)));

        pyret = run_python_method(pyobj, "_print", args);

        Py_XDECREF(pyret);

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}



/* ---------------------------------------------------------------------------------- */
/*                           CONNEXION AVEC L'API DE PYTHON                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un générateur à manipuler.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Retrouve l'emplacement correspondant à une position donnée.  *
*                                                                             *
*  Retour      : Emplacement constitué.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_line_generator_compute_cursor(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Propriétés à retourner      */
    int x;                                  /* Position horizontale        */
    size_t index;                           /* Indice dans le tampon       */
    size_t repeat;                          /* Utilisations successives    */
    int ret;                                /* Bilan de lecture des args.  */
    GLineGenerator *generator;              /* Version native              */
    GLineCursor *cursor;                    /* Curseur nouveau obtenu      */

#define LINE_GENERATOR_COMPUTE_CURSOR_METHOD PYTHON_METHOD_DEF      \
(                                                                   \
    compute_cursor, "$self, x, index, repeat, /",                   \
    METH_VARARGS, py_line_generator,                                \
    "Create a a new cursor for a given location inside displayed"   \
    " lines.\n"                                                     \
    "\n"                                                            \
    "The position on the horizontal axis, the line index and the"   \
    " number of repetitions (only relevant if the generator"        \
    " produces several lines) give indications about the active"    \
    " position.\n"                                                  \
    "\n"                                                            \
    "The result has to be a pychrysalide.glibext.LineCursor"        \
    " instance."                                                    \
)

    ret = PyArg_ParseTuple(args, "inn", &x, &index, &repeat);
    if (!ret) return NULL;

    generator = G_LINE_GENERATOR(pygobject_get(self));

    cursor = g_line_generator_compute_cursor(generator, x, index, repeat);

    if (cursor != NULL)
    {
        result = pygobject_new(G_OBJECT(cursor));
        g_object_unref(G_OBJECT(cursor));
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
*  Paramètres  : self = classe représentant un générateur à manipuler.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Détermine si le conteneur s'inscrit dans une plage donnée.   *
*                                                                             *
*  Retour      : Bilan de la détermination, utilisable en comparaisons.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_line_generator_contain_cursor(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Propriétés à retourner      */
    size_t index;                           /* Indice dans le tampon       */
    size_t repeat;                          /* Utilisations successives    */
    GLineCursor *cursor;                    /* Curseur à venir situer      */
    int ret;                                /* Bilan de lecture des args.  */
    GLineGenerator *generator;              /* Version native              */
    int status;                             /* Bilan d'une analyse         */

#define LINE_GENERATOR_CONTAIN_CURSOR_METHOD PYTHON_METHOD_DEF      \
(                                                                   \
    contain_cursor, "$self, index, repeat, cursor, /",              \
    METH_VARARGS, py_line_generator,                                \
    "Check the position of a cursor in relation to rendering"       \
    " lines.\n"                                                     \
    "\n"                                                            \
    "The line index and the number of repetitions (only relevant"   \
    " if the generator produces several lines) give indications"    \
    " about the active position. The cursor is a"                   \
    " pychrysalide.glibext.LineCursor instance.\n"                  \
    "\n"                                                            \
    "The result has to be an integer less than, equal to, or"       \
    " greater than zero if the cursor is, respectively, before,"    \
    " inside or after the area covered by the generator."           \
)

    ret = PyArg_ParseTuple(args, "nnO&", &index, &repeat, convert_to_line_cursor, &cursor);
    if (!ret) return NULL;

    generator = G_LINE_GENERATOR(pygobject_get(self));

    status = g_line_generator_contain_cursor(generator, index, repeat, cursor);

    result = PyLong_FromLong(status);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un générateur à manipuler.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Renseigne sur les propriétés liées à un générateur.          *
*                                                                             *
*  Retour      : Propriétés particulières associées.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_line_generator_get_flags(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Propriétés à retourner      */
    size_t index;                           /* Indice dans le tampon       */
    size_t repeat;                          /* Utilisations successives    */
    int ret;                                /* Bilan de lecture des args.  */
    GLineGenerator *generator;              /* Version native              */
    BufferLineFlags flags;                  /* Propriétés courantes        */

#define LINE_GENERATOR_GET_FLAGS_METHOD PYTHON_METHOD_DEF               \
(                                                                       \
    get_flags, "$self, index, repeat, /",                               \
    METH_VARARGS, py_line_generator,                                    \
    "Get the flags of a given position from the generator.\n"           \
    "\n"                                                                \
    "The line index and the number of repetitions (only relevant"       \
    " if the generator produces several lines) give indications"        \
    " about the active position.\n"                                     \
    "\n"                                                                \
    "The result is a pychrysalide.glibext.BufferLine.BufferLineFlags"   \
    " value."                                                           \
)

    ret = PyArg_ParseTuple(args, "nn", &index, &repeat);
    if (!ret) return NULL;

    generator = G_LINE_GENERATOR(pygobject_get(self));

    flags = g_line_generator_get_flags(generator, index, repeat);

    result = cast_with_constants_group_from_type(get_python_buffer_line_type(), "BufferLineFlags", flags);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un générateur à manipuler.        *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Imprime dans une ligne de rendu le contenu représenté.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_line_generator_print(PyObject *self, PyObject *args)
{
    GBufferLine *line;                      /* Ligne de rendu à compléter  */
    size_t index;                           /* Indice dans le tampon       */
    size_t repeat;                          /* Utilisations successives    */
    GBinContent *content;                   /* Contenu binaire associé     */
    GLineGenerator *generator;              /* Version native              */
    int ret;                                /* Bilan de lecture des args.  */

#define LINE_GENERATOR_PRINT_METHOD PYTHON_METHOD_DEF               \
(                                                                   \
    print, "$self, line, index, repeat, content, /",                \
    METH_VARARGS, py_line_generator,                                \
    "Produce output into a rendering line with optional content.\n" \
    "\n"                                                            \
    "The provided line is a pychrysalide.glibext.BufferLine"        \
    " instance. The index and the number of repetitions (only"      \
    " relevant if the generator produces several lines) give"       \
    " indications about the current rendering position.\n"          \
    "\n"                                                            \
    "If set, the content is a pychrysalide.analysis.BinContent"     \
    " instance providing access to the processed binary data."      \
)

    ret = PyArg_ParseTuple(args, "O&nnO&", convert_to_buffer_line, &line, &index,
                           &repeat, convert_to_binary_content, &content);
    if (!ret) return NULL;

    generator = G_LINE_GENERATOR(pygobject_get(self));

    g_line_generator_print(generator, line, index, repeat, content);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un générateur à manipuler.     *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le nombre de ligne prêtes à être générées.           *
*                                                                             *
*  Retour      : Nombre de lignes devant apparaître au final.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_line_generator_get_lines_count(PyObject *self, void *closure)
{
    PyObject *result;                       /* Décompte à retourner        */
    GLineGenerator *generator;              /* Version native              */
    size_t count;                           /* Nombre de lignes présentes  */

#define LINE_GENERATOR_LINES_COUNT_ATTRIB PYTHON_GET_DEF_FULL       \
(                                                                   \
    lines_count, py_line_generator,                                 \
    "Quantity of lines produced by the generator.\n"                \
    "\n"                                                            \
    "This number may vary between calls, if a width has changed"    \
    " for instance."                                                \
)

    generator = G_LINE_GENERATOR(pygobject_get(self));

    count = g_line_generator_count_lines(generator);

    result = PyLong_FromSize_t(count);

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

PyTypeObject *get_python_line_generator_type(void)
{
    static PyMethodDef py_line_generator_methods[] = {
        LINE_GENERATOR_COUNT_LINES_WRAPPER,
        LINE_GENERATOR_COMPUTE_CURSOR_WRAPPER,
        LINE_GENERATOR_CONTAIN_CURSOR_WRAPPER,
        LINE_GENERATOR_GET_FLAGS_WRAPPER,
        LINE_GENERATOR_PRINT_WRAPPER,
        LINE_GENERATOR_COMPUTE_CURSOR_METHOD,
        LINE_GENERATOR_CONTAIN_CURSOR_METHOD,
        LINE_GENERATOR_GET_FLAGS_METHOD,
        LINE_GENERATOR_PRINT_METHOD,
        { NULL }
    };

    static PyGetSetDef py_line_generator_getseters[] = {
        LINE_GENERATOR_LINES_COUNT_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_line_generator_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.LineGenerator",
        .tp_basicsize   = sizeof(PyObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = LINE_GENERATOR_DOC,

        .tp_methods     = py_line_generator_methods,
        .tp_getset      = py_line_generator_getseters,

    };

    return &py_line_generator_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.glibext.LineGenerator'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_line_generator_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'LineGenerator' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    static GInterfaceInfo info = {          /* Paramètres d'inscription    */

        .interface_init = (GInterfaceInitFunc)py_line_generator_interface_init,
        .interface_finalize = NULL,
        .interface_data = NULL,

    };

    type = get_python_line_generator_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        dict = PyModule_GetDict(module);

        if (!register_interface_for_pygobject(dict, G_TYPE_LINE_GENERATOR, type, &info))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en générateur de lignes.                  *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_line_generator(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_line_generator_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to line generator");
            break;

        case 1:
            *((GLineGenerator **)dst) = G_LINE_GENERATOR(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
