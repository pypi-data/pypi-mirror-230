
/* Chrysalide - Outil d'analyse de fichiers binaires
 * edge.c - équivalent Python du fichier "glibext/gtkext/graph/edge.c"
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include "edge.h"


#include <pygobject.h>


#include <i18n.h>
#include <gtkext/graph/edge.h>
#include <plugins/dt.h>


#include "constants.h"
#include "../../access.h"
#include "../../helpers.h"



/* Fournit les deux blocs aux extrémités d'un lien. */
static PyObject *py_graph_edge_get_boundaries(PyObject *, void *);

/* Fournit la couleur de rendu d'un lien graphique. */
static PyObject *py_graph_edge_get_color(PyObject *, void *);

/* Fournit l'ensemble des points constituant un lien graphique. */
static PyObject *py_graph_edge_get_points(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les deux blocs aux extrémités d'un lien.             *
*                                                                             *
*  Retour      : Blocs d'origine et de destination du lien.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_graph_edge_get_boundaries(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GGraphEdge *edge;                       /* Version GLib du type        */
    GCodeBlock *src;                        /* Bloc d'origine              */
    GCodeBlock *dst;                        /* Bloc de destination         */
#ifndef NDEBUG
    int ret;                                /* Bilan d'une insertion       */
#endif

    edge = G_GRAPH_EDGE(pygobject_get(self));

    g_graph_edge_get_boundaries(edge, &src, &dst);

    result = PyTuple_New(2);

#ifndef NDEBUG
    ret = PyTuple_SetItem(result, 0, pygobject_new(G_OBJECT(src)));
    assert(ret == 0);
#else
    PyTuple_SetItem(result, 0, pygobject_new(G_OBJECT(src)));
#endif

#ifndef NDEBUG
    ret = PyTuple_SetItem(result, 1, pygobject_new(G_OBJECT(dst)));
    assert(ret == 0);
#else
    PyTuple_SetItem(result, 1, pygobject_new(G_OBJECT(dst)));
#endif

    g_object_unref(G_OBJECT(src));
    g_object_unref(G_OBJECT(dst));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la couleur de rendu d'un lien graphique.             *
*                                                                             *
*  Retour      : Identifiant de couleur de rendu.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_graph_edge_get_color(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GGraphEdge *edge;                       /* Version GLib du type        */
    EdgeColor color;                        /* Couleur de rendu courante   */

    edge = G_GRAPH_EDGE(pygobject_get(self));

    color = g_graph_edge_get_color(edge);

    result = PyLong_FromUnsignedLong(color);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'ensemble des points constituant un lien graphique. *
*                                                                             *
*  Retour      : Liste de points utilisés pour le dessin d'un lien.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_graph_edge_get_points(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GGraphEdge *edge;                       /* Version GLib du type        */
    size_t count;                           /* Quantité à considérer       */
    const GdkPoint *points;                 /* Ensemble de points du lien  */
    size_t i;                               /* Boucle de parcours          */
    PyObject *obj;                          /* Objet Python à insérer      */
#ifndef NDEBUG
    int ret;                                /* Bilan d'une insertion       */
#endif

    edge = G_GRAPH_EDGE(pygobject_get(self));

    points = g_graph_edge_get_points(edge, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        obj = Py_BuildValue("(ii)", points[i].x, points[i].y);

#ifndef NDEBUG
        ret = PyTuple_SetItem(result, i, obj);
        assert(ret == 0);
#else
        PyTuple_SetItem(result, i, obj);
#endif

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

PyTypeObject *get_python_graph_edge_type(void)
{
    static PyMethodDef py_graph_edge_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_graph_edge_getseters[] = {
        {
            "boundaries", py_graph_edge_get_boundaries, NULL,
            "Origin and destination blocks for the graphical edge.", NULL
        },
        {
            "color", py_graph_edge_get_color, NULL,
            "Rendering color of the graphical edge.", NULL
        },
        {
            "points", py_graph_edge_get_points, NULL,
            "Points of the lines rendered for the graphical edge.", NULL
        },
        { NULL }
    };

    static PyTypeObject py_graph_edge_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.gtkext.graph.GraphEdge",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "Graphical edge used in the graph view.\n" \
                          "\n" \
                          "The aim of this object is to provide a read-only " \
                          "access to the information relative to graphical " \
                          "edge contained in a layout.",

        .tp_methods     = py_graph_edge_methods,
        .tp_getset      = py_graph_edge_getseters,

        .tp_new         = no_python_constructor_allowed,

    };

    return &py_graph_edge_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.gtkext.....GraphEdge'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_graph_edge_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BinPortion'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_graph_edge_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.gtkext.graph");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_GRAPH_EDGE, type))
            return false;

        if (!define_graph_edge_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en lien graphique entre noeuds.           *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_graph_edge(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_graph_edge_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to graph edge");
            break;

        case 1:
            *((GGraphEdge **)dst) = G_GRAPH_EDGE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
