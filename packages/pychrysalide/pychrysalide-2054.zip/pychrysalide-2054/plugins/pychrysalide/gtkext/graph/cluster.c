
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cluster.c - équivalent Python du fichier "glibext/gtkext/graph/cluster.c"
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


#include "cluster.h"


#include <malloc.h>
#include <pygobject.h>


#include <i18n.h>
#include <gtkext/graph/cluster.h>
#include <plugins/dt.h>


#include "../../access.h"
#include "../../helpers.h"
#include "../../struct.h"
#include "../../analysis/binary.h"
#include "../../analysis/block.h"



/* Recherche le groupe de blocs avec un bloc donné comme chef. */
static PyObject *py_graph_cluster_find_by_block(PyObject *, PyObject *);

/* Recherche le groupe de blocs avec un composant comme chef. */
static PyObject *py_graph_cluster_find_by_widget(PyObject *, PyObject *);

/* Recherche le groupe de blocs avec une cible particulière. */
static PyObject *py_graph_cluster_find(PyObject *, PyObject *);

/* Construit un graphique à partir de blocs basiques. */
static PyObject *py_graph_cluster_bootstrap(PyObject *, PyObject *);

/* Collecte tous les chefs de file de blocs de code. */
static PyObject *py_graph_cluster_collect(PyObject *, PyObject *);

/* Collecte tous les liens de chefs de file de blocs de code. */
static PyObject *py_graph_cluster_collect_edges(PyObject *, PyObject *);

/* Fournit le bloc de code principal du groupe. */
static PyObject *py_graph_cluster_get_block(PyObject *, void *);

/* Fournit le composant graphique principal du groupe. */
static PyObject *py_graph_cluster_get_widget(PyObject *, void *);

/* Fournit l'emplacement prévu pour un chef de file de blocs. */
static PyObject *py_graph_cluster_get_allocation(PyObject *, void *);

/* Détermine l'emplacement requis d'un ensemble de blocs. */
static PyObject *py_graph_cluster_get_needed_alloc(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = arguments fournis pour l'appel.                       *
*                                                                             *
*  Description : Recherche le groupe de blocs avec un bloc donné comme chef.  *
*                                                                             *
*  Retour      : Groupe trouvé ou None en cas d'échec.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_graph_cluster_find_by_block(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GCodeBlock *block;                      /* Bloc de code à retrouver    */
    int ret;                                /* Bilan de lecture des args.  */
    GGraphCluster *cluster;                 /* Ensemble mis en place       */
    GGraphCluster *found;                   /* Ensemble graphique trouvé   */

    ret = PyArg_ParseTuple(args, "O&",
                           convert_to_code_block, &block);
    if (!ret) return NULL;

    cluster = G_GRAPH_CLUSTER(pygobject_get(self));

    found = g_graph_cluster_find_by_block(cluster, block);

    if (found != NULL)
    {
        result = pygobject_new(G_OBJECT(found));
        g_object_unref(G_OBJECT(found));
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
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = arguments fournis pour l'appel.                       *
*                                                                             *
*  Description : Recherche le groupe de blocs avec un composant comme chef.   *
*                                                                             *
*  Retour      : Groupe trouvé ou None en cas d'échec.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_graph_cluster_find_by_widget(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    PyObject *gtk_mod;                      /* Module Python Gtk           */
    PyObject *type;                         /* Module "GtkWidget"          */
    PyObject *widget_obj;                   /* Composant GTK en Python     */
    int ret;                                /* Bilan de lecture des args.  */
    GGraphCluster *cluster;                 /* Ensemble mis en place       */
    GtkWidget *widget;                      /* Composant GTK à retrouver   */
    GGraphCluster *found;                   /* Ensemble graphique trouvé   */

    gtk_mod = PyImport_ImportModule("gi.repository.Gtk");

    if (gtk_mod == NULL)
    {
        PyErr_SetString(PyExc_TypeError, "unable to find the Gtk Python module");
        return NULL;
    }

    type = PyObject_GetAttrString(gtk_mod, "Widget");

    Py_DECREF(gtk_mod);

    ret = PyArg_ParseTuple(args, "O!", type, &widget_obj);

    Py_DECREF(type);

    if (!ret) return NULL;

    cluster = G_GRAPH_CLUSTER(pygobject_get(self));

    widget = GTK_WIDGET(pygobject_get(widget_obj));

    found = g_graph_cluster_find_by_widget(cluster, widget);

    if (found != NULL)
    {
        result = pygobject_new(G_OBJECT(found));
        g_object_unref(G_OBJECT(found));
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
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = arguments fournis pour l'appel.                       *
*                                                                             *
*  Description : Recherche le groupe de blocs avec une cible particulière.    *
*                                                                             *
*  Retour      : Groupe trouvé ou None en cas d'échec.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_graph_cluster_find(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    PyObject *block_or_widget;              /* Objet Python fourni         */
    int ret;                                /* Bilan de lecture des args.  */

    ret = PyArg_ParseTuple(args, "O", &block_or_widget);
    if (!ret) return NULL;

    ret = PyObject_IsInstance(block_or_widget, (PyObject *)get_python_code_block_type());

    if (ret == 1)
        result = py_graph_cluster_find_by_block(self, args);

    else
    {
        PyErr_Clear();
        result = py_graph_cluster_find_by_widget(self, args);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = arguments fournis pour l'appel.                       *
*                                                                             *
*  Description : Construit un graphique à partir de blocs basiques.           *
*                                                                             *
*  Retour      : Structure mise en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_graph_cluster_bootstrap(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GLoadedBinary *binary;                  /* Binaire chargé avec contenu */
    GBlockList *list;                       /* Liste de blocs de code      */
    int ret;                                /* Bilan de lecture des args.  */
    GGraphCluster *cluster;                 /* Ensemble mis en place       */

    ret = PyArg_ParseTuple(args, "O&O&",
                           convert_to_loaded_binary, &binary,
                           convert_to_block_list_with_ref, &list);
    if (!ret) return NULL;

    cluster = bootstrap_graph_cluster(binary, list, NULL);

    if (cluster != NULL)
    {
        result = pygobject_new(G_OBJECT(cluster));
        g_object_unref(G_OBJECT(cluster));
    }
    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    g_object_unref(G_OBJECT(list));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = arguments fournis pour l'appel.                       *
*                                                                             *
*  Description : Collecte tous les chefs de file de blocs de code.            *
*                                                                             *
*  Retour      : Liste de graphiques de blocs rassemblés.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_graph_cluster_collect(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Liste à retourner           */
    GGraphCluster *root;                    /* Chef de file à analyser     */
    size_t count;                           /* Taille de la liste          */
    GGraphCluster **list;                   /* Liste constituée            */
    size_t i;                               /* Boucle de parcours          */
    PyObject *item;                         /* Instance à transmettre      */

    root = G_GRAPH_CLUSTER(pygobject_get(self));

    list = collect_graph_clusters(root, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        item = pygobject_new(G_OBJECT(list[i]));
        g_object_unref(G_OBJECT(list[i]));

        PyTuple_SetItem(result, i, item);

    }

    if (list != NULL)
        free(list);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = arguments fournis pour l'appel.                       *
*                                                                             *
*  Description : Collecte tous les liens de chefs de file de blocs de code.   *
*                                                                             *
*  Retour      : Liste de liens graphiques de blocs rassemblés.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_graph_cluster_collect_edges(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Liste à retourner           */
    GGraphCluster *root;                    /* Chef de file à analyser     */
    size_t count;                           /* Taille de la liste          */
    GGraphEdge **list;                      /* Liste constituée            */
    size_t i;                               /* Boucle de parcours          */
    PyObject *item;                         /* Instance à transmettre      */

    root = G_GRAPH_CLUSTER(pygobject_get(self));

    list = collect_graph_cluster_edges(root, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        item = pygobject_new(G_OBJECT(list[i]));
        g_object_unref(G_OBJECT(list[i]));

        PyTuple_SetItem(result, i, item);

    }

    if (list != NULL)
        free(list);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le bloc de code principal du groupe.                 *
*                                                                             *
*  Retour      : Bloc de code associé.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_graph_cluster_get_block(PyObject *self, void *closure)
{
    PyObject *result;                       /* Construction à retourner    */
    GGraphCluster *cluster;                 /* Version GLib du type        */
    GCodeBlock *block;                      /* Bloc de code associé        */

    cluster = G_GRAPH_CLUSTER(pygobject_get(self));

    block = g_graph_cluster_get_block(cluster);

    result = pygobject_new(G_OBJECT(block));

    g_object_unref(G_OBJECT(block));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le composant graphique principal du groupe.          *
*                                                                             *
*  Retour      : Composant graphique principal utilisé.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_graph_cluster_get_widget(PyObject *self, void *closure)
{
    PyObject *result;                       /* Construction à retourner    */
    GGraphCluster *cluster;                 /* Version GLib du type        */
    GtkWidget *widget;                      /* Composant graphique associé */

    cluster = G_GRAPH_CLUSTER(pygobject_get(self));

    widget = g_graph_cluster_get_widget(cluster);

    result = new_pygobject_widget(widget);

    g_object_unref(G_OBJECT(widget));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'emplacement prévu pour un chef de file de blocs.   *
*                                                                             *
*  Retour      : Emplacement idéal pour l'affichage.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_graph_cluster_get_allocation(PyObject *self, void *closure)
{
    PyObject *result;                       /* Construction à retourner    */
    GGraphCluster *cluster;                 /* Version GLib du type        */
    GtkAllocation alloc;                    /* Aire à convertir en Python  */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    cluster = G_GRAPH_CLUSTER(pygobject_get(self));

    g_graph_cluster_get_allocation(cluster, &alloc);

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

#define TRANSLATE_ALLOC_FIELD(_n, _v)                       \
    do                                                      \
    {                                                       \
        attrib = PyLong_FromUnsignedLongLong(_v);           \
        ret = PyDict_SetItemString(result, _n, attrib);     \
        if (ret != 0) goto failed;                          \
    }                                                       \
    while (0);

    TRANSLATE_ALLOC_FIELD("x", alloc.x);
    TRANSLATE_ALLOC_FIELD("y", alloc.y);
    TRANSLATE_ALLOC_FIELD("width", alloc.width);
    TRANSLATE_ALLOC_FIELD("height", alloc.height);

    return result;

 failed:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Détermine l'emplacement requis d'un ensemble de blocs.       *
*                                                                             *
*  Retour      : Emplacement idéal pour l'affichage.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_graph_cluster_get_needed_alloc(PyObject *self, void *closure)
{
    PyObject *result;                       /* Construction à retourner    */
    GGraphCluster *cluster;                 /* Version GLib du type        */
    GtkAllocation alloc;                    /* Aire à convertir en Python  */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */

    cluster = G_GRAPH_CLUSTER(pygobject_get(self));

    g_graph_cluster_compute_needed_alloc(cluster, &alloc);

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

#define TRANSLATE_ALLOC_FIELD(_n, _v)                       \
    do                                                      \
    {                                                       \
        attrib = PyLong_FromUnsignedLongLong(_v);           \
        ret = PyDict_SetItemString(result, _n, attrib);     \
        if (ret != 0) goto failed;                          \
    }                                                       \
    while (0);

    TRANSLATE_ALLOC_FIELD("x", alloc.x);
    TRANSLATE_ALLOC_FIELD("y", alloc.y);
    TRANSLATE_ALLOC_FIELD("width", alloc.width);
    TRANSLATE_ALLOC_FIELD("height", alloc.height);

    return result;

 failed:

    Py_DECREF(result);

    return NULL;

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

PyTypeObject *get_python_graph_cluster_type(void)
{
    static PyMethodDef py_graph_cluster_methods[] = {
        {
            "find_by_block", py_graph_cluster_find_by_block,
            METH_VARARGS,
            "find_by_block(block, /)\n--\n\nFind the cluster associated with a given code block."
        },
        {
            "find_by_widget", py_graph_cluster_find_by_widget,
            METH_VARARGS,
            "find_by_widget(widget, /)\n--\n\nFind the cluster associated with a given GTK widget."
        },
        {
            "find", py_graph_cluster_find,
            METH_VARARGS,
            "find(block_or_widget, /)\n--\n\nFind a cluster depending on the provided property."
            "\n"
            "Alias for find_by_block() or find_by_widget()."
        },
        {
            "bootstrap", py_graph_cluster_bootstrap,
            METH_VARARGS | METH_STATIC,
            "bootstrap(binary, list, /)\n--\n\nBuild a graph cluster from a binary and a list of code blocks."
        },
        {
            "collect_clusters", py_graph_cluster_collect,
            METH_NOARGS,
            "collect_clusters()\n--\n\nCollect all clusters involvded in a graph view clustering."
        },
        {
            "collect_edges", py_graph_cluster_collect_edges,
            METH_NOARGS,
            "collect_edges()\n--\n\nCollect all cluster edges involvded in a graph view clustering."
        },
        { NULL }
    };

    static PyGetSetDef py_graph_cluster_getseters[] = {
        {
            "block", py_graph_cluster_get_block, NULL,
            "Main code block linked to the cluster.", NULL
        },
        {
            "widget", py_graph_cluster_get_widget, NULL,
            "GTK widget built to display the code block linked to the cluster.", NULL
        },
        {
            "allocation", py_graph_cluster_get_allocation, NULL,
            "Area allocated for the cluster code block.", NULL
        },
        {
            "needed_alloc", py_graph_cluster_get_needed_alloc, NULL,
            "Area needed for the cluster code block and all its children.", NULL
        },
        { NULL }
    };

    static PyTypeObject py_graph_cluster_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.gtkext.graph.GraphCluster",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "Graphical cluster used in the graph view.\n" \
                          "\n" \
                          "The aim of this object is to provide a read-only " \
                          "access to the information relative to graphical " \
                          "cluster contained in a layout.",

        .tp_methods     = py_graph_cluster_methods,
        .tp_getset      = py_graph_cluster_getseters,

        .tp_new         = no_python_constructor_allowed,

    };

    return &py_graph_cluster_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.gtkext..GraphCluster'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_graph_cluster_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BinPortion'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_graph_cluster_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.gtkext.graph");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_GRAPH_CLUSTER, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en ensemble de blocs de code.             *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_graph_cluster(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_graph_cluster_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to graph cluster");
            break;

        case 1:
            *((GGraphCluster **)dst) = G_GRAPH_CLUSTER(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
