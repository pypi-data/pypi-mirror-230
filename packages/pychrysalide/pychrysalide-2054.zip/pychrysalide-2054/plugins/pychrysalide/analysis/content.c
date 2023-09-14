
/* Chrysalide - Outil d'analyse de fichiers binaires
 * content.c - prototypes pour l'équivalent Python du fichier "analysis/content.c"
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#include "content.h"


#include <assert.h>
#include <malloc.h>
#include <pygobject.h>
#include <string.h>


#include <i18n.h>


#include <analysis/content-int.h>
#include <common/endianness.h>


#include "cattribs.h"
#include "constants.h"
#include "../access.h"
#include "../helpers.h"
#include "../arch/vmpa.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Procède à l'initialisation de l'interface de génération. */
static void py_binary_content_interface_init(GBinContentIface *, gpointer *);

/* Fournit le nom associé au contenu binaire. */
static char *py_binary_content_describe_wrapper(const GBinContent *, bool);

/* Fournit une portion des données représentées. */
static bool py_binary_content_read_raw_wrapper(const GBinContent *, vmpa2t *, phys_t, bin_t *);;

/* Lit un nombre non signé sur un octet. */
static bool py_binary_content_read_u8_wrapper(const GBinContent *, vmpa2t *, uint8_t *);

/* Lit un nombre non signé sur deux octets. */
static bool py_binary_content_read_u16_wrapper(const GBinContent *, vmpa2t *, SourceEndian, uint16_t *);

/* Lit un nombre non signé sur quatre octets. */
static bool py_binary_content_read_u32_wrapper(const GBinContent *, vmpa2t *, SourceEndian, uint32_t *);

/* Lit un nombre non signé sur huit octets. */
static bool py_binary_content_read_u64_wrapper(const GBinContent *, vmpa2t *, SourceEndian, uint64_t *);



/* ------------------------- CONNEXION AVEC L'API DE PYTHON ------------------------- */


/* Fournit le nom associé au contenu binaire. */
static PyObject *py_binary_content_describe(PyObject *, PyObject *);

/* Fournit une portion des données représentées. */
static PyObject *py_binary_content_read_raw(PyObject *, PyObject *);

/* Lit un nombre non signé sur un octet. */
static PyObject *py_binary_content_read_u8(PyObject *, PyObject *);

/* Lit un nombre non signé sur deux octets. */
static PyObject *py_binary_content_read_u16(PyObject *, PyObject *);

/* Lit un nombre non signé sur quatre octets. */
static PyObject *py_binary_content_read_u32(PyObject *, PyObject *);

/* Lit un nombre non signé sur huit octets. */
static PyObject *py_binary_content_read_u64(PyObject *, PyObject *);

/* Associe un ensemble d'attributs au contenu binaire. */
static int py_binary_content_set_attributes(PyObject *, PyObject *, void *);

/* Fournit l'ensemble des attributs associés à un contenu. */
static PyObject *py_binary_content_get_attributes(PyObject *, void *);

/* Donne l'origine d'un contenu binaire. */
static PyObject *py_binary_content_get_root(PyObject *, void *);

/* Fournit une empreinte unique (SHA256) pour les données. */
static PyObject *py_binary_content_get_checksum(PyObject *, void *);

/* Détermine le nombre d'octets lisibles. */
static PyObject *py_binary_content_get_size(PyObject *, void *);

/* Détermine la position initiale d'un contenu. */
static PyObject *py_binary_content_get_start_pos(PyObject *, void *);

/* Détermine la position finale d'un contenu. */
static PyObject *py_binary_content_get_end_pos(PyObject *, void *);

/* Renvoie tout le contenu binaire d'un coup. */
static PyObject *py_binary_content_get_data(PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : iface  = interface GLib à initialiser.                       *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de génération.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_binary_content_interface_init(GBinContentIface *iface, gpointer *unused)
{
#define BINARY_CONTENT_DOC                                                  \
    "The BinContent is an interface which handles access to a given binary" \
    " content.\n"                                                           \
    "\n"                                                                    \
    "All of its implementations are located in the"                         \
    " pychrysalide.analysis.contents module. The main implemantation is"    \
    " the pychrysalide.analysis.contents.FileContent class.\n"              \
    "\n"                                                                    \
    "A typical class declaration for a new implementation looks like:\n"    \
    "\n"                                                                    \
    "    class NewImplem(GObject.Object, BinContent):\n"                    \
    "        ...\n"                                                         \
    "\n"                                                                    \
    "The following methods have to be defined for new implementations:\n"   \
    "* pychrysalide.analysis.BinContent._describe();\n"                     \
    "* pychrysalide.analysis.BinContent._read_raw();\n"                     \
    "* pychrysalide.analysis.BinContent._read_u4();\n"                      \
    "* pychrysalide.analysis.BinContent._read_u8();\n"                      \
    "* pychrysalide.analysis.BinContent._read_u16();\n"                     \
    "* pychrysalide.analysis.BinContent._read_u32();\n"                     \
    "* pychrysalide.analysis.BinContent._read_u64();\n"

    iface->describe = py_binary_content_describe_wrapper;

    iface->read_raw = py_binary_content_read_raw_wrapper;
    iface->read_u8 = py_binary_content_read_u8_wrapper;
    iface->read_u16 = py_binary_content_read_u16_wrapper;
    iface->read_u32 = py_binary_content_read_u32_wrapper;
    iface->read_u64 = py_binary_content_read_u64_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = élément chargé à consulter.                        *
*                full    = précise s'il s'agit d'une version longue ou non.   *
*                                                                             *
*  Description : Fournit le nom associé au contenu binaire.                   *
*                                                                             *
*  Retour      : Nom de fichier avec chemin absolu au besoin.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_binary_content_describe_wrapper(const GBinContent *content, bool full)
{
    char *result;                           /* Description à retourner     */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *full_obj;                     /* Précision sur la longueur   */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Validité d'une conversion   */

#define BINARY_CONTENT_DESCRIBE_WRAPPER PYTHON_WRAPPER_DEF      \
(                                                               \
    _describe, "$self, full",                                   \
    METH_VARARGS,                                               \
    "Abstract method used to build a (full ?) description of"   \
    " the binary content.describe the loaded content.\n"        \
    "\n"                                                        \
    "The description is returned as a string."                  \
)

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_describe"))
    {
        full_obj = full ? Py_True : Py_False;
        Py_INCREF(full_obj);

        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, full_obj);

        pyret = run_python_method(pyobj, "_describe", args);

        if (pyret != NULL)
        {
            ret = PyUnicode_Check(pyret);

            if (ret)
                result = strdup(PyUnicode_AsUTF8(pyret));

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
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                length  = quantité d'octets à lire.                          *
*                out     = réceptacle disponible pour ces données. [OUT]      *
*                                                                             *
*  Description : Fournit une portion des données représentées.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_binary_content_read_raw_wrapper(const GBinContent *content, vmpa2t *addr, phys_t length, bin_t *out)
{
    bool result;                            /* Bilan à remonter            */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *addr_obj;                     /* Position en version Python  */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Validité d'une conversion   */
    const char *data;                       /* Données brutes à copier     */

#define BINARY_CONTENT_READ_RAW_WRAPPER PYTHON_WRAPPER_DEF      \
(                                                               \
    _read_raw, "$self, addr, length",                                   \
    METH_VARARGS,                                               \
    "Abstract method used to provide the bytes read from a given position.\n"   \
    "\n"                                                        \
    "The description is returned as a string."                  \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_read_raw"))
    {
        addr_obj = build_from_internal_vmpa(addr);

        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, addr_obj);
        PyTuple_SetItem(args, 1, PyLong_FromUnsignedLongLong(length));

        pyret = run_python_method(pyobj, "_read_raw", args);

        if (pyret != NULL)
        {
            ret = PyUnicode_Check(pyret);

            if (ret)
            {
                assert((phys_t)PyBytes_Size(pyret) == length);

                if ((phys_t)PyBytes_Size(pyret) == length)
                {
                    /* Avancement de la tête de lecture */

                    copy_vmpa(addr, get_internal_vmpa(addr_obj));

                    /* Récupération des données */

                    data = PyBytes_AsString(pyret);

                    memcpy(out, data, length);

                    /* Bilan à retenir */

                    result = true;

                }

            }

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
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                val     = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Lit un nombre non signé sur un octet.                        *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_binary_content_read_u8_wrapper(const GBinContent *content, vmpa2t *addr, uint8_t *val)
{
    bool result;                            /* Bilan à remonter            */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *addr_obj;                     /* Position en version Python  */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Validité d'une conversion   */

#define BINARY_CONTENT_READ_U8_WRAPPER PYTHON_WRAPPER_DEF               \
(                                                                       \
    _read_u8, "$self, addr",                                            \
    METH_VARARGS,                                                       \
    "Abstract method used to read an unsigned bytes from a given"       \
    " position.\n"                                                      \
    "\n"                                                                \
    "The location of the data to read is a pychrysalide.arch.vmpa"      \
    " instance.\n"                                                      \
    "\n"                                                                \
    "The returned value is the read data or None is case of error."     \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_read_u8"))
    {
        addr_obj = build_from_internal_vmpa(addr);

        args = PyTuple_New(1);
        PyTuple_SetItem(args, 0, addr_obj);

        pyret = run_python_method(pyobj, "_read_u8", args);

        if (pyret != NULL)
        {
            ret = PyLong_Check(pyret);

            if (ret)
            {
                /* Avancement de la tête de lecture */

                copy_vmpa(addr, get_internal_vmpa(addr_obj));

                /* Récupération des données */

                *val = PyLong_AsUnsignedLong(pyret);

                /* Bilan à retenir */

                result = true;

            }

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
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                endian  = ordre des bits dans la source.                     *
*                val     = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Lit un nombre non signé sur deux octets.                     *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_binary_content_read_u16_wrapper(const GBinContent *content, vmpa2t *addr, SourceEndian endian, uint16_t *val)
{
    bool result;                            /* Bilan à remonter            */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *addr_obj;                     /* Position en version Python  */
    PyObject *endianness_obj;               /* Boutisme en version Python  */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Validité d'une conversion   */

#define BINARY_CONTENT_READ_U16_WRAPPER PYTHON_WRAPPER_DEF              \
(                                                                       \
    _read_u16, "$self, addr, endian",                                   \
    METH_VARARGS,                                                       \
    "Abstract method used to read two unsigned bytes from a given"      \
    " position.\n"                                                      \
    "\n"                                                                \
    "The location of the data to read is a pychrysalide.arch.vmpa"      \
    " instance. The endianness of the data can be provided using"       \
    " pychrysalide.analysis.BinContent.SourceEndian values.\n"          \
    "\n"                                                                \
    "The returned value is the read data or None is case of error."     \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_read_u16"))
    {
        addr_obj = build_from_internal_vmpa(addr);
        endianness_obj = cast_with_constants_group_from_type(get_python_binary_content_type(),
                                                             "SourceEndian", endian);

        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, addr_obj);
        PyTuple_SetItem(args, 1, endianness_obj);

        pyret = run_python_method(pyobj, "_read_u16", args);

        if (pyret != NULL)
        {
            ret = PyLong_Check(pyret);

            if (ret)
            {
                /* Avancement de la tête de lecture */

                copy_vmpa(addr, get_internal_vmpa(addr_obj));

                /* Récupération des données */

                *val = PyLong_AsUnsignedLong(pyret);

                /* Bilan à retenir */

                result = true;

            }

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
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                endian  = ordre des bits dans la source.                     *
*                val     = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Lit un nombre non signé sur quatre octets.                   *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_binary_content_read_u32_wrapper(const GBinContent *content, vmpa2t *addr, SourceEndian endian, uint32_t *val)
{
    bool result;                            /* Bilan à remonter            */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *addr_obj;                     /* Position en version Python  */
    PyObject *endianness_obj;               /* Boutisme en version Python  */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Validité d'une conversion   */

#define BINARY_CONTENT_READ_U32_WRAPPER PYTHON_WRAPPER_DEF              \
(                                                                       \
    _read_u32, "$self, addr, endian",                                   \
    METH_VARARGS,                                                       \
    "Abstract method used to read four unsigned bytes from a given"     \
    " position.\n"                                                      \
    "\n"                                                                \
    "The location of the data to read is a pychrysalide.arch.vmpa"      \
    " instance. The endianness of the data can be provided using"       \
    " pychrysalide.analysis.BinContent.SourceEndian values.\n"          \
    "\n"                                                                \
    "The returned value is the read data or None is case of error."     \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_read_u32"))
    {
        addr_obj = build_from_internal_vmpa(addr);
        endianness_obj = cast_with_constants_group_from_type(get_python_binary_content_type(),
                                                             "SourceEndian", endian);

        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, addr_obj);
        PyTuple_SetItem(args, 1, endianness_obj);

        pyret = run_python_method(pyobj, "_read_u32", args);

        if (pyret != NULL)
        {
            ret = PyLong_Check(pyret);

            if (ret)
            {
                /* Avancement de la tête de lecture */

                copy_vmpa(addr, get_internal_vmpa(addr_obj));

                /* Récupération des données */

                *val = PyLong_AsUnsignedLong(pyret);

                /* Bilan à retenir */

                result = true;

            }

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
*  Paramètres  : content = contenu binaire à venir lire.                      *
*                addr    = position de la tête de lecture.                    *
*                endian  = ordre des bits dans la source.                     *
*                val     = lieu d'enregistrement de la lecture. [OUT]         *
*                                                                             *
*  Description : Lit un nombre non signé sur huit octets.                     *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_binary_content_read_u64_wrapper(const GBinContent *content, vmpa2t *addr, SourceEndian endian, uint64_t *val)
{
    bool result;                            /* Bilan à remonter            */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *addr_obj;                     /* Position en version Python  */
    PyObject *endianness_obj;               /* Boutisme en version Python  */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyret;                        /* Bilan de consultation       */
    int ret;                                /* Validité d'une conversion   */

#define BINARY_CONTENT_READ_U64_WRAPPER PYTHON_WRAPPER_DEF              \
(                                                                       \
    _read_u64, "$self, addr, endian",                                   \
    METH_VARARGS,                                                       \
    "Abstract method used to read eight unsigned bytes from a given"    \
    " position.\n"                                                      \
    "\n"                                                                \
    "The location of the data to read is a pychrysalide.arch.vmpa"      \
    " instance. The endianness of the data can be provided using"       \
    " pychrysalide.analysis.BinContent.SourceEndian values.\n"          \
    "\n"                                                                \
    "The returned value is the read data or None is case of error."     \
)

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(content));

    if (has_python_method(pyobj, "_read_u64"))
    {
        addr_obj = build_from_internal_vmpa(addr);
        endianness_obj = cast_with_constants_group_from_type(get_python_binary_content_type(),
                                                             "SourceEndian", endian);

        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, addr_obj);
        PyTuple_SetItem(args, 1, endianness_obj);

        pyret = run_python_method(pyobj, "_read_u64", args);

        if (pyret != NULL)
        {
            ret = PyLong_Check(pyret);

            if (ret)
            {
                /* Avancement de la tête de lecture */

                copy_vmpa(addr, get_internal_vmpa(addr_obj));

                /* Récupération des données */

                *val = PyLong_AsUnsignedLongLong(pyret);

                /* Bilan à retenir */

                result = true;

            }

            Py_DECREF(pyret);

        }

        Py_DECREF(args);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           CONNEXION AVEC L'API DE PYTHON                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = précise s'il s'agit d'une version longue ou non.      *
*                                                                             *
*  Description : Fournit le nom associé au contenu binaire.                   *
*                                                                             *
*  Retour      : Nom de fichier avec chemin absolu au besoin.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_content_describe(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    int full;                               /* Description complète ?      */
    int ret;                                /* Bilan de lecture des args.  */
    GBinContent *content;                   /* Version GLib du format      */
    char *desc;                             /* Description obtenue         */

#define BINARY_CONTENT_DESCRIBE_METHOD PYTHON_METHOD_DEF                \
(                                                                       \
    describe, "$self, /, full=False",                                   \
    METH_VARARGS, py_binary_content,                                    \
    "Get a (full ?) description of the binary content."                 \
)

    full = 0;

    ret = PyArg_ParseTuple(args, "|p", &full);
    if (!ret) return NULL;

    content = G_BIN_CONTENT(pygobject_get(self));

    desc = g_binary_content_describe(content, full);

    result = PyUnicode_FromString(desc);

    free(desc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Fournit une portion des données représentées.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_content_read_raw(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    vmpa2t *addr;                           /* Position interne associée   */
    unsigned long long length;              /* Quantité de données à lire  */
    int ret;                                /* Bilan de lecture des args.  */
    GBinContent *content;                   /* Version GLib du format      */
    const bin_t *val;                       /* Valeur lue à faire suivre   */

#define BINARY_CONTENT_READ_RAW_METHOD PYTHON_METHOD_DEF                \
(                                                                       \
    read_raw, "$self, addr, length, /",                                 \
    METH_VARARGS, py_binary_content,                                    \
    "Read bytes from a given position."                                 \
)

    ret = PyArg_ParseTuple(args, "O&K", convert_any_to_vmpa, &addr, &length);
    if (!ret) return NULL;

    content = G_BIN_CONTENT(pygobject_get(self));

    val = g_binary_content_get_raw_access(content, addr, length);
    if (val == NULL)
    {
        clean_vmpa_arg(addr);

        PyErr_SetString(PyExc_Exception, _("Invalid read access."));
        return NULL;

    }

    result = PyBytes_FromStringAndSize((char *)val, length);

    clean_vmpa_arg(addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Lit un nombre non signé sur un octet.                        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_content_read_u8(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    vmpa2t *addr;                           /* Position interne associée   */
    int ret;                                /* Bilan de lecture des args.  */
    GBinContent *content;                   /* Version GLib du format      */
    uint8_t val;                            /* Valeur lue à faire suivre   */
    bool status;                            /* Bilan de l'opération        */

#define BINARY_CONTENT_READ_U8_METHOD PYTHON_METHOD_DEF                 \
(                                                                       \
    read_u8, "$self, addr, /",                                          \
    METH_VARARGS, py_binary_content,                                    \
    "Read an unsigned byte from a given position."                      \
    "\n"                                                                \
    "The location of the data to read is a pychrysalide.arch.vmpa"      \
    " instance.\n"                                                      \
    "\n"                                                                \
    "The returned value is the read data or None is case of error."     \
)

    ret = PyArg_ParseTuple(args, "O&", convert_any_to_vmpa, &addr);
    if (!ret) return NULL;

    content = G_BIN_CONTENT(pygobject_get(self));

    status = g_binary_content_read_u8(content, addr, &val);
    if (!status)
    {
        clean_vmpa_arg(addr);

        PyErr_SetString(PyExc_Exception, _("Invalid read access."));
        return NULL;

    }

    result = PyLong_FromUnsignedLong(val);

    clean_vmpa_arg(addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Lit un nombre non signé sur deux octets.                     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_content_read_u16(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    vmpa2t *addr;                           /* Position interne associée   */
    unsigned long endianness;               /* Boutisme de la lecture      */
    int ret;                                /* Bilan de lecture des args.  */
    GBinContent *content;                   /* Version GLib du format      */
    uint16_t val;                           /* Valeur lue à faire suivre   */
    bool status;                            /* Bilan de l'opération        */

#define BINARY_CONTENT_READ_U16_METHOD PYTHON_METHOD_DEF                \
(                                                                       \
    read_u16, "$self, addr, endian, /",                                 \
    METH_VARARGS, py_binary_content,                                    \
    "Read two unsigned bytes from a given position."                    \
    "\n"                                                                \
    "The location of the data to read is a pychrysalide.arch.vmpa"      \
    " instance. The endianness of the data can be provided using"       \
    " pychrysalide.analysis.BinContent.SourceEndian values.\n"          \
    "\n"                                                                \
    "The returned value is the read data or None is case of error."     \
)

    ret = PyArg_ParseTuple(args, "O&k", convert_any_to_vmpa, &addr, &endianness);
    if (!ret) return NULL;

    content = G_BIN_CONTENT(pygobject_get(self));

    status = g_binary_content_read_u16(content, addr, endianness, &val);
    if (!status)
    {
        clean_vmpa_arg(addr);

        PyErr_SetString(PyExc_Exception, _("Invalid read access."));
        return NULL;

    }

    result = PyLong_FromUnsignedLong(val);

    clean_vmpa_arg(addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Lit un nombre non signé sur quatre octets.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_content_read_u32(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    vmpa2t *addr;                           /* Position interne associée   */
    unsigned long endianness;               /* Boutisme de la lecture      */
    int ret;                                /* Bilan de lecture des args.  */
    GBinContent *content;                   /* Version GLib du format      */
    uint32_t val;                           /* Valeur lue à faire suivre   */
    bool status;                            /* Bilan de l'opération        */

#define BINARY_CONTENT_READ_U32_METHOD PYTHON_METHOD_DEF                \
(                                                                       \
    read_u32, "$self, addr, endian, /",                                 \
    METH_VARARGS, py_binary_content,                                    \
    "Read four unsigned bytes from a given position."                   \
    "\n"                                                                \
    "The location of the data to read is a pychrysalide.arch.vmpa"      \
    " instance. The endianness of the data can be provided using"       \
    " pychrysalide.analysis.BinContent.SourceEndian values.\n"          \
    "\n"                                                                \
    "The returned value is the read data or None is case of error."     \
)

    ret = PyArg_ParseTuple(args, "O&k", convert_any_to_vmpa, &addr, &endianness);
    if (!ret) return NULL;

    content = G_BIN_CONTENT(pygobject_get(self));

    status = g_binary_content_read_u32(content, addr, endianness, &val);
    if (!status)
    {
        clean_vmpa_arg(addr);

        PyErr_SetString(PyExc_Exception, _("Invalid read access."));
        return NULL;

    }

    result = PyLong_FromUnsignedLong(val);

    clean_vmpa_arg(addr);

    return result;

}

/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Lit un nombre non signé sur huit octets.                     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_content_read_u64(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    vmpa2t *addr;                           /* Position interne associée   */
    unsigned long endianness;               /* Boutisme de la lecture      */
    int ret;                                /* Bilan de lecture des args.  */
    GBinContent *content;                   /* Version GLib du format      */
    uint64_t val;                           /* Valeur lue à faire suivre   */
    bool status;                            /* Bilan de l'opération        */

#define BINARY_CONTENT_READ_U64_METHOD PYTHON_METHOD_DEF                \
(                                                                       \
    read_u64, "$self, addr, endian, /",                                 \
    METH_VARARGS, py_binary_content,                                    \
    "Read eight unsigned bytes from a given position.\n"                \
    "\n"                                                                \
    "The location of the data to read is a pychrysalide.arch.vmpa"      \
    " instance. The endianness of the data can be provided using"       \
    " pychrysalide.analysis.BinContent.SourceEndian values.\n"          \
    "\n"                                                                \
    "The returned value is the read data or None is case of error."     \
)

    ret = PyArg_ParseTuple(args, "O&k", convert_any_to_vmpa, &addr, &endianness);
    if (!ret) return NULL;

    content = G_BIN_CONTENT(pygobject_get(self));

    status = g_binary_content_read_u64(content, addr, endianness, &val);
    if (!status)
    {
        clean_vmpa_arg(addr);

        PyErr_SetString(PyExc_Exception, _("Invalid read access."));
        return NULL;

    }

    result = PyLong_FromUnsignedLongLong(val);

    clean_vmpa_arg(addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = contenu binaire à manipuler.                       *
*                value   = jeu d'attributs à lier au contenu courant.         *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Associe un ensemble d'attributs au contenu binaire.          *
*                                                                             *
*  Retour      : Jeu d'attributs liés au contenu courant.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_content_set_attributes(PyObject *self, PyObject *value, void *closure)
{
    int result;                             /* Bilan à renvoyer            */
    GBinContent *content;                   /* Version GLib du format      */
    GContentAttributes *attribs;            /* Version native des attributs*/

    content = G_BIN_CONTENT(pygobject_get(self));

    if (!convert_to_content_attributes(value, &attribs))
        result = -1;

    else
    {
        g_binary_content_set_attributes(content, attribs);
        result = 0;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = contenu binaire à manipuler.                       *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Fournit l'ensemble des attributs associés à un contenu.      *
*                                                                             *
*  Retour      : Jeu d'attributs liés au contenu courant.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_content_get_attributes(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinContent *content;                   /* Version GLib du format      */
    GContentAttributes *attribs;            /* Attributs à transmettre     */

#define BINARY_CONTENT_ATTRIBUTES_ATTRIB PYTHON_GETSET_DEF_FULL         \
(                                                                       \
    attributes, py_binary_content,                                      \
    "Provide or define the attributes linked to the binary content."    \
)

    content = G_BIN_CONTENT(pygobject_get(self));

    attribs = g_binary_content_get_attributes(content);

    result = pygobject_new(G_OBJECT(attribs));

    g_object_unref(attribs);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = contenu binaire à manipuler.                       *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Donne l'origine d'un contenu binaire.                        *
*                                                                             *
*  Retour      : Contenu à l'origine du contenu courant.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_content_get_root(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinContent *content;                   /* Version GLib du format      */
    GContentAttributes *attribs;            /* Attributs à transmettre     */

#define BINARY_CONTENT_ROOT_ATTRIB PYTHON_GET_DEF_FULL                  \
(                                                                       \
    root, py_binary_content,                                            \
    "Provide, as a pychrysalide.analysis.BinContent instance, the root" \
    " content leading to the current content."                          \
    "\n"                                                                \
    "This property is relevant only for"                                \
    " pychrysalide.analysis.contents.EncapsulatedContent objects."      \
)

    content = G_BIN_CONTENT(pygobject_get(self));

    attribs = g_binary_content_get_attributes(content);

    result = pygobject_new(G_OBJECT(attribs));

    g_object_unref(attribs);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = contenu binaire à manipuler.                       *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Fournit une empreinte unique (SHA256) pour les données.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_content_get_checksum(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinContent *content;                   /* Version GLib du format      */
    const gchar *checksum;                  /* Empreinte fournie           */

#define BINARY_CONTENT_CHECKSUM_ATTRIB PYTHON_GET_DEF_FULL              \
(                                                                       \
    checksum, py_binary_content,                                        \
    "Compute a SHA256 hash as chechsum of handled data."                \
)

    content = G_BIN_CONTENT(pygobject_get(self));

    checksum = g_binary_content_get_checksum(content);

    result = PyUnicode_FromString(checksum);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = contenu binaire à manipuler.                       *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Détermine le nombre d'octets lisibles.                       *
*                                                                             *
*  Retour      : Quantité représentée.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_content_get_size(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinContent *content;                   /* Version GLib du format      */
    phys_t size;                            /* Quantité d'octets dispos.   */

#define BINARY_CONTENT_SIZE_ATTRIB PYTHON_GET_DEF_FULL                  \
(                                                                       \
    size, py_binary_content,                                            \
    "Compute the quantity of readable bytes."                           \
)

    content = G_BIN_CONTENT(pygobject_get(self));

    size = g_binary_content_compute_size(content);

    result = PyLong_FromUnsignedLongLong(size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = contenu binaire à manipuler.                       *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Détermine la position initiale d'un contenu.                 *
*                                                                             *
*  Retour      : Position initiale.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_content_get_start_pos(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinContent *content;                   /* Version GLib du format      */
    vmpa2t pos;                             /* Position à transmettre      */

#define BINARY_CONTENT_START_POS_ATTRIB PYTHON_GET_DEF_FULL             \
(                                                                       \
    start_pos, py_binary_content,                                       \
    "Provide the starting position of the binary content."              \
)

    content = G_BIN_CONTENT(pygobject_get(self));

    g_binary_content_compute_start_pos(content, &pos);

    result = build_from_internal_vmpa(&pos);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = contenu binaire à manipuler.                       *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Détermine la position finale d'un contenu.                   *
*                                                                             *
*  Retour      : Position finale.                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_content_get_end_pos(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinContent *content;                   /* Version GLib du format      */
    vmpa2t pos;                             /* Position à transmettre      */

#define BINARY_CONTENT_END_POS_ATTRIB PYTHON_GET_DEF_FULL               \
(                                                                       \
    end_pos, py_binary_content,                                         \
    "Provide the ending position of the binary content."                \
)

    content = G_BIN_CONTENT(pygobject_get(self));

    g_binary_content_compute_end_pos(content, &pos);

    result = build_from_internal_vmpa(&pos);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = contenu binaire à manipuler.                       *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Renvoie tout le contenu binaire d'un coup.                   *
*                                                                             *
*  Retour      : Ensemble d'octets lus.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_content_get_data(PyObject *self, void *closure)
{
    PyObject *result;                       /* Contenu à retourner         */
    GBinContent *content;                   /* Version GLib du format      */
    vmpa2t start;                           /* Tête de lecture initiale    */
    phys_t length;                          /* Nombre d'octets disponibles */
    const bin_t *val;                       /* Valeur lue à faire suivre   */

#define BINARY_CONTENT_DATA_ATTRIB PYTHON_GET_DEF_FULL                  \
(                                                                       \
    data, py_binary_content,                                            \
    "Provide all the content bytes at once."                            \
)

    content = G_BIN_CONTENT(pygobject_get(self));

    init_vmpa(&start, 0, VMPA_NO_VIRTUAL);

    length = g_binary_content_compute_size(content);

    val = g_binary_content_get_raw_access(content, &start, length);
    assert(val != NULL);

    result = PyBytes_FromStringAndSize((char *)val, length);

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

PyTypeObject *get_python_binary_content_type(void)
{
    static PyMethodDef py_binary_content_methods[] = {
        BINARY_CONTENT_DESCRIBE_WRAPPER,
        BINARY_CONTENT_READ_RAW_WRAPPER,
        BINARY_CONTENT_READ_U8_WRAPPER,
        BINARY_CONTENT_READ_U16_WRAPPER,
        BINARY_CONTENT_READ_U32_WRAPPER,
        BINARY_CONTENT_READ_U64_WRAPPER,
        BINARY_CONTENT_DESCRIBE_METHOD,
        BINARY_CONTENT_READ_RAW_METHOD,
        BINARY_CONTENT_READ_U8_METHOD,
        BINARY_CONTENT_READ_U16_METHOD,
        BINARY_CONTENT_READ_U32_METHOD,
        BINARY_CONTENT_READ_U64_METHOD,
        { NULL }
    };

    static PyGetSetDef py_binary_content_getseters[] = {
        BINARY_CONTENT_ATTRIBUTES_ATTRIB,
        BINARY_CONTENT_ROOT_ATTRIB,
        BINARY_CONTENT_CHECKSUM_ATTRIB,
        BINARY_CONTENT_SIZE_ATTRIB,
        BINARY_CONTENT_START_POS_ATTRIB,
        BINARY_CONTENT_END_POS_ATTRIB,
        BINARY_CONTENT_DATA_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_binary_content_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.BinContent",
        .tp_basicsize   = sizeof(PyObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = BINARY_CONTENT_DOC,

        .tp_methods     = py_binary_content_methods,
        .tp_getset      = py_binary_content_getseters

    };

    return &py_binary_content_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.analysis.BinContent'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_binary_content_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BinContent'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    static GInterfaceInfo info = {          /* Paramètres d'inscription    */

        .interface_init = (GInterfaceInitFunc)py_binary_content_interface_init,
        .interface_finalize = NULL,
        .interface_data = NULL,

    };

    type = get_python_binary_content_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis");

        dict = PyModule_GetDict(module);

        if (!register_interface_for_pygobject(dict, G_TYPE_BIN_CONTENT, type, &info))
            return false;

        if (!define_analysis_content_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en contenu binaire.                       *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_binary_content(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_binary_content_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to binary content");
            break;

        case 1:
            *((GBinContent **)dst) = G_BIN_CONTENT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en contenu binaire ou NULL.               *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_binary_content_or_none(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    if (arg == Py_None)
    {
        *((GBinContent **)dst) = NULL;
        result = 1;
    }

    else
        result = convert_to_binary_content(arg, dst);

    return result;

}
