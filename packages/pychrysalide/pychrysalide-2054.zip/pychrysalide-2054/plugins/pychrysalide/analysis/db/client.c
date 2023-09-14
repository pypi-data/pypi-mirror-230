
/* Chrysalide - Outil d'analyse de fichiers binaires
 * client.c - équivalent Python du fichier "analysis/db/client.c"
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


#include "client.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>
#include <analysis/db/client.h>
#include <core/collections.h>


#include "collection.h"
#include "../../access.h"
#include "../../helpers.h"
#include "../../struct.h"



#define HUB_CLIENT_DOC                                                                  \
    "HubClient provides and receives binary updates to and from a connected"            \
    " to a server.\n"                                                                   \
    "\n"                                                                                \
    "Such clients must be authenticated and communications are encrypted using TLS.\n"  \
    "\n"                                                                                \
    "Instances can be created directly."                                                \
    "\n"                                                                                \
    "HubClient instances emit the following signals:\n"                                 \
    "* 'snapshots-updated'\n"                                                           \
    "    This signal is emitted when the snapshot list has evolved.\n"                  \
    "\n"                                                                                \
    "    Handlers are expected to have only one argument: the client managing the"      \
    "    updated snapshots.\n"                                                          \
    "* 'snapshot-changed'\n"                                                            \
    "    This signal is emitted when the identifier of the current snapshot changed.\n" \
    "\n"                                                                                \
    "    Handlers are expected to have only one argument: the client managing the"      \
    "    snapshots."



/* Démarre la connexion à la base de données. */
static PyObject *py_hub_client_start(PyObject *, PyObject *);

/* Arrête la connexion à la base de données. */
static PyObject *py_hub_client_stop(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = client à manipuler.                                   *
*                args = paramètres à transmettre à l'appel natif.             *
*                                                                             *
*  Description : Démarre la connexion à la base de données.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_hub_client_start(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    const char *host;                       /* Désignation de serveur      */
    const char *port;                       /* Port d'écoute associé       */
    bool ipv6;                              /* Préférence pour IPv6 ?      */
    int ret;                                /* Bilan de lecture des args.  */
    GHubClient *client;                     /* Version native du serveur   */
    bool status;                            /* Bilan de l'opération        */

#define HUB_CLIENT_START_METHOD PYTHON_METHOD_DEF                   \
(                                                                   \
    start, "$self, /, host=None, port='1337', ipv6=True",           \
    METH_VARARGS, py_hub_client,                                    \
    "Connect to a server for binary updates.\n"                     \
    "\n"                                                            \
    "host and port define the properties of the server, and ipv6"   \
    " tries to establish IPv6 connections first."                   \
)

    host = NULL;
    port = "1337";
    ipv6 = true;

    ret = PyArg_ParseTuple(args, "|ssp", &host, &port, &ipv6);
    if (!ret) return NULL;

    client = G_HUB_CLIENT(pygobject_get(self));

    if (host == NULL)
        status = g_hub_client_start_internal(client);
    else
        status = g_hub_client_start_remote(client, host, port, ipv6);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = client à manipuler.                                   *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Arrête la connexion à la base de données.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_hub_client_stop(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GHubClient *client;                     /* Version native du serveur   */

#define HUB_CLIENT_STOP_METHOD PYTHON_METHOD_DEF    \
(                                                   \
    stop, "$self, /",                               \
    METH_NOARGS, py_hub_client,                     \
    "Stop the client."                              \
)

    client = G_HUB_CLIENT(pygobject_get(self));

    g_hub_client_stop(client);

    result = Py_None;
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

PyTypeObject *get_python_hub_client_type(void)
{
    static PyMethodDef py_hub_client_methods[] = {
        HUB_CLIENT_START_METHOD,
        HUB_CLIENT_STOP_METHOD,
        { NULL }
    };

    static PyGetSetDef py_hub_client_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_hub_client_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.db.HubClient",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = HUB_CLIENT_DOC,

        .tp_methods     = py_hub_client_methods,
        .tp_getset      = py_hub_client_getseters,
        .tp_new         = no_python_constructor_allowed,

    };

    return &py_hub_client_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....db.HubClient'.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_hub_client_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'HubClient'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_hub_client_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.db");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_HUB_CLIENT, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en client de base de données.             *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_hub_client(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_hub_client_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to hub client");
            break;

        case 1:
            *((GHubClient **)dst) = G_HUB_CLIENT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
