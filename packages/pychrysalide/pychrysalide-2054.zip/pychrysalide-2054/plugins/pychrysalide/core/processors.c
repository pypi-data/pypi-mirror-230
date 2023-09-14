
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processors.c - équivalent Python du fichier "core/processors.c"
 *
 * Copyright (C) 2019-2020 Cyrille Bagard
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


#include "processors.h"


#include <malloc.h>
#include <pygobject.h>


#include <i18n.h>
#include <arch/processor.h>
#include <core/processors.h>


#include "../access.h"
#include "../core.h"
#include "../helpers.h"
#include "../arch/processor.h"



/* Enregistre un processeur pour une architecture donnée. */
static PyObject *py_processors_register_processor(PyObject *, PyObject *);

/* Fournit la liste des processeurs d'architecture disponibles. */
static PyObject *py_processors_get_all_processor_keys(PyObject *, PyObject *);

/* Fournit le processeur d'architecture correspondant à un nom. */
static PyObject *py_processors_get_processor_for_key(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Enregistre un processeur pour une architecture donnée.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_processors_register_processor(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    PyObject *type;                         /* Type d'une instance future  */
    int ret;                                /* Bilan de lecture des args.  */
    PyObject *new_args;                     /* Nouveaux arguments épurés   */
    PyObject *new_kwds;                     /* Nouveau dictionnaire épuré  */
    PyObject *dummy;                        /* Coquille vide pour analyse  */
    GType instance;                         /* Type pour futures instances */
    bool status;                            /* Bilan d'un enregistrement   */

#define PROCESSORS_REGISTER_PROCESSOR_METHOD PYTHON_METHOD_DEF           \
(                                                                           \
    register_processor, "inst, /",                                          \
    METH_VARARGS, py_processors,                                            \
    "Register an architecture processor using an initial instance of it.\n" \
    "\n"                                                                    \
    "This instance has to be a subclass of pychrysalide.arch.ArchProcessor."\
)

    ret = PyArg_ParseTuple(args, "O!", &PyType_Type, &type);
    if (!ret) return NULL;

    ret = PyObject_IsSubclass(type, (PyObject *)get_python_arch_processor_type());;
    if (ret == -1) return NULL;

    if (ret != 1)
    {
        PyErr_SetString(PyExc_TypeError, _("The new processor should be a subclass of the ArchProcessor type."));
        return NULL;
    }

    /**
     * Comme le type GLib n'est initié et enregistré qu'à la création d'une première instance,
     * on force sa mise en place ici, afin de ne pas contraidre l'utilisateur à le faire
     * lui même via un appel du style :
     *
     *    register_processor('aaa', 'BBB CCC', type(AaaProcessor()))
     */

    new_args = PyTuple_New(0);
    new_kwds = PyDict_New();

    dummy = PyObject_Call(type, new_args, new_kwds);

    Py_DECREF(new_kwds);
    Py_DECREF(new_args);

    if (dummy == NULL) return NULL;

    instance = pyg_type_from_object_strict((PyObject *)Py_TYPE(dummy), TRUE);
    assert(instance != 0 && instance != G_TYPE_ARCH_PROCESSOR);

    Py_DECREF(dummy);

    status = register_processor_type(instance);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Fournit la liste des processeurs d'architecture disponibles. *
*                                                                             *
*  Retour      : Liste de nom technique des processeurs enregistrés.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_processors_get_all_processor_keys(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    size_t count;                           /* Taille de la liste retournée*/
    char **keys;                            /* Noms techniques à traiter   */
    size_t i;                               /* Boucle de parcours          */

#define PROCESSORS_GET_ALL_PROCESSOR_KEYS_METHOD PYTHON_METHOD_DEF          \
(                                                                           \
    get_all_processor_keys, "",                                             \
    METH_NOARGS, py_processors,                                             \
    "Provide the list of keys from all registered architecture processors." \
)

    keys = get_all_processor_keys(&count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        PyTuple_SetItem(result, i, PyUnicode_FromString(keys[i]));
        free(keys[i]);
    }

    if (keys != NULL)
        free(keys);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Fournit le processeur d'architecture correspondant à un nom. *
*                                                                             *
*  Retour      : Processeur d'architecture trouvé.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_processors_get_processor_for_key(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    const char *key;                        /* Nom technique de processeur */
    int ret;                                /* Bilan de lecture des args.  */
    GArchProcessor *proc;                   /* Instance mise en place      */

#define PROCESSORS_GET_PROCESSOR_FOR_KEY_METHOD PYTHON_METHOD_DEF           \
(                                                                           \
    get_processor_for_key, "key, /",                                        \
    METH_VARARGS, py_processors,                                            \
    "Provide an instance of an architecture processor for a given name,"    \
    " provided as a key string.\n"                                          \
    "\n"                                                                    \
    "The return instance is a pychrysalide.arch.ArchProcessor subclass."    \
)

    ret = PyArg_ParseTuple(args, "s", &key);
    if (!ret) return NULL;

    proc = get_arch_processor_for_key(key);

    if (proc != NULL)
    {
        result = pygobject_new(G_OBJECT(proc));
        g_object_unref(G_OBJECT(proc));
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
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Définit une extension du module 'core' à compléter.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_core_module_with_processors(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_processors_methods[] = {
        PROCESSORS_REGISTER_PROCESSOR_METHOD,
        PROCESSORS_GET_ALL_PROCESSOR_KEYS_METHOD,
        PROCESSORS_GET_PROCESSOR_FOR_KEY_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.core");

    result = register_python_module_methods(module, py_processors_methods);

    return result;

}
