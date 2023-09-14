
/* Chrysalide - Outil d'analyse de fichiers binaires
 * singleton.c - équivalent Python du fichier "glibext/singleton.c"
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#include "singleton.h"


#include <assert.h>
#include <pygobject.h>


#include <glibext/singleton-int.h>
#include <plugins/dt.h>


#include "../access.h"
#include "../helpers.h"



/* ------------------ INTERFACE POUR CANDIDAT A UNE CENTRALISATION ------------------ */


/* Procède à l'initialisation de l'interface de candidature. */
static void py_singleton_candidate_interface_init(GSingletonCandidateIface *, gpointer *);

/* Fournit une liste de candidats embarqués par un candidat. */
static GSingletonCandidate **py_singleton_candidate_list_inner_instances_wrapper(const GSingletonCandidate *, size_t *);

/* Met à jour une liste de candidats embarqués par un candidat. */
static void py_singleton_candidate_update_inner_instances_wrapper(GSingletonCandidate *, GSingletonCandidate **, size_t);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint py_singleton_candidate___hash__wrapper(const GSingletonCandidate *);

/* Détermine si deux candidats à l'unicité sont identiques. */
static gboolean py_singleton_candidate___eq__wrapper(const GSingletonCandidate *, const GSingletonCandidate *);

/* Marque un candidat comme figé. */
static void py_singleton_candidate_set_ro_wrapper(GSingletonCandidate *);

/* Indique si le candidat est figé. */
static bool py_singleton_candidate_is_ro_wrapper(const GSingletonCandidate *);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static PyObject *py_singleton_candidate_hash(PyObject *, PyObject *);

/* Fournit une liste de candidats embarqués par un candidat. */
static PyObject *py_singleton_candidate_get_inner_instances(PyObject *, void *);

/* Indique si le candidat est figé. */
static PyObject *py_singleton_candidate_get_read_only(PyObject *, void *);

/* Effectue une comparaison avec un objet 'SingletonCandidate'. */
static PyObject *py_singleton_candidate_richcompare(PyObject *, PyObject *, int);



/* ------------------------- COLLECTION D'INSTANCES UNIQUES ------------------------- */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_singleton_factory_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_singleton_factory_init(PyObject *, PyObject *, PyObject *);

/* Fournit l'instance unique correspondant à un objet. */
static PyObject *py_singleton_factory_get_instance(PyObject *, PyObject *);



/* ---------------------------------------------------------------------------------- */
/*                    INTERFACE POUR CANDIDAT A UNE CENTRALISATION                    */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : iface  = interface GLib à initialiser.                       *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de candidature.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_singleton_candidate_interface_init(GSingletonCandidateIface *iface, gpointer *unused)
{
#define SINGLETON_CANDIDATE_DOC                                             \
    "The SingletonCandidate class is a required interface for objects"      \
    " aiming at becoming singleton instances. All shared singletons are"    \
    " registered within a pychrysalide.glibext.SingletonFactory object.\n"  \
    "\n"                                                                    \
    "The main implemantations come with types derived from"                 \
    " pychrysalide.analysis.DataType.\n"                                    \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, SingletonCandidate):\n"            \
    "        ...\n"                                                         \
    "\n"                                                                    \
    "The following methods have to be defined for new implementations:\n"   \
    "* pychrysalide.glibext.SingletonCandidate._list_inner_instances();\n"  \
    "* pychrysalide.glibext.SingletonCandidate._update_inner_instances();\n"\
    "* pychrysalide.glibext.SingletonCandidate.__hash__();\n"               \
    "* pychrysalide.glibext.SingletonCandidate.__eq__();\n"                 \
    "* pychrysalide.glibext.SingletonCandidate._set_read_only();\n"         \
    "* pychrysalide.glibext.SingletonCandidate._is_read_only().\n"

    iface->update_inner = py_singleton_candidate_update_inner_instances_wrapper;
    iface->list_inner = py_singleton_candidate_list_inner_instances_wrapper;

    iface->hash = py_singleton_candidate___hash__wrapper;
    iface->is_equal = py_singleton_candidate___eq__wrapper;

    iface->set_ro = py_singleton_candidate_set_ro_wrapper;
    iface->is_ro = py_singleton_candidate_is_ro_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                count     = quantité d'instances à l'unicité internes.       *
*                                                                             *
*  Description : Fournit une liste de candidats embarqués par un candidat.    *
*                                                                             *
*  Retour      : Liste de candidats internes ou NULL si aucun.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GSingletonCandidate **py_singleton_candidate_list_inner_instances_wrapper(const GSingletonCandidate *candidate, size_t *count)
{
    GSingletonCandidate **result;           /* Instances à retourner       */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyinstances;                  /* Liste en version Python     */
    int ret;                                /* Bilan d'un appel            */
    Py_ssize_t size;                        /* Taille de la liste          */
    Py_ssize_t i;                           /* Boucle de parcours #1       */
    PyObject *pyinstance;                   /* Instance interne            */
    Py_ssize_t k;                           /* Boucle de parcours #2       */

#define SINGLETON_CANDIDATE_LIST_INNER_INSTANCES_WRAPPER PYTHON_WRAPPER_DEF     \
(                                                                               \
    _list_inner_instances, "$self, /",                                          \
    METH_NOARGS,                                                                \
    "Provide an internal access to the list of optional internal singleton"     \
    " candidate instances.\n"                                                   \
    "\n"                                                                        \
    "The result has to be a tuple containing zero or more"                      \
    " pychrysalide.glibext.SingletonCandidate instances."                       \
)

    result = NULL;
    *count = 0;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(candidate));

    if (has_python_method(pyobj, "_list_inner_instances"))
    {
        pyinstances = run_python_method(pyobj, "_list_inner_instances", NULL);

        if (pyinstances != NULL)
        {
            ret = PyTuple_Check(pyinstances);
            if (!ret)
            {
                PyErr_SetString(PyExc_TypeError, "the _inner_instances attribute must be a tuple");
                goto done;
            }

            size = PyTuple_GET_SIZE(pyinstances);

            result = calloc(size, sizeof(GSingletonCandidate *));

            for (i = 0; i < size; i++)
            {
                pyinstance = PyTuple_GET_ITEM(pyinstances, i);

                ret = PyObject_IsInstance(pyinstance, (PyObject *)get_python_singleton_candidate_type());
                if (ret != 1)
                {
                    PyErr_SetString(PyExc_TypeError, "the _inner_instances attribute must only contain pychrysalide.glibext.SingletonCandidate instances");

                    for (k = 0; k < i; k++)
                        g_object_unref(G_OBJECT(result[k]));

                    free(result);
                    result = NULL;

                    goto done;

                }

                result[i] = G_SINGLETON_CANDIDATE(pygobject_get(pyinstance));
                assert(result[i] != NULL);

                g_object_ref(G_OBJECT(result[i]));

            }

            *count = size;

 done:

            Py_DECREF(pyinstances);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                instances = liste de candidats internes devenus singletons.  *
*                count     = quantité d'instances à l'unicité internes.       *
*                                                                             *
*  Description : Met à jour une liste de candidats embarqués par un candidat. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_singleton_candidate_update_inner_instances_wrapper(GSingletonCandidate *candidate, GSingletonCandidate **instances, size_t count)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyinstances;                  /* Liste d'instances converties*/
    size_t i;                               /* Boucle de parcours          */
    PyObject *pyret;                        /* Bilan de consultation       */

#define SINGLETON_CANDIDATE_UPDATE_INNER_INSTANCES_WRAPPER PYTHON_WRAPPER_DEF           \
(                                                                                       \
    _update_inner_instances, "$self, instances, /",                                     \
    METH_VARARGS,                                                                       \
    "Update the list of internal singleton candidate instances.\n"                      \
    "\n"                                                                                \
    "The provided *instances* are a tuple of pychrysalide.glibext.SingletonCandidate"   \
    " objets promoted as singletons."                                                   \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(candidate));

    if (has_python_method(pyobj, "_update_inner_instances"))
    {
        args = PyTuple_New(1);

        pyinstances = PyTuple_New(count);
        PyTuple_SetItem(args, 0, pyinstances);

        for (i = 0; i < count; i++)
            PyTuple_SetItem(pyinstances, i, pygobject_new(G_OBJECT(instances[i])));

        pyret = run_python_method(pyobj, "_update_inner_instances", args);

        Py_XDECREF(pyret);
        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                                                                             *
*  Description : Fournit l'empreinte d'un candidat à une centralisation.      *
*                                                                             *
*  Retour      : Empreinte de l'élément représenté.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint py_singleton_candidate___hash__wrapper(const GSingletonCandidate *candidate)
{
    guint result;                           /* Empreinte à retourner       */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define SINGLETON_CANDIDATE_HASH_WRAPPER PYTHON_WRAPPER_DEF             \
(                                                                       \
    __hash__, "$self, /",                                               \
    METH_NOARGS,                                                        \
    "Abstract method used to produce a hash of the object.\n"           \
    "\n"                                                                \
    "The result must be an integer value up to 64 bits."                \
    "\n"                                                                \
    "Inner instances which are listed through the"                      \
    " pychrysalide.glibext.SingletonCandidate._list_inner_instances()"  \
    " method do not need to get processed here as they are handled"     \
    " automatically by the interface core."                             \
)

    result = 0;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(candidate));

    if (has_python_method(pyobj, "__hash__"))
    {
        pyret = run_python_method(pyobj, "__hash__", NULL);

        if (pyret != NULL)
        {
            if (PyLong_Check(pyret))
                result = PyLong_AsUnsignedLongMask(pyret);

            Py_DECREF(pyret);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                other     = second élément à analyser.                       *
*                                                                             *
*  Description : Détermine si deux candidats à l'unicité sont identiques.     *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean py_singleton_candidate___eq__wrapper(const GSingletonCandidate *candidate, const GSingletonCandidate *other)
{
    guint result;                           /* Empreinte à retourner       */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyret;                        /* Bilan de consultation       */

#define SINGLETON_CANDIDATE_EQ_WRAPPER PYTHON_WRAPPER_DEF       \
(                                                               \
    __eq__, "$self, other, /",                                  \
    METH_NOARGS,                                                \
    "Abstract method used to provide the *__eq__* method for"   \
    " rich comparison.\n"                                       \
    "\n"                                                        \
    "The expected result is a boolean value."                   \
)

    result = 0;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(candidate));

    if (has_python_method(pyobj, "__eq__"))
    {
        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(other)));

        pyret = run_python_method(pyobj, "__eq__", args);

        if (pyret != NULL)
        {
            if (PyLong_Check(pyret))
                result = PyLong_AsUnsignedLong(pyret);

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
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                                                                             *
*  Description : Marque un candidat comme figé.                               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_singleton_candidate_set_ro_wrapper(GSingletonCandidate *candidate)
{
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define SINGLETON_CANDIDATE_SET_RO_WRAPPER PYTHON_WRAPPER_DEF   \
(                                                               \
    _set_read_only, "$self, /",                        \
    METH_NOARGS,                                                \
    "Abstract method used to mark the content of a singleton"   \
    " candidate as read-only.\n"                                \
    "\n"                                                        \
    "The read-only state is mandatory once the candidate is"    \
    " registered inside a pychrysalide.glibext.SingletonFactory"\
    " instance as official singleton."                          \
)

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(candidate));

    if (has_python_method(pyobj, "_set_read_only"))
    {
        pyret = run_python_method(pyobj, "_set_read_only", NULL);

        Py_XDECREF(pyret);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : candidate = objet dont l'instance se veut unique.            *
*                                                                             *
*  Description : Indique si le candidat est figé.                             *
*                                                                             *
*  Retour      : true si le contenu du candidat ne peut plus être modifié.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_singleton_candidate_is_ro_wrapper(const GSingletonCandidate *candidate)
{
    bool result;                            /* Etat à retourner            */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */

#define SINGLETON_CANDIDATE_IS_RO_WRAPPER PYTHON_WRAPPER_DEF    \
(                                                               \
    _is_read_only, "$self, /",                                  \
    METH_NOARGS,                                                \
    "Abstract method used to retrieve the status of the data"   \
    " contained by a singleton candidate.\n"                    \
    "\n"                                                        \
    "The retured value is *True* if the candidate is"           \
    " registered inside a pychrysalide.glibext.SingletonFactory"\
    " instance as official singleton, *False* otherwise."       \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(candidate));

    if (has_python_method(pyobj, "_is_read_only"))
    {
        pyret = run_python_method(pyobj, "_is_read_only", NULL);

        result = (pyret == Py_True);

        Py_XDECREF(pyret);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet dont l'instance se veut unique.                 *
*                args = adresse non utilisée ici.                             *
*                                                                             *
*  Description : Fournit l'empreinte d'un candidat à une centralisation.      *
*                                                                             *
*  Retour      : Empreinte de l'élément représenté.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_singleton_candidate_hash(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Emplacement à retourner     */
    GSingletonCandidate *candidate;         /* Mécanismes natifs           */
    guint hash;                             /* Valeur d'empreitne          */

#define SINGLETON_CANDIDATE_HASH_METHOD PYTHON_METHOD_DEF           \
(                                                                   \
    hash, "$self",                                                  \
    METH_NOARGS, py_singleton_candidate,                            \
    "Compute the hash value of the singleton candidate.\n"          \
    "\n"                                                            \
    "The method relies on the interface core to include in the"     \
    " process the optional embedded instances which may become"     \
    " singletons.\n"                                                \
    "\n"                                                            \
    "The result is an integer value.\n"                             \
    "\n"                                                            \
    "Even if the Python *hash()* method, relying on the"            \
    " pychrysalide.glibext.SingletonCandidate.__hash__()"           \
    " implementation, provides values up to 64 bits, the final"     \
    " hashes processed by the native GLib hash methods are"         \
    " limited to 32 bits values."                                   \
)

    candidate = G_SINGLETON_CANDIDATE(pygobject_get(self));

    hash = g_singleton_candidate_hash(candidate);

    result = PyLong_FromUnsignedLong(hash);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit une liste de candidats embarqués par un candidat.    *
*                                                                             *
*  Retour      : Liste de candidats internes, vide si aucun.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_singleton_candidate_get_inner_instances(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GSingletonCandidate *candidate;         /* Mécanismes natifs           */
    size_t count;                           /* Quantité d'objets internes  */
    GSingletonCandidate **instances;        /* Liste des embarqués         */
    size_t i;                               /* Boucle de parcours          */

#define SINGLETON_CANDIDATE_INNER_INSTANCES_ATTRIB PYTHON_GET_DEF_FULL  \
(                                                                       \
    inner_instances, py_singleton_candidate,                            \
    "List of optional internal singleton candidate instances.\n"        \
    "\n"                                                                \
    "The result has to be a tuple containing zero or more"              \
    " pychrysalide.glibext.SingletonCandidate instances."               \
)

    candidate = G_SINGLETON_CANDIDATE(pygobject_get(self));

    instances = g_singleton_candidate_list_inner_instances(candidate, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        PyTuple_SetItem(result, i, pygobject_new(G_OBJECT(instances[i])));
        g_object_unref(G_OBJECT(instances[i]));
    }

    if (instances != NULL)
        free(instances);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique si le candidat est figé.                             *
*                                                                             *
*  Retour      : true si le contenu du candidat ne peut plus être modifié.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_singleton_candidate_get_read_only(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GSingletonCandidate *candidate;         /* Mécanismes natifs           */
    bool status;                            /* Etat de l'élément consulté  */

#define SINGLETON_CANDIDATE_READ_ONLY_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                                   \
    read_only, py_singleton_candidate,                              \
    "State of the singleton candidate content.\n"                   \
    "\n"                                                            \
    "The result is a boolean: *True* if the object is registered"   \
    " as singleton, *False* otherwise.\n"                           \
    "\n"                                                            \
    "Once a singleton, the object must not change its content as"   \
    " it is a shared instance."                                     \
)

    candidate = G_SINGLETON_CANDIDATE(pygobject_get(self));

    status = g_singleton_candidate_is_read_only(candidate);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a  = premier object Python à consulter.                      *
*                b  = second object Python à consulter.                       *
*                op = type de comparaison menée.                              *
*                                                                             *
*  Description : Effectue une comparaison avec un objet 'SingletonCandidate'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_singleton_candidate_richcompare(PyObject *a, PyObject *b, int op)
{
    PyObject *result;                       /* Bilan à retourner           */
    int ret;                                /* Bilan de lecture des args.  */
    GSingletonCandidate *cand_a;            /* Premier élément à traiter   */
    GSingletonCandidate *cand_b;            /* Second élément à traiter    */
    gboolean status;                        /* Résultat d'une comparaison  */

    if (op != Py_EQ)
    {
        result = Py_NotImplemented;
        goto cmp_done;
    }

    ret = PyObject_IsInstance(b, (PyObject *)get_python_singleton_candidate_type());
    if (!ret)
    {
        result = Py_NotImplemented;
        goto cmp_done;
    }

    cand_a = G_SINGLETON_CANDIDATE(pygobject_get(a));
    cand_b = G_SINGLETON_CANDIDATE(pygobject_get(b));

    status = g_singleton_candidate_is_equal(cand_a, cand_b);

    result = (status ? Py_True : Py_False);

 cmp_done:

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

PyTypeObject *get_python_singleton_candidate_type(void)
{
    static PyMethodDef py_singleton_candidate_methods[] = {
        SINGLETON_CANDIDATE_LIST_INNER_INSTANCES_WRAPPER,
        SINGLETON_CANDIDATE_UPDATE_INNER_INSTANCES_WRAPPER,
        SINGLETON_CANDIDATE_HASH_WRAPPER,
        SINGLETON_CANDIDATE_EQ_WRAPPER,
        SINGLETON_CANDIDATE_SET_RO_WRAPPER,
        SINGLETON_CANDIDATE_IS_RO_WRAPPER,
        SINGLETON_CANDIDATE_HASH_METHOD,
        { NULL }
    };

    static PyGetSetDef py_singleton_candidate_getseters[] = {
        SINGLETON_CANDIDATE_INNER_INSTANCES_ATTRIB,
        SINGLETON_CANDIDATE_READ_ONLY_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_singleton_candidate_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.SingletonCandidate",
        .tp_basicsize   = sizeof(PyObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = SINGLETON_CANDIDATE_DOC,

        .tp_richcompare = py_singleton_candidate_richcompare,

        .tp_methods     = py_singleton_candidate_methods,
        .tp_getset      = py_singleton_candidate_getseters

    };

    return &py_singleton_candidate_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....SingletonCandidate'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_singleton_candidate_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BinContent'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    static GInterfaceInfo info = {          /* Paramètres d'inscription    */

        .interface_init = (GInterfaceInitFunc)py_singleton_candidate_interface_init,
        .interface_finalize = NULL,
        .interface_data = NULL,

    };

    type = get_python_singleton_candidate_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        dict = PyModule_GetDict(module);

        if (!register_interface_for_pygobject(dict, G_TYPE_SINGLETON_CANDIDATE, type, &info))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en candidat à une centralisation.         *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_singleton_candidate(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_singleton_candidate_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to singleton candidate");
            break;

        case 1:
            *((GSingletonCandidate **)dst) = G_SINGLETON_CANDIDATE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           COLLECTION D'INSTANCES UNIQUES                           */
/* ---------------------------------------------------------------------------------- */


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

static PyObject *py_singleton_factory_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_singleton_factory_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_SINGLETON_FACTORY, type->tp_name, NULL, NULL, NULL);

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

static int py_singleton_factory_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int ret;                                /* Bilan de lecture des args.  */

#define SINGLETON_FACTORY_DOC                                               \
    "The SingletonFactory class reduces the memory footprint by compacting" \
    " the quantity of running instances of a given GLib type.\n"            \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    SingletonFactory()"                                                \
    "\n"                                                                    \
    "The first processed instance defines the type handled by the factory."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "");
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = gestionnaire d'instances uniques à consulter.         *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Fournit l'instance unique correspondant à un objet.          *
*                                                                             *
*  Retour      : Instance unique à utiliser.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_singleton_factory_get_instance(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Emplacement à retourner     */
    GSingletonCandidate *candidate;         /* Candidat à traiter          */
    int ret;                                /* Bilan de lecture des args.  */
    GSingletonFactory *factory;             /* Gestionnaire à manipuler    */
    GSingletonCandidate *instance;          /* Instance unique à retourner */

#define SINGLETON_FACTORY_GET_INSTANCE_METHOD PYTHON_METHOD_DEF         \
(                                                                       \
    get_instance, "$self, candidate, /",                                \
    METH_VARARGS, py_singleton_factory,                                 \
    "Provide the unique instance for a given singleton *candidate*.\n"  \
    "\n"                                                                \
    "The *candidate* object and the result of the function belong to"   \
    " the same type: pychrysalide.glibext.SingletonCandidate."          \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_singleton_candidate, &candidate);
    if (!ret) return NULL;

    factory = G_SINGLETON_FACTORY(pygobject_get(self));

    instance = g_singleton_factory_get_instance(factory, candidate);

    result = pygobject_new(G_OBJECT(instance));

    g_object_unref(G_OBJECT(instance));

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

PyTypeObject *get_python_singleton_factory_type(void)
{
    static PyMethodDef py_singleton_factory_methods[] = {
        SINGLETON_FACTORY_GET_INSTANCE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_singleton_factory_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_singleton_factory_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.SingletonFactory",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = SINGLETON_FACTORY_DOC,

        .tp_methods     = py_singleton_factory_methods,
        .tp_getset      = py_singleton_factory_getseters,

        .tp_init        = py_singleton_factory_init,
        .tp_new         = py_singleton_factory_new

    };

    return &py_singleton_factory_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....SingletonFactory'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_singleton_factory_is_registered(void)
{
    PyTypeObject *type;                     /* Type 'SingletonFactory'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_singleton_factory_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_SINGLETON_FACTORY, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en compacteur d'instances.                *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_singleton_factory(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_singleton_factory_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to singleton factory");
            break;

        case 1:
            *((GSingletonFactory **)dst) = G_SINGLETON_FACTORY(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
