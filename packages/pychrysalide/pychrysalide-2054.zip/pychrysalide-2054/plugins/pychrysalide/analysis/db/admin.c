
/* Chrysalide - Outil d'analyse de fichiers binaires
 * admin.c - équivalent Python du fichier "analysis/db/admin.c"
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


#include "admin.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>
#include <analysis/db/admin.h>


#include "client.h"
#include "../../access.h"
#include "../../helpers.h"



/* Crée un nouvel objet Python de type 'AdminClient'. */
static PyObject *py_admin_client_new(PyTypeObject *, PyObject *, PyObject *);

/* Effectue une demande de liste de binaires existants. */
static PyObject *py_admin_client_request_existing_binaries(PyObject *, PyObject *);

/* Fournit la liste des instantanés existants. */
static PyObject *py_admin_client_get_existing_binaries(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'AdminClient'.           *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_admin_client_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    GAdminClient *client;                   /* Serveur mis en place        */

#define ADMIN_CLIENT_DOC                                                                \
    "AdminClient provides control of the registered binary contents available from a"   \
    " server.\n"                                                                        \
    "\n"                                                                                \
    "Such clients must be authenticated and communications are encrypted using TLS.\n"  \
    "\n"                                                                                \
    "Instances can be created using the following constructor:\n"                       \
    "\n"                                                                                \
    "    AdminClient()"                                                                 \
    "\n"                                                                                \
    "AdminClient instances emit the following signals:\n"                               \
    "* 'existing-binaries-updated'\n"                                                   \
    "    This signal is emitted when the list of existing binaries on server side"      \
    " has been updated following a user request.\n"                                     \

    client = g_admin_client_new();

    if (client != NULL)
    {
        result = pygobject_new(G_OBJECT(client));
        g_object_unref(client);
    }
    else result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = client à manipuler.                                   *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Effectue une demande de liste de binaires existants.         *
*                                                                             *
*  Retour      : True si la commande a bien été envoyée, False sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_admin_client_request_existing_binaries(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GAdminClient *client;                   /* Version native du serveur   */
    bool status;                            /* Bilan de l'opération        */

#define ADMIN_CLIENT_REQUEST_EXISTING_BINARIES_METHOD PYTHON_METHOD_DEF \
(                                                                       \
    request_existing_binaries, "$self, /",                              \
    METH_NOARGS, py_admin_client,                                       \
    "Ask the server for a list of all existing analyzed binaries"       \
    " and returns the status of the request transmission."              \
    "\n"                                                                \
    "A *existing-binaries-updated* signal is emitted when the"          \
    " pychrysalide.analysis.db.AdminClient.existing_binaries attribute" \
    " gets ready for reading."                                          \
)

    client = G_ADMIN_CLIENT(pygobject_get(self));

    status = g_admin_client_request_existing_binaries(client);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la liste des instantanés existants.                  *
*                                                                             *
*  Retour      : Liste de binaires en place, vide si aucun.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_admin_client_get_existing_binaries(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GAdminClient *client;                   /* Version native du serveur   */
    size_t count;                           /* Taille de cette liste       */
    char **binaries;                        /* Liste des binaires présents */
    size_t i;                               /* Boucle de parcours          */

#define ADMIN_CLIENT_EXISTING_BINARIES_ATTRIB PYTHON_GET_DEF_FULL       \
(                                                                       \
    existing_binaries, py_admin_client,                                 \
    "Provide the list of all exisiting binaries on the server side.\n"  \
    "\n"                                                                \
    "The returned value is a tuple of strings or an empty tuple."       \
)

    client = G_ADMIN_CLIENT(pygobject_get(self));

    binaries = g_admin_client_get_existing_binaries(client, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
        PyTuple_SetItem(result, i, PyUnicode_FromString(binaries[i]));

    if (binaries != NULL)
        free(binaries);

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

PyTypeObject *get_python_admin_client_type(void)
{
    static PyMethodDef py_admin_client_methods[] = {
        ADMIN_CLIENT_REQUEST_EXISTING_BINARIES_METHOD,
        { NULL }
    };

    static PyGetSetDef py_admin_client_getseters[] = {
        ADMIN_CLIENT_EXISTING_BINARIES_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_admin_client_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.db.AdminClient",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = ADMIN_CLIENT_DOC,

        .tp_methods     = py_admin_client_methods,
        .tp_getset      = py_admin_client_getseters,
        .tp_new         = py_admin_client_new,

    };

    return &py_admin_client_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....db.AdminClient'.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_admin_client_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'AdminClient'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_admin_client_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.db");

        dict = PyModule_GetDict(module);

        if (!ensure_python_hub_client_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_ADMIN_CLIENT, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en client administrateur.                 *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_admin_client(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_admin_client_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to admin client");
            break;

        case 1:
            *((GAdminClient **)dst) = G_ADMIN_CLIENT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
