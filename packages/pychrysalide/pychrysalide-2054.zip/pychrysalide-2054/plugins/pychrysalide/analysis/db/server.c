
/* Chrysalide - Outil d'analyse de fichiers binaires
 * server.c - équivalent Python du fichier "analysis/db/server.c"
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


#include "server.h"


#include <pygobject.h>


#include <i18n.h>
#include <analysis/db/server.h>


#include "constants.h"
#include "../../access.h"
#include "../../helpers.h"



/* Crée un nouvel objet Python de type 'HubServer'. */
static PyObject *py_hub_server_new(PyTypeObject *, PyObject *, PyObject *);

/* Démarre le serveur de base de données. */
static PyObject *py_hub_server_start(PyObject *, PyObject *);

/* Arrête le serveur de base de données. */
static PyObject *py_hub_server_stop(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'HubServer'.             *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_hub_server_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *host;                       /* Désignation de serveur      */
    const char *port;                       /* Port d'écoute associé       */
    bool ipv6;                              /* Préférence pour IPv6 ?      */
    int ret;                                /* Bilan de lecture des args.  */
    GHubServer *server;                     /* Serveur mis en place        */

#define HUB_SERVER_DOC                                                                  \
    "HubServer creates a server listening for binary updates from clients.\n"           \
    "\n"                                                                                \
    "Such clients are authenticated and communications are encrypted using TLS.\n"      \
    "\n"                                                                                \
    "There are two kinds of servers:\n"                                                 \
    "* one \"local\", which aims to server one given local user account;\n"             \
    "* one \"remote\", which may target several different users at the same time.\n"    \
    "\n"                                                                                \
    "Instances can be created using the following constructor:\n"                       \
    "\n"                                                                                \
    "    HubServer()"                                                                   \
    "    HubServer(host='localhost', port='1337', ipv6=True)"                           \
    "\n"                                                                                \
    "Where host and port define the listening properties of the server, and ipv6"       \
    " tries to establish IPv6 connections first."                                       \
    "\n"                                                                                \
    "Without any parameters, a local server is created."

    host = NULL;
    port = "1337";
    ipv6 = true;

    ret = PyArg_ParseTuple(args, "|ssp", &host, &port, &ipv6);
    if (!ret) return NULL;

    if (host == NULL)
        server = g_hub_server_new_internal();
    else
        server = g_hub_server_new_remote(host, port, ipv6);

    if (server != NULL)
    {
        result = pygobject_new(G_OBJECT(server));
        g_object_unref(server);
    }
    else result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Démarre le serveur de base de données.                       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_hub_server_start(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    int backlog;                            /* Nombre de connexions        */
    int ret;                                /* Bilan de lecture des args.  */
    GHubServer *server;                     /* Version native du serveur   */
    bool status;                            /* Bilan de l'opération        */

#define HUB_SERVER_START_METHOD PYTHON_METHOD_DEF               \
(                                                               \
    start, "$self, /, backlog=10",                              \
    METH_VARARGS, py_hub_server,                                \
    "Run a listening server waiting for client connections."    \
    "\n"                                                        \
    "The backlog argument defines the maximum length to which"  \
    " the queue of pending connections may grow."               \
    "\n"                                                        \
    "The returned value is a status of type"                    \
    " pychrysalide.analysis.db.HubServer.ServerStartStatus."    \
)

    backlog = 10;

    ret = PyArg_ParseTuple(args, "|i", &backlog);
    if (!ret) return NULL;

    server = G_HUB_SERVER(pygobject_get(self));

    status = g_hub_server_start(server, backlog, true);

    result = cast_with_constants_group_from_type(get_python_hub_server_type(), "ServerStartStatus", status);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = serveur à manipuler.                                  *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Arrête le serveur de base de données.                        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_hub_server_stop(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GHubServer *server;                     /* Version native du serveur   */

#define HUB_SERVER_STOP_METHOD PYTHON_METHOD_DEF    \
(                                                   \
    stop, "$self, /",                               \
    METH_NOARGS, py_hub_server,                     \
    "Stop the listening server."                    \
)

    server = G_HUB_SERVER(pygobject_get(self));

    g_hub_server_stop(server);

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

PyTypeObject *get_python_hub_server_type(void)
{
    static PyMethodDef py_hub_server_methods[] = {
        HUB_SERVER_START_METHOD,
        HUB_SERVER_STOP_METHOD,
        { NULL }
    };

    static PyGetSetDef py_hub_server_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_hub_server_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.db.HubServer",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = HUB_SERVER_DOC,

        .tp_methods     = py_hub_server_methods,
        .tp_getset      = py_hub_server_getseters,
        .tp_new         = py_hub_server_new,

    };

    return &py_hub_server_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....db.HubServer'.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_hub_server_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'HubServer'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_hub_server_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.db");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_HUB_SERVER, type))
            return false;

        if (!define_hub_server_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en serveur de base de données.            *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_hub_server(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_hub_server_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to hub server");
            break;

        case 1:
            *((GHubServer **)dst) = G_HUB_SERVER(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
