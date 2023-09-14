
/* Chrysalide - Outil d'analyse de fichiers binaires
 * analyst.c - équivalent Python du fichier "analysis/db/analyst.c"
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


#include "analyst.h"


#include <assert.h>
#include <pygobject.h>


#include <i18n.h>
#include <analysis/db/analyst-int.h>
#include <core/collections.h>


#include "client.h"
#include "collection.h"
#include "constants.h"
#include "../content.h"
#include "../loaded.h"
#include "../../access.h"
#include "../../helpers.h"
#include "../../struct.h"



/* Initialise une instance sur la base du dérivé de GObject. */
static int py_analyst_client_init(PyObject *, PyObject *, PyObject *);

/* Envoie un contenu binaire pour conservation côté serveur. */
static PyObject *py_analyst_client_send_content(PyObject *, PyObject *);

/* Effectue une demande de sauvegarde de l'état courant. */
static PyObject *py_analyst_client_save(PyObject *, PyObject *);

/* Active les éléments en amont d'un horodatage donné. */
static PyObject *py_analyst_client_set_last_active(PyObject *, PyObject *);

/* Définit la désignation d'un instantané donné. */
static PyObject *py_analyst_client_set_snapshot_name(PyObject *, PyObject *);

/* Définit la désignation d'un instantané donné. */
static PyObject *py_analyst_client_set_snapshot_desc(PyObject *, PyObject *);

/* Restaure un ancien instantané. */
static PyObject *py_analyst_client_restore_snapshot(PyObject *, PyObject *);

/* Crée un nouvel instantané à partir d'un autre. */
static PyObject *py_analyst_client_create_snapshot(PyObject *, PyObject *);

/* Supprime un ancien instantané. */
static PyObject *py_analyst_client_remove_snapshot(PyObject *, PyObject *);

/* Fournit la liste des instantanés existants. */
static PyObject *py_analyst_client_get_snapshots(PyObject *, void *);

/* Fournit l'identifiant de l'instantané courant. */
static PyObject *py_analyst_client_get_current_snapshot(PyObject *, void *);



CREATE_DYN_CONSTRUCTOR(analyst_client, G_TYPE_ANALYST_CLIENT);


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

static int py_analyst_client_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à retourner           */
    GLoadedContent *loaded;                 /* Contenu local déjà chargé   */
    const char *hash;                       /* Empreinte du binaire visé   */
    const char *class;                      /* Nature du contenu analysé   */
    PyObject *list;                         /* Liste Python de collections */
    int ret;                                /* Bilan de lecture des args.  */
    Py_ssize_t length;                      /* Nombre d'éléments collectés */
    GList *collections;                     /* Liste native de collections */
    Py_ssize_t i;                           /* Boucle de parcours          */
    PyObject *item;                         /* Elément de la liste Python  */
    GDbCollection *collec;                  /* Version équivalente native  */
    GAnalystClient *client;                 /* Client mis en place         */
    bool status;                            /* Bilan d'initialisation      */

#define ANALYST_CLIENT_DOC                                                              \
    "AnalystClient provides and receives binary updates to and from a connected"        \
    " to a server.\n"                                                                   \
    "\n"                                                                                \
    "Such clients must be authenticated and communications are encrypted using TLS.\n"  \
    "\n"                                                                                \
    "Instances can be created using the following constructor:\n"                       \
    "\n"                                                                                \
    "    AnalystClient(hash, class, list, loaded=None)"                                 \
    "\n"                                                                                \
    "Where *hash* is a SHA256 fingerprint of the studied binary, *class* refers to"     \
    " the nature description of the loaded content (as provided from"                   \
    " pychrysalide.analysis.LoadedContent.content_class), *list* is a list of"          \
    " pychrysalide.analysis.db.DbCollection instances ; this kind of list can be"       \
    " retrived with the pychrysalide.analysis.LoadedBinary.collections attribute."      \
    " The *loaded* object is an optional local already loaded content which has to"     \
    " be a pychrysalide.analysis.LoadedContent instance or *None*."                     \
    "\n"                                                                                \
    "AnalystClient instances emit the following signals:\n"                             \
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

    loaded = NULL;

    ret = PyArg_ParseTuple(args, "ssO|O&", &hash, &class, &list, convert_to_loaded_content, &loaded);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    if (!PySequence_Check(list))
    {
        PyErr_SetString(PyExc_TypeError, _("The second argument must be a collection list"));
        return -1;
    }

    length = PySequence_Length(list);

    collections = NULL;

    for (i = 0; i < length; i++)
    {
        item = PySequence_GetItem(list, i);

        ret = convert_to_db_collection(item, &collec);

        Py_DECREF(item);

        if (ret != 1)
        {
            delete_collections_list(&collections);
            result = -1;
            goto exit;
        }

        g_object_ref(G_OBJECT(collec));
        collections = g_list_append(collections, collec);

    }

    client = G_ANALYST_CLIENT(pygobject_get(self));

    status = g_analyst_client_setup(client, hash, class, collections, loaded);

    result = status ? 0 : -1;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = client à manipuler.                                   *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Envoie un contenu binaire pour conservation côté serveur.    *
*                                                                             *
*  Retour      : True si la commande a bien été envoyée, False sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_analyst_client_send_content(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GBinContent *content;                   /* Contenu binaire à envoyer   */
    int ret;                                /* Bilan de lecture des args.  */
    GAnalystClient *client;                 /* Version native du serveur   */
    bool status;                            /* Bilan de l'opération        */

#define ANALYST_CLIENT_SEND_CONTENT_METHOD PYTHON_METHOD_DEF                \
(                                                                           \
    send_content, "$self, content, /",                                      \
    METH_VARARGS, py_analyst_client,                                        \
    "Ask the server for saving the current state of the analyzed binary"    \
    " and returns the status of the request transmission."                  \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_binary_content, &content);
    if (!ret) return NULL;

    client = G_ANALYST_CLIENT(pygobject_get(self));

    status = g_analyst_client_send_content(client, content);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = client à manipuler.                                   *
*                args = arguments d'appel non utilisés ici.                   *
*                                                                             *
*  Description : Effectue une demande de sauvegarde de l'état courant.        *
*                                                                             *
*  Retour      : True si la commande a bien été envoyée, False sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_analyst_client_save(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GAnalystClient *client;                 /* Version native du serveur   */
    bool status;                            /* Bilan de l'opération        */

#define ANALYST_CLIENT_SAVE_METHOD PYTHON_METHOD_DEF                        \
(                                                                           \
    save, "$self, /",                                                       \
    METH_NOARGS, py_analyst_client,                                         \
    "Ask the server for saving the current state of the analyzed binary"    \
    " and returns the status of the request transmission."                  \
)

    client = G_ANALYST_CLIENT(pygobject_get(self));

    status = g_analyst_client_save(client);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = client à manipuler.                                   *
*                args = arguments d'appel à consulter.                        *
*                                                                             *
*  Description : Active les éléments en amont d'un horodatage donné.          *
*                                                                             *
*  Retour      : True si la commande a bien été envoyée, False sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_analyst_client_set_last_active(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned long long timestamp;           /* Horodatage de limite        */
    int ret;                                /* Bilan de lecture des args.  */
    GAnalystClient *client;                 /* Version native du serveur   */
    bool status;                            /* Bilan de l'opération        */

#define ANALYST_CLIENT_SET_LAST_ACTIVE_METHOD PYTHON_METHOD_DEF         \
(                                                                       \
    set_last_active, "$self, timestamp, /",                             \
    METH_VARARGS, py_analyst_client,                                    \
    "Define the timestamp of the last active item in the collection"    \
    " and returns the status of the request transmission."              \
    "\n"                                                                \
    "This method should not be used directly. Prefer calling"           \
    " pychrysalide.analysis.LoadedBinary.set_last_active() instead,"    \
    " as some items may be volatile and thus not handled by clients."   \
)

    ret = PyArg_ParseTuple(args, "K", &timestamp);
    if (!ret) return NULL;

    client = G_ANALYST_CLIENT(pygobject_get(self));

    status = g_analyst_client_set_last_active(client, timestamp);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = client à manipuler.                                   *
*                args = arguments d'appel à consulter.                        *
*                                                                             *
*  Description : Définit la désignation d'un instantané donné.                *
*                                                                             *
*  Retour      : True si la commande a bien été envoyée, False sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_analyst_client_set_snapshot_name(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    const char *raw_id;                     /* Identifiant brut            */
    const char *text;                       /* Texte fourni à transmettre  */
    int ret;                                /* Bilan de lecture des args.  */
    snapshot_id_t id;                       /* Identifiant utilisable      */
    bool status;                            /* Bilan d'opération           */
    GAnalystClient *client;                 /* Version native du serveur   */

#define ANALYST_CLIENT_SET_SNAPSHOT_NAME_METHOD PYTHON_METHOD_DEF           \
(                                                                           \
    set_snapshot_name, "$self, id, name, /",                                \
    METH_VARARGS, py_analyst_client,                                        \
    "Ask the server for defining a new name of for a snapshot using its"    \
    " identifier and returns the status of the request transmission."       \
    "\n"                                                                    \
    "A 'snapshots-updated' signal is emitted once the request has been"     \
    " processed with success."                                              \
)

    ret = PyArg_ParseTuple(args, "ss", &raw_id, &text);
    if (!ret) return NULL;

    status = init_snapshot_id_from_text(&id, raw_id);
    if (!status)
    {
        PyErr_SetString(PyExc_TypeError, _("provided value is not a valid snapshot identifier."));
        return NULL;
    }

    client = G_ANALYST_CLIENT(pygobject_get(self));

    status = g_analyst_client_set_snapshot_name(client, &id, text);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = client à manipuler.                                   *
*                args = arguments d'appel à consulter.                        *
*                                                                             *
*  Description : Définit la désignation d'un instantané donné.                *
*                                                                             *
*  Retour      : True si la commande a bien été envoyée, False sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_analyst_client_set_snapshot_desc(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    const char *raw_id;                     /* Identifiant brut            */
    const char *text;                       /* Texte fourni à transmettre  */
    int ret;                                /* Bilan de lecture des args.  */
    snapshot_id_t id;                       /* Identifiant utilisable      */
    bool status;                            /* Bilan d'opération           */
    GAnalystClient *client;                 /* Version native du serveur   */

#define ANALYST_CLIENT_SET_SNAPSHOT_DESC_METHOD PYTHON_METHOD_DEF           \
(                                                                           \
    set_snapshot_desc, "$self, id, desc, /",                                \
    METH_VARARGS, py_analyst_client,                                        \
    "Ask the server for defining a new description for a snapshot using"    \
    " its identifier and returns the status of the request transmission."   \
    "\n"                                                                    \
    "A 'snapshots-updated' signal is emitted once the request has been"     \
    " processed with success."                                              \
)

    ret = PyArg_ParseTuple(args, "ss", &raw_id, &text);
    if (!ret) return NULL;

    status = init_snapshot_id_from_text(&id, raw_id);
    if (!status)
    {
        PyErr_SetString(PyExc_TypeError, _("provided value is not a valid snapshot identifier."));
        return NULL;
    }

    client = G_ANALYST_CLIENT(pygobject_get(self));

    status = g_analyst_client_set_snapshot_desc(client, &id, text);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = client à manipuler.                                   *
*                args = arguments d'appel à consulter.                        *
*                                                                             *
*  Description : Restaure un ancien instantané.                               *
*                                                                             *
*  Retour      : True si la commande a bien été envoyée, False sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_analyst_client_restore_snapshot(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    const char *raw_id;                     /* Identifiant brut            */
    int ret;                                /* Bilan de lecture des args.  */
    snapshot_id_t id;                       /* Identifiant utilisable      */
    bool status;                            /* Bilan d'opération           */
    GAnalystClient *client;                 /* Version native du serveur   */

#define ANALYST_CLIENT_RESTORE_SNAPSHOT_METHOD PYTHON_METHOD_DEF            \
(                                                                           \
    restore_snapshot, "$self, id, /",                                       \
    METH_VARARGS, py_analyst_client,                                        \
    "Ask the server for restoring a given snapshot using"                   \
    " its identifier and returns the status of the request transmission."   \
    "\n"                                                                    \
    "A 'snapshot-changed' signal is emitted once the request has been"      \
    " processed with success."                                              \
)

    ret = PyArg_ParseTuple(args, "s", &raw_id);
    if (!ret) return NULL;

    status = init_snapshot_id_from_text(&id, raw_id);
    if (!status)
    {
        PyErr_SetString(PyExc_TypeError, _("provided value is not a valid snapshot identifier."));
        return NULL;
    }

    client = G_ANALYST_CLIENT(pygobject_get(self));

    status = g_analyst_client_restore_snapshot(client, &id);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = client à manipuler.                                   *
*                args = arguments d'appel à consulter.                        *
*                                                                             *
*  Description : Crée un nouvel instantané à partir d'un autre.               *
*                                                                             *
*  Retour      : True si la commande a bien été envoyée, False sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_analyst_client_create_snapshot(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GAnalystClient *client;                 /* Version native du serveur   */
    bool status;                            /* Bilan d'opération           */

#define ANALYST_CLIENT_CREATE_SNAPSHOT_METHOD PYTHON_METHOD_DEF             \
(                                                                           \
    create_snapshot, "$self, /",                                            \
    METH_NOARGS, py_analyst_client,                                         \
    "Ask the server for creating a new snapshot of the current state"       \
    " and returns the status of the request transmission."                  \
    "\n"                                                                    \
    "A 'snapshots-updated' signal is emitted once the request has been"     \
    " processed with success."                                              \
)

    client = G_ANALYST_CLIENT(pygobject_get(self));

    status = g_analyst_client_create_snapshot(client);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = client à manipuler.                                   *
*                args = arguments d'appel à consulter.                        *
*                                                                             *
*  Description : Supprime un ancien instantané.                               *
*                                                                             *
*  Retour      : True si la commande a bien été envoyée, False sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_analyst_client_remove_snapshot(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    const char *raw_id;                     /* Identifiant brut            */
    int rec;                                /* Indicateur de récursivité   */
    int ret;                                /* Bilan de lecture des args.  */
    snapshot_id_t id;                       /* Identifiant utilisable      */
    bool status;                            /* Bilan d'opération           */
    GAnalystClient *client;                 /* Version native du serveur   */

#define ANALYST_CLIENT_REMOVE_SNAPSHOT_METHOD PYTHON_METHOD_DEF             \
(                                                                           \
    remove_snapshot, "$self, id, recursive, /",                             \
    METH_VARARGS, py_analyst_client,                                        \
    "Ask the server for removing a given snapshot using"                    \
    " its identifier and returns the status of the request transmission."   \
    "\n"                                                                    \
    "If this removal has not to be recursive, all children snapshots get"   \
    " reassigned to the parent snapshot of the target."                     \
    "\n"                                                                    \
    "A 'snapshots-updated' signal is emitted once the request has been"     \
    " processed with success."                                              \
)

    ret = PyArg_ParseTuple(args, "sp", &raw_id, &rec);
    if (!ret) return NULL;

    status = init_snapshot_id_from_text(&id, raw_id);
    if (!status)
    {
        PyErr_SetString(PyExc_TypeError, _("provided value is not a valid snapshot identifier."));
        return NULL;
    }

    client = G_ANALYST_CLIENT(pygobject_get(self));

    status = g_analyst_client_remove_snapshot(client, &id, rec);

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
*  Retour      : Liste d'instantanés ou None.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_analyst_client_get_snapshots(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GAnalystClient *client;                 /* Version native du serveur   */
    snapshot_info_t *info;                  /* Liste d'instantanés présents*/
    size_t count;                           /* Taille de cette liste       */
    bool status;                            /* Validité de cet identifiant */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    size_t i;                               /* Boucle de parcours          */
    PyObject *item;                         /* Nouvelle description        */
    char *text;                             /* Valeur textuelle à placer   */
    PyObject *attrib;                       /* Attribut à constituer       */
    int ret;                                /* Bilan d'une mise en place   */
    bool failed;                            /* Détection d'une erreur      */

#define ANALYST_CLIENT_SNAPSHOTS_ATTRIB PYTHON_GET_DEF_FULL                             \
(                                                                                       \
    snapshots, py_analyst_client,                                                       \
    "List of all existing snapshots, provided as a tuple of pychrysalide.StructObject." \
    "\n"                                                                                \
    "Each snapshot is characterised by the following properties :\n"                    \
    "* parent_id : identifier of the parent snapshot;\n"                                \
    "* id : identifier of the snapshot;\n"                                              \
    "* created : timestamp of the creation date;\n"                                     \
    "* name : name of the snapshot, or None;\n"                                         \
    "* desc : description of the snapshot, or None."                                    \
)

    client = G_ANALYST_CLIENT(pygobject_get(self));

    status = g_analyst_client_get_snapshots(client, &info, &count);

    if (status)
    {
        result = PyTuple_New(count);

        base = get_python_py_struct_type();

        failed = false;

        for (i = 0; i < count; i++)
        {
            item = PyObject_CallFunction((PyObject *)base, NULL);
            assert(item != NULL);

            text = snapshot_id_as_string(get_snapshot_info_parent_id(&info[i]));
            attrib = PyUnicode_FromString(text);
            ret = PyDict_SetItemString(item, "parent_id", attrib);
            if (ret != 0) break;

            text = snapshot_id_as_string(get_snapshot_info_id(&info[i]));
            attrib = PyUnicode_FromString(text);
            ret = PyDict_SetItemString(item, "id", attrib);
            if (ret != 0) break;

            attrib = PyLong_FromUnsignedLongLong(get_snapshot_info_created(&info[i]));
            ret = PyDict_SetItemString(item, "created", attrib);
            if (ret != 0) break;

            text = get_snapshot_info_name(&info[i]);

            if (text != NULL)
                attrib = PyUnicode_FromString(text);
            else
            {
                attrib = Py_None;
                Py_INCREF(attrib);
            }

            ret = PyDict_SetItemString(item, "name", attrib);
            if (ret != 0) break;

            text = get_snapshot_info_desc(&info[i]);

            if (text != NULL)
                attrib = PyUnicode_FromString(text);
            else
            {
                attrib = Py_None;
                Py_INCREF(attrib);
            }

            ret = PyDict_SetItemString(item, "desc", attrib);
            if (ret != 0) break;

            PyTuple_SetItem(result, i, item);

        }

        failed = (i < count);

        for (i = 0; i < count; i++)
            exit_snapshot_info(&info[i]);

        free(info);

        if (failed)
            goto on_failure;

    }

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

 on_failure:

    Py_DECREF(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'identifiant de l'instantané courant.               *
*                                                                             *
*  Retour      : Identifiant d'instantané ou None.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_analyst_client_get_current_snapshot(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GAnalystClient *client;                 /* Version native du serveur   */
    snapshot_id_t id;                       /* Identifiant à transmettre   */
    bool status;                            /* Validité de cet identifiant */

#define ANALYST_CLIENT_CURRENT_SNAPSHOT_ATTRIB PYTHON_GETSET_DEF_FULL   \
(                                                                       \
    current_snapshot, py_analyst_client,                                \
    "Identifier of the current snapshot, provided as a string."         \
    "\n"                                                                \
    "The returned value is a cached version of the value stored at"     \
    " server side. Thus, defining a new current snapshot is"            \
    " successful as soon as the request to this server is sent."        \
)

    client = G_ANALYST_CLIENT(pygobject_get(self));

    status = g_analyst_client_get_current_snapshot(client, &id);

    if (status)
        result = PyUnicode_FromString(snapshot_id_as_string(&id));

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
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Définit l'identifiant de l'instantané courant.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_analyst_client_set_current_snapshot(PyObject *self, PyObject *value, void *closure)
{
    int ret;                                /* Bilan d'analyse             */
    void *raw;                              /* Valeur brute d'identifiant  */
    snapshot_id_t id;                       /* Identifiant reconnu         */
    bool status;                            /* Bilan d'une conversion      */
    GAnalystClient *client;                 /* Version native du serveur   */

    ret = PyUnicode_Check(value);
    if (!ret) return -1;

    raw = PyUnicode_DATA(value);

    status = init_snapshot_id_from_text(&id, raw);
    if (!status)
    {
        PyErr_SetString(PyExc_TypeError, _("provided value is not a valid snapshot identifier."));
        return -1;
    }

    client = G_ANALYST_CLIENT(pygobject_get(self));

    status = g_analyst_client_set_current_snapshot(client, &id);
    if (!status)
    {
        PyErr_SetString(PyExc_TypeError, "unable to send the provided snapshot identifier");
        return -1;
    }

    return 0;

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

PyTypeObject *get_python_analyst_client_type(void)
{
    static PyMethodDef py_analyst_client_methods[] = {
        ANALYST_CLIENT_SEND_CONTENT_METHOD,
        ANALYST_CLIENT_SAVE_METHOD,
        ANALYST_CLIENT_SET_LAST_ACTIVE_METHOD,
        ANALYST_CLIENT_SET_SNAPSHOT_NAME_METHOD,
        ANALYST_CLIENT_SET_SNAPSHOT_DESC_METHOD,
        ANALYST_CLIENT_RESTORE_SNAPSHOT_METHOD,
        ANALYST_CLIENT_CREATE_SNAPSHOT_METHOD,
        ANALYST_CLIENT_REMOVE_SNAPSHOT_METHOD,
        { NULL }
    };

    static PyGetSetDef py_analyst_client_getseters[] = {
        ANALYST_CLIENT_SNAPSHOTS_ATTRIB,
        ANALYST_CLIENT_CURRENT_SNAPSHOT_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_analyst_client_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.db.AnalystClient",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = ANALYST_CLIENT_DOC,

        .tp_methods     = py_analyst_client_methods,
        .tp_getset      = py_analyst_client_getseters,

        .tp_init        = py_analyst_client_init,
        .tp_new         = py_analyst_client_new

    };

    return &py_analyst_client_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....db.AnalystClient'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_analyst_client_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'AnalystClient' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_analyst_client_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis.db");

        dict = PyModule_GetDict(module);

        if (!ensure_python_hub_client_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_ANALYST_CLIENT, type))
            return false;

        if (!define_loading_status_hint_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en client analyste.                       *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_analyst_client(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_analyst_client_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to analyst client");
            break;

        case 1:
            *((GAnalystClient **)dst) = G_ANALYST_CLIENT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
