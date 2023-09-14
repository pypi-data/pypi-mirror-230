
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format.c - équivalent Python du fichier "plugins/pe/format.c"
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include "format.h"


#include <pygobject.h>


#include <format/known.h>
#include <plugins/dt.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/content.h>
#include <plugins/pychrysalide/format/executable.h>


#include "constants.h"
#include "translate.h"
#include "../format.h"
#include "../rich.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_pe_format_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_pe_format_init(PyObject *, PyObject *, PyObject *);



/* ------------------------------ DEFINITION DE FORMAT ------------------------------ */


/* Présente l'en-tête MS-DOS du format chargé. */
static PyObject *py_pe_format_get_dos_header(PyObject *, void *);

/* Offre un raccourci vers les répertoires du format PE. */
static PyObject *py_pe_format_get_directories(PyObject *, void *);

/* Présente l'en-tête enrichi du format chargé. */
static PyObject *py_pe_format_get_rich_header(PyObject *, void *);

/* Présente l'empreinte d'un en-tête enrichi du format chargé. */
static PyObject *py_pe_format_get_rich_header_checksum(PyObject *, void *);

/* Présente les identifiants contenues dans l'en-tête enrichi. */
static PyObject *py_pe_format_get_comp_ids(PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
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

static PyObject *py_pe_format_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_pe_format_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_PE_FORMAT, type->tp_name, NULL, NULL, NULL);

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

static int py_pe_format_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GBinContent *content;                   /* Instance GLib du contenu    */
    int ret;                                /* Bilan de lecture des args.  */
    GPeFormat *format;                      /* Création GLib à transmettre */

#define PE_FORMAT_DOC                                                       \
    "The PeFormat class handles executables with a Portable Executable"     \
    " structure.\n"                                                         \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    PeFormat(content)"                                                 \
    "\n"                                                                    \
    "Where content points to data as a pychrysalide.analysis.BinContent"    \
    " instance."

    /* Récupération des paramètres */

    ret = PyArg_ParseTuple(args, "O&", convert_to_binary_content, &content);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    format = G_PE_FORMAT(pygobject_get(self));

    g_known_format_set_content(G_KNOWN_FORMAT(format), content);

    return 0;

}



/* ---------------------------------------------------------------------------------- */
/*                                DEFINITION DE FORMAT                                */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = format en place à consulter.                       *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Présente l'en-tête MS-DOS du format chargé.                  *
*                                                                             *
*  Retour      : Structure Python créée pour l'occasion.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_pe_format_get_dos_header(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GPeFormat *format;                      /* Version GLib du format      */

#define PE_FORMAT_DOS_HEADER_ATTRIB PYTHON_GET_DEF_FULL         \
(                                                               \
    dos_header, py_pe_format,                                   \
    "MS-DOS header of the file format.\n"                       \
    "\n"                                                        \
    "This property is a pychrysalide.StructObject instance."    \
    "\n"                                                        \
    "The provided information is composed of the following"     \
    " properties :\n"                                           \
    "\n"                                                        \
    "* e_magic;\n"                                              \
    "* e_cblp;\n"                                               \
    "* e_cp;\n"                                                 \
    "* e_crlc;\n"                                               \
    "* e_cparhdr;\n"                                            \
    "* e_minalloc;\n"                                           \
    "* e_maxalloc;\n"                                           \
    "* e_ss;\n"                                                 \
    "* e_sp;\n"                                                 \
    "* e_csum;\n"                                               \
    "* e_ip;\n"                                                 \
    "* e_cs;\n"                                                 \
    "* e_lfarlc;\n"                                             \
    "* e_ovno;\n"                                               \
    "* e_res;\n"                                                \
    "* e_oemid;\n"                                              \
    "* e_oeminfo;\n"                                            \
    "* e_res2;\n"                                               \
    "* e_lfanew."                                               \
)

    format = G_PE_FORMAT(pygobject_get(self));

    result = translate_pe_dos_header_to_python(format, g_pe_format_get_dos_header(format));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = format en place à consulter.                       *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Offre un raccourci vers les répertoires du format PE.        *
*                                                                             *
*  Retour      : Structure Python créée pour l'occasion.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_pe_format_get_directories(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GPeFormat *format;                      /* Version GLib du format      */
    size_t count;                           /* Quantité de répertoires     */
    const image_data_directory *directories; /* Répertoires à exporter     */
    size_t i;                               /* Boucle de parcours          */
    PyObject *item;                         /* Elément de tableau          */
    int ret;                                /* Bilan d'une mise en place   */

#define PE_FORMAT_DIRECTORIES_ATTRIB PYTHON_GET_DEF_FULL            \
(                                                                   \
    directories, py_pe_format,                                      \
    "Shortcut to the PE format directories.\n"                      \
    "\n"                                                            \
    "This property is a pychrysalide.StructObject instance and"     \
    " can also be access trough the"                                \
    " *self.nt_headers.data_directory* attribute.\n"                \
    "\n"                                                            \
    "Each returned item is composed of the following properties :\n"\
    "\n"                                                            \
    "* virtual_address;\n"                                          \
    "* size."                                                       \
)

    format = G_PE_FORMAT(pygobject_get(self));

    directories = g_pe_format_get_directories(format, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        item = translate_pe_image_data_directory_to_python(format, directories + i);

        ret = PyTuple_SetItem(result, i, item);

        if (ret != 0)
        {
            Py_DECREF(result);
            result = NULL;
            break;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = format en place à consulter.                       *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Présente l'en-tête enrichi du format chargé.                 *
*                                                                             *
*  Retour      : Tableau de valeurs brutes d'information.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_pe_format_get_rich_header(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GPeFormat *format;                      /* Version GLib du format      */
    size_t count;                           /* Quantité de valeurs obtenues*/
    uint64_t *values;                       /* Valeurs brutes à transcrire */
    size_t i;                               /* Boucle de parcours          */

#define PE_FORMAT_RICH_HEADER_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                           \
    rich_header, py_pe_format,                              \
    "Raw values from the Rich header of the file format.\n" \
    "\n"                                                    \
    "This property is a tuple of 64-bit values or an empty" \
    " tuple if no Rich header exists in the PE file."       \
)

    format = G_PE_FORMAT(pygobject_get(self));

    values = g_pe_format_get_rich_header(format, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
        PyTuple_SetItem(result, i, PyLong_FromUnsignedLongLong(values[i]));

    if (values != NULL)
        free(values);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = format en place à consulter.                       *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Présente l'empreinte d'un en-tête enrichi du format chargé.  *
*                                                                             *
*  Retour      : Valeur de l'empreinte ou None en cas d'erreur.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_pe_format_get_rich_header_checksum(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GPeFormat *format;                      /* Version GLib du format      */
    uint32_t checksum;                      /* Valeur à transcrire         */
    bool status;                            /* Validité de cette valeur    */

#define PE_FORMAT_RICH_HEADER_CHECKSUM_ATTRIB PYTHON_GET_DEF_FULL   \
(                                                                   \
    rich_header_checksum, py_pe_format,                             \
    "Checksum used as XOR value for the Rich header of the file"    \
    " format.\n"                                                    \
    "\n"                                                            \
    "This property is a 32-bit integer value."                      \
)

    format = G_PE_FORMAT(pygobject_get(self));

    status = g_pe_format_get_rich_header_checksum(format, &checksum);

    if (status)
        result = PyLong_FromUnsignedLong(checksum);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = format en place à consulter.                       *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Présente les identifiants contenues dans l'en-tête enrichi.  *
*                                                                             *
*  Retour      : Tableau de valeurs raffinées d'information.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_pe_format_get_comp_ids(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GPeFormat *format;                      /* Version GLib du format      */
    size_t count;                           /* Quantité de valeurs obtenues*/
    comp_id_t *ids;                         /* Valeurs raffinées à émettre */
    size_t i;                               /* Boucle de parcours          */

#define PE_FORMAT_COMP_IDS_ATTRIB PYTHON_GET_DEF_FULL               \
(                                                                   \
    comp_ids, py_pe_format,                                         \
    "Compiler identifiers carried by the Rich header of the file"   \
    " format.\n"                                                    \
    "\n"                                                            \
    "This property is a tuple of"                                   \
    " pychrysalide.StructObject items or an empty tuple if no"      \
    " information is found.\n"                                      \
    "\n"                                                            \
    "Each item contains the the following properties :\n"           \
    "\n"                                                            \
    "* minor_cv;\n"                                                 \
    "* prod_id;\n"                                                  \
    "* count."                                                      \
)

    format = G_PE_FORMAT(pygobject_get(self));

    ids = g_pe_format_get_comp_ids(format, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
        PyTuple_SetItem(result, i, translate_pe_comp_id_to_python(format, &ids[i]));

    if (ids != NULL)
        free(ids);

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

PyTypeObject *get_python_pe_format_type(void)
{
    static PyMethodDef py_pe_format_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_pe_format_getseters[] = {
        PE_FORMAT_DOS_HEADER_ATTRIB,
        PE_FORMAT_DIRECTORIES_ATTRIB,
        PE_FORMAT_RICH_HEADER_ATTRIB,
        PE_FORMAT_RICH_HEADER_CHECKSUM_ATTRIB,
        PE_FORMAT_COMP_IDS_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_pe_format_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.pe.PeFormat",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = PE_FORMAT_DOC,

        .tp_methods     = py_pe_format_methods,
        .tp_getset      = py_pe_format_getseters,

        .tp_init        = py_pe_format_init,
        .tp_new         = py_pe_format_new,

    };

    return &py_pe_format_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.pe.PeFormat'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_pe_format(PyObject *module)
{
    PyTypeObject *type;                     /* Type Python 'PeFormat'      */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_pe_format_type();

    dict = PyModule_GetDict(module);

    if (!ensure_python_executable_format_is_registered())
        return false;

    if (!register_class_for_pygobject(dict, G_TYPE_PE_FORMAT, type))
        return false;

    if (!define_python_pe_format_constants(type))
        return false;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en format PE.                             *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_pe_format(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_pe_format_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to PE format");
            break;

        case 1:
            *((GPeFormat **)dst) = G_PE_FORMAT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
