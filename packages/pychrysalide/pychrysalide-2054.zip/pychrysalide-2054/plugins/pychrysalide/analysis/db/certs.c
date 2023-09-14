
/* Chrysalide - Outil d'analyse de fichiers binaires
 * certs.c - équivalent Python du fichier "analysis/db/certs.c"
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


#include "certs.h"


#include <pygobject.h>
#include <string.h>


#include <i18n.h>
#include <analysis/db/certs.h>


#include "../../access.h"
#include "../../helpers.h"



/* Traduit en version native une identité de certificat. */
static bool py_certs_fill_x509_entries(PyObject *, x509_entries *);

/* Crée un certificat de signature racine. */
static PyObject *py_certs_build_keys_and_ca(PyObject *, PyObject *);

/* Crée un certificat pour application. */
static PyObject *py_certs_build_keys_and_request(PyObject *, PyObject *);

/* Signe un certificat pour application. */
static PyObject *py_certs_sign_cert(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : dict = ensemble de propriétés renseignées.                   *
*                out  = résumé des entrées regroupées. [OUT]                  *
*                                                                             *
*  Description : Traduit en version native une identité de certificat.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_certs_fill_x509_entries(PyObject *dict, x509_entries *out)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *value;                        /* Valeur au format Python     */

#define TRANSLATE_ENTRY(name, dest)                                                             \
    do                                                                                          \
    {                                                                                           \
        value = PyDict_GetItemString(dict, name);                                               \
        if (value != NULL)                                                                      \
        {                                                                                       \
            result = PyUnicode_Check(value);                                                    \
            if (result)                                                                         \
                out->dest = strdup(PyUnicode_DATA(value));                                      \
            else                                                                                \
                PyErr_Format(PyExc_TypeError, _("The %s property must be a string."), name);    \
        }                                                                                       \
    }                                                                                           \
    while (0)

    result = true;

    memset(out, 0, sizeof(x509_entries));

    TRANSLATE_ENTRY("C", country);

    if (result)
        TRANSLATE_ENTRY("ST", state);

    if (result)
        TRANSLATE_ENTRY("L", locality);

    if (result)
        TRANSLATE_ENTRY("O", organisation);

    if (result)
        TRANSLATE_ENTRY("OU", organisational_unit);

    if (result)
        TRANSLATE_ENTRY("CN", common_name);

    if (!result)
        free_x509_entries(out);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = paramètres à transmettre à l'appel natif.             *
*                                                                             *
*  Description : Crée un certificat de signature racine.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_certs_build_keys_and_ca(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Désignation à retourner     */
    const char *dir;                        /* Répertoire de sortie        */
    const char *label;                      /* Nom principal du certificat */
    unsigned long valid;                    /* Durée de validité en sec.   */
    PyObject *dict;                         /* Détails identitaires        */
    int ret;                                /* Bilan de lecture des args.  */
    x509_entries entries;                   /* Définition d'une identité   */
    bool status;                            /* Bilan d'une constitution    */

    ret = PyArg_ParseTuple(args, "sskO!", &dir, &label, &valid, &PyDict_Type, &dict);
    if (!ret) return NULL;

    status = py_certs_fill_x509_entries(dict, &entries);
    if (!status) return NULL;

    status = build_keys_and_ca(dir, label, valid, &entries);

    free_x509_entries(&entries);

    result = status ? Py_True : Py_False;

    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = paramètres à transmettre à l'appel natif.             *
*                                                                             *
*  Description : Crée un certificat pour application.                         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_certs_build_keys_and_request(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Désignation à retourner     */
    const char *dir;                        /* Répertoire de sortie        */
    const char *label;                      /* Nom principal du certificat */
    PyObject *dict;                         /* Détails identitaires        */
    int ret;                                /* Bilan de lecture des args.  */
    x509_entries entries;                   /* Définition d'une identité   */
    bool status;                            /* Bilan d'une constitution    */

    ret = PyArg_ParseTuple(args, "ssO!", &dir, &label, &PyDict_Type, &dict);
    if (!ret) return NULL;

    status = py_certs_fill_x509_entries(dict, &entries);
    if (!status) return NULL;

    status = build_keys_and_request(dir, label, &entries);

    free_x509_entries(&entries);

    result = status ? Py_True : Py_False;

    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = paramètres à transmettre à l'appel natif.             *
*                                                                             *
*  Description : Signe un certificat pour application.                        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_certs_sign_cert(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Désignation à retourner     */
    const char *csr;                        /* Requête à satisfaire        */
    const char *cacert;                     /* Certificat de confiance     */
    const char *cakey;                      /* Clef de ce certificat       */
    const char *cert;                       /* Certificat en sortie        */
    unsigned long valid;                    /* Durée de validité en sec.   */
    int ret;                                /* Bilan de lecture des args.  */
    bool status;                            /* Bilan de l'opération        */

    ret = PyArg_ParseTuple(args, "ssssk", &csr, &cacert, &cakey, &cert, &valid);
    if (!ret) return NULL;

    status = sign_cert(csr, cacert, cakey, cert, valid);

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

PyTypeObject *get_python_certs_type(void)
{
    static PyMethodDef py_certs_methods[] = {

        { "build_keys_and_ca", py_certs_build_keys_and_ca,
          METH_VARARGS | METH_STATIC,
          "build_keys_and_ca(dir, label, valid, entries, /)\n--\n\nCreate a certificate authority."
        },
        { "build_keys_and_request", py_certs_build_keys_and_request,
          METH_VARARGS | METH_STATIC,
          "build_keys_and_request(dir, label, entries, /)\n--\n\nCreate a certificate sign request."
        },
        { "sign_cert", py_certs_sign_cert,
          METH_VARARGS | METH_STATIC,
          "sign_cert(csr, cacert, cakey, cert, valid, /)\n--\n\nSign a certificate sign request."
        },
        { NULL }

    };

    static PyGetSetDef py_certs_getseters[] = {

        { NULL }

    };

    static PyTypeObject py_certs_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.db.certs",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "PyChrysalide support for DataBase certicates",

        .tp_methods     = py_certs_methods,
        .tp_getset      = py_certs_getseters,

        .tp_new         = no_python_constructor_allowed,

    };

    return &py_certs_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide....db.certs'.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_certs_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python pour 'certs'    */
    PyObject *module;                       /* Module à recompléter        */

    type = get_python_certs_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        if (PyType_Ready(type) != 0)
            return false;

        module = get_access_to_python_module("pychrysalide.analysis.db");

        if (!register_python_module_object(module, type))
            return false;

    }

    return true;

}
