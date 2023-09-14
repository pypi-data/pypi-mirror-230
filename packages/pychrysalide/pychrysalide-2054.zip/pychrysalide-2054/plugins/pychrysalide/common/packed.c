
/* Chrysalide - Outil d'analyse de fichiers binaires
 * packed.c - équivalent Python du fichier "common/packed.c"
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#include "packed.h"


#include <assert.h>


#include "../access.h"
#include "../helpers.h"



/* Rassemblement de données d'un paquet */
typedef struct _py_packed_buffer_t
{
    PyObject_HEAD                           /* A laisser en premier        */

    packed_buffer_t *native;                /* Tampon de données lié       */

} py_packed_buffer_t;


/* Libère de la mémoire un objet Python 'py_packed_buffer_t'. */
static void py_packed_buffer_dealloc(py_packed_buffer_t *);

/* Initialise un objet Python de type 'py_packed_buffer_t'. */
static int py_packed_buffer_init(py_packed_buffer_t *, PyObject *, PyObject *);

/* Rembobine le paquet de données à son départ. */
static PyObject *py_packed_buffer_rewind(PyObject *, PyObject *);

/* Ajoute des données à un paquet en amont à un envoi. */
static PyObject *py_packed_buffer_extend(PyObject *, PyObject *);

/* Récupère des données depuis un paquet après une réception. */
static PyObject *py_packed_buffer_peek(PyObject *, PyObject *);

/* Avance la tête de lecture dans les données d'un paquet. */
static PyObject *py_packed_buffer_advance(PyObject *, PyObject *);

/* Récupère des données depuis un paquet après une réception. */
static PyObject *py_packed_buffer_extract(PyObject *, PyObject *);

/* Indique le nombre d'octets de la charge utile d'un paquet. */
static PyObject *py_packed_buffer_get_payload_length(PyObject *, void *);

/* Détermine si des données sont disponibles en lecture. */
static PyObject *py_packed_buffer_has_more_data(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = tampon de données à supprimer.                        *
*                                                                             *
*  Description : Libère de la mémoire un objet Python 'py_packed_buffer_t'.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_packed_buffer_dealloc(py_packed_buffer_t *self)
{
    exit_packed_buffer(self->native);

    Py_TYPE(self)->tp_free((PyObject *)self);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance d'objet à initialiser.                       *
*                args = arguments passés pour l'appel.                        *
*                kwds = mots clefs éventuellement fournis en complément.      *
*                                                                             *
*  Description : Initialise un objet Python de type 'py_packed_buffer_t'.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_packed_buffer_init(py_packed_buffer_t *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à retourner           */

#define PACKED_BUFFER_DOC                                               \
    "The PackedBuffer object is mainly used as helper for the storage"  \
    " of GLib objects over the network or into files.\n"                \
    "\n"                                                                \
    "The same kind of features as the Python *struct* module are"       \
    " provided to store and retrieve data.\n"                           \
    "\n"                                                                \
    "Instances can be created using the following constructor:\n"       \
    "\n"                                                                \
    "    PackedBuffer()"

    self->native = malloc(sizeof(packed_buffer_t));

    init_packed_buffer(self->native);

    result = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = tampon de données à consulter.                        *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Rembobine le paquet de données à son départ.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_packed_buffer_rewind(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à faire remonter      */
    py_packed_buffer_t *pybuf;              /* Instance à manipuler        */

#define PACKED_BUFFER_REWIND_METHOD PYTHON_METHOD_DEF           \
(                                                               \
    rewind, "$self, /",                                         \
    METH_NOARGS, py_packed_buffer,                              \
    "Rewind the reader head to the beginning of the buffer."    \
)

    pybuf = (py_packed_buffer_t *)self;

    rewind_packed_buffer(pybuf->native);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = tampon de données à consulter.                        *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Ajoute des données à un paquet en amont à un envoi.          *
*                                                                             *
*  Retour      : True.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_packed_buffer_extend(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à faire remonter      */
    const char *data;                       /* Données à intégrer          */
    Py_ssize_t length;                      /* Taille des données contenues*/
    int ntoh;                               /* Conversion à réaliser ?     */
    int ret;                                /* Bilan de lecture des args.  */
    py_packed_buffer_t *pybuf;              /* Instance à manipuler        */
    bool status;                            /* Bilan de l'opération        */

#define PACKED_BUFFER_EXTEND_METHOD PYTHON_METHOD_DEF               \
(                                                                   \
    extend, "$self, data, /, ntoh=False",                           \
    METH_VARARGS, py_packed_buffer,                                 \
    "Append data to a buffer.\n"                                    \
    "\n"                                                            \
    "The data must be bytes. The *ntoh* parameter forces the data"  \
    " to be converted from the network order to the host order.\n"  \
    "\n"                                                            \
    "This conversion is only relevant for 2, 4 and 8 bytes"         \
    " quantities.\n"                                                \
    "\n"                                                            \
    "The method returns True if the operation succeeded."           \
)

    ntoh = 0;

    ret = PyArg_ParseTuple(args, "s#|p", &data, &length, &ntoh);
    if (!ret) return NULL;

    pybuf = (py_packed_buffer_t *)self;

    status = extend_packed_buffer(pybuf->native, data, length, ntoh);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = tampon de données à consulter.                        *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Récupère des données depuis un paquet après une réception.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_packed_buffer_peek(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à faire remonter      */
    int len;                                /* Ampleur de progression      */
    int ntoh;                               /* Conversion à réaliser ?     */
    int ret;                                /* Bilan de lecture des args.  */
    py_packed_buffer_t *pybuf;              /* Instance à manipuler        */
    void *data;                             /* Données obtenues            */
    bool status;                            /* Bilan de l'opération        */

#define PACKED_BUFFER_PEEK_METHOD PYTHON_METHOD_DEF                 \
(                                                                   \
    peek, "$self, len, /, ntoh=False",                              \
    METH_VARARGS, py_packed_buffer,                                 \
    "Extract data from a buffer. The reader head remains untouched" \
    " during the operation.\n"                                      \
    "\n"                                                            \
    "The *len* argument defines the quantity of data to retrieve"   \
    " and the *ntoh* parameter forces the data to be converted"     \
    " from the network order to the host order.\n"                  \
    "\n"                                                            \
    "This conversion is only relevant for 2, 4 and 8 bytes"         \
    " quantities.\n"                                                \
    "\n"                                                            \
    "The method returns data as bytes or None in case of error."    \
)

    ntoh = 0;

    ret = PyArg_ParseTuple(args, "n|p", &len, &ntoh);
    if (!ret) return NULL;

    result = NULL;

    data = malloc(len);

    if (data != NULL)
    {
        pybuf = (py_packed_buffer_t *)self;

        status = peek_packed_buffer(pybuf->native, data, len, ntoh);

        if (status)
            result = PyBytes_FromStringAndSize(data, len);

        free(data);

    }

    if (result == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = tampon de données à consulter.                        *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Avance la tête de lecture dans les données d'un paquet.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_packed_buffer_advance(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à faire remonter      */
    int len;                                /* Ampleur de progression      */
    int ret;                                /* Bilan de lecture des args.  */
    py_packed_buffer_t *pybuf;              /* Instance à manipuler        */

#define PACKED_BUFFER_ADVANCE_METHOD PYTHON_METHOD_DEF          \
(                                                               \
    advance, "$self, len, /",                                   \
    METH_VARARGS, py_packed_buffer,                             \
    "Advance the reader head inside the buffer.\n"              \
    "\n"                                                        \
    "The *len* argument defines the quantity of data to skip."  \
)

    ret = PyArg_ParseTuple(args, "n", &len);
    if (!ret) return NULL;

    pybuf = (py_packed_buffer_t *)self;

    advance_packed_buffer(pybuf->native, len);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = tampon de données à consulter.                        *
*                args = arguments fournis pour la conduite de l'opération.    *
*                                                                             *
*  Description : Récupère des données depuis un paquet après une réception.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_packed_buffer_extract(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à faire remonter      */
    int len;                                /* Ampleur de progression      */
    int ntoh;                               /* Conversion à réaliser ?     */
    int ret;                                /* Bilan de lecture des args.  */
    py_packed_buffer_t *pybuf;              /* Instance à manipuler        */
    void *data;                             /* Données obtenues            */
    bool status;                            /* Bilan de l'opération        */

#define PACKED_BUFFER_EXTRACT_METHOD PYTHON_METHOD_DEF              \
(                                                                   \
    extract, "$self, len, /, ntoh=False",                           \
    METH_VARARGS, py_packed_buffer,                                 \
    "Extract data from a buffer.\n"                                 \
    "\n"                                                            \
    "The *len* argument defines the quantity of data to retrieve"   \
    " and the *ntoh* parameter forces the data to be converted"     \
    " from the network order to the host order.\n"                  \
    "\n"                                                            \
    "This conversion is only relevant for 2, 4 and 8 bytes"         \
    " quantities.\n"                                                \
    "\n"                                                            \
    "The method returns data as bytes or None in case of error."    \
)

    ntoh = 0;

    ret = PyArg_ParseTuple(args, "n|p", &len, &ntoh);
    if (!ret) return NULL;

    result = NULL;

    data = malloc(len);

    if (data != NULL)
    {
        pybuf = (py_packed_buffer_t *)self;

        status = extract_packed_buffer(pybuf->native, data, len, ntoh);

        if (status)
            result = PyBytes_FromStringAndSize(data, len);

        free(data);

    }

    if (result == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un tampon de données.          *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Indique le nombre d'octets de la charge utile d'un paquet.   *
*                                                                             *
*  Retour      : Quantité de données utiles.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_packed_buffer_get_payload_length(PyObject *self, void *closure)
{
    PyObject *result;                       /* Conversion à retourner      */
    py_packed_buffer_t *pybuf;              /* Instance à manipuler        */
    size_t length;                          /* Quantité de données portées */

#define PACKED_BUFFER_PAYLOAD_LENGTH_ATTRIB PYTHON_GET_DEF_FULL \
(                                                               \
    payload_length, py_packed_buffer,                           \
    "Size of the full data carried by the buffer."              \
)

    pybuf = (py_packed_buffer_t *)self;

    length = get_packed_buffer_payload_length(pybuf->native);

    result = PyLong_FromSize_t(length);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un tampon de données.          *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Détermine si des données sont disponibles en lecture.        *
*                                                                             *
*  Retour      : True si des données peuvent être dépilées, False sinon.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_packed_buffer_has_more_data(PyObject *self, void *closure)
{
    PyObject *result;                       /* Conversion à retourner      */
    py_packed_buffer_t *pybuf;              /* Instance à manipuler        */
    bool status;                            /* Bilan de la consultation    */

#define PACKED_BUFFER_HAS_MORE_DATA_ATTRIB PYTHON_HAS_DEF_FULL  \
(                                                               \
    more_data, py_packed_buffer,                                \
    "Tell if the buffer has more data for further reading."     \
)

    pybuf = (py_packed_buffer_t *)self;

    status = has_more_data_in_packed_buffer(pybuf->native);

    result = status ? Py_True : Py_False;
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

PyTypeObject *get_python_packed_buffer_type(void)
{
    static PyMethodDef py_packed_buffer_methods[] = {
        PACKED_BUFFER_REWIND_METHOD,
        PACKED_BUFFER_EXTEND_METHOD,
        PACKED_BUFFER_PEEK_METHOD,
        PACKED_BUFFER_ADVANCE_METHOD,
        PACKED_BUFFER_EXTRACT_METHOD,
        { NULL }
    };

    static PyGetSetDef py_packed_buffer_getseters[] = {
        PACKED_BUFFER_PAYLOAD_LENGTH_ATTRIB,
        PACKED_BUFFER_HAS_MORE_DATA_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_packed_buffer_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.common.PackedBuffer",
        .tp_basicsize   = sizeof(py_packed_buffer_t),

        .tp_dealloc     = (destructor)py_packed_buffer_dealloc,

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = PACKED_BUFFER_DOC,

        .tp_methods     = py_packed_buffer_methods,
        .tp_getset      = py_packed_buffer_getseters,

        .tp_init        = (initproc)py_packed_buffer_init,
        .tp_new         = PyType_GenericNew,

    };

    return &py_packed_buffer_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.common.PackedBuffer'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_packed_buffer_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'PackedBuffer'  */
    PyObject *module;                       /* Module à recompléter        */

    type = get_python_packed_buffer_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        if (PyType_Ready(type) != 0)
            return false;

        module = get_access_to_python_module("pychrysalide.common");

        if (!register_python_module_object(module, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pbuf = structure interne à copier en objet Python.           *
*                                                                             *
*  Description : Convertit une structure 'packed_buffer_t' en objet Python.   *
*                                                                             *
*  Retour      : Object Python résultant de la conversion opérée.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *build_from_internal_packed_buffer(const packed_buffer_t *pbuf)
{
    PyObject *result;                       /* Instance à retourner        */
    PyTypeObject *type;                     /* Type à instancier           */

    type = get_python_packed_buffer_type();

    result = PyObject_CallObject((PyObject *)type, NULL);

    copy_packed_buffer(((py_packed_buffer_t *)result)->native, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en tampon de données.                     *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_packed_buffer(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_packed_buffer_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to packed buffer");
            break;

        case 1:
            *((packed_buffer_t **)dst) = ((py_packed_buffer_t *)arg)->native;
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
