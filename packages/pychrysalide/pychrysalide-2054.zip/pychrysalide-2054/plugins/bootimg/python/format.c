
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format.c - équivalent Python du fichier "plugins/bootimg/format.c"
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


#include "format.h"


#include <pygobject.h>


#include <i18n.h>
#include <format/known.h>
#include <plugins/dt.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/content.h>
#include <plugins/pychrysalide/format/known.h>


#include "translate.h"
#include "../format.h"



/* Crée un nouvel objet Python de type 'BootImgFormat'. */
static PyObject *py_bootimg_format_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_bootimg_format_init(PyObject *, PyObject *, PyObject *);

/* Fournit l'en-tête Bootimg correspondant au format. */
static PyObject *py_bootimg_format_get_header(PyObject *, void *);

/* Fournit le noyau inclus dans une image de démarrage. */
static PyObject *py_bootimg_format_get_kernel(PyObject *, void *);

/* Fournit le disque en RAM inclus dans une image de démarrage. */
static PyObject *py_bootimg_format_get_ramdisk(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de l'objet à instancier.                         *
*                args = arguments fournis à l'appel.                          *
*                kwds = arguments de type key=val fournis.                    *
*                                                                             *
*  Description : Crée un nouvel objet Python de type 'BootImgFormat'.         *
*                                                                             *
*  Retour      : Instance Python mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bootimg_format_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_bootimg_format_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_BOOTIMG_FORMAT, type->tp_name, NULL, NULL, NULL);

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

static int py_bootimg_format_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GBinContent *content;                   /* Instance GLib du contenu    */
    int ret;                                /* Bilan de lecture des args.  */
    GBootImgFormat *format;                 /* Création GLib à transmettre */

#define BOOTIMG_FORMAT_DOC                                                      \
    "BootImgFormat provides support for Android boot images.\n"                 \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    BootImgFormat(content)"                                                \
    "\n"                                                                        \
    "Where content is the binary content of a file usually named 'boot.img',"   \
    " provided as a pychrysalide.analysis.BinContent instance."

    ret = PyArg_ParseTuple(args, "O&", convert_to_binary_content, &content);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    if (!check_bootimg_format(content))
    {
        PyErr_SetString(PyExc_TypeError, "bad format for an Android boot image");
        return -1;
    }

    format = G_BOOTIMG_FORMAT(pygobject_get(self));

    g_known_format_set_content(G_KNOWN_FORMAT(format), content);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = contenu binaire à manipuler.                       *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'entête Bootimg correspondant au format.            *
*                                                                             *
*  Retour      : Structure Python créée pour l'occasion.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bootimg_format_get_header(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    GBootImgFormat *format;                 /* Version GLib du format      */
    const boot_img_hdr *header;             /* Entête à transcrire         */

#define BOOTING_FORMAT_HEADER_ATTRIB PYTHON_GET_DEF_FULL                        \
(                                                                               \
    header, py_bootimg_format,                                                  \
    "Header of the boot image, as a pychrysalide.StructObject instance.\n"      \
    "\n"                                                                        \
    "All the fields are extracted from the Android *boot_img_hdr* structure:\n" \
    "* magic: the string 'ANDROID!';\n"                                         \
    "* kernel_size: size of the embedded kernel, in bytes;\n"                   \
    "* kernel_addr: physical load address of the kernel;\n"                     \
    "* ramdisk_size: size of the embedded ramdisk, in bytes;\n"                 \
    "* ramdisk_addr: physical load address of the ramdisk;\n"                   \
    "* second_size: size of the second stage bootloader, in bytes;\n"           \
    "* second_addr: physical load address of the second stage bootloader;\n"    \
    "* tags_addr: physical address for kernel tags;\n"                          \
    "* page_size: assumed flash page size;\n"                                   \
    "* header_version: boot image header version;\n"                            \
    "* os_version: OS version;\n"                                               \
    "* name: asciiz product name;\n"                                            \
    "* cmdline: kernel command line parameters;\n"                              \
    "* id: timestamp / checksum / sha1 / etc;\n"                                \
    "* extra_cmdline: extra kernel command line parameters;\n"                  \
    "* recovery_dtbo_size: size of the included recovery DTBO, in bytes;\n"     \
    "* recovery_dtbo_offset: offset in boot image;\n"                           \
    "* header_size: size of boot image header, in bytes.\n"                     \
)

    format = G_BOOTIMG_FORMAT(pygobject_get(self));

    header = g_bootimg_format_get_header(format);

    result = translate_bootimg_header_to_python(header);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le noyau inclus dans une image de démarrage.         *
*                                                                             *
*  Retour      : Nouveau contenu binaire ou NULL en cas d'absence.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bootimg_format_get_kernel(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GBootImgFormat *format;                 /* Version GLib du format      */
    GBinContent *content;                   /* Contenu à transmettre       */

#define BOOTING_FORMAT_KERNEL_ATTRIB PYTHON_GET_DEF_FULL                    \
(                                                                           \
    kernel, py_bootimg_format,                                              \
    "Binary content for the (Linux) kernel contained in the boot image,"    \
    "  provided as a pychrysalide.analysis.BinContent instance, or None."   \
)

    format = G_BOOTIMG_FORMAT(pygobject_get(self));

    content = g_bootimg_format_get_kernel(format);

    if (content == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        g_object_ref_sink(content);
        result = pygobject_new(G_OBJECT(content));
        g_object_unref(content);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le disque en RAM inclus dans une image de démarrage. *
*                                                                             *
*  Retour      : Nouveau contenu binaire ou None en cas d'absence.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bootimg_format_get_ramdisk(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GBootImgFormat *format;                 /* Version GLib du format      */
    GBinContent *content;                   /* Contenu à transmettre       */

#define BOOTING_FORMAT_RAMDISK_ATTRIB PYTHON_GET_DEF_FULL                   \
(                                                                           \
    ramdisk, py_bootimg_format,                                             \
    "Binary content for the ramdisk contained in the boot image,"           \
    "  provided as a pychrysalide.analysis.BinContent instance, or None."   \
)

    format = G_BOOTIMG_FORMAT(pygobject_get(self));

    content = g_bootimg_format_get_ramdisk(format);

    if (content == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        g_object_ref_sink(content);
        result = pygobject_new(G_OBJECT(content));
        g_object_unref(content);
    }

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

PyTypeObject *get_python_bootimg_format_type(void)
{
    static PyMethodDef py_bootimg_format_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_bootimg_format_getseters[] = {
        BOOTING_FORMAT_HEADER_ATTRIB,
        BOOTING_FORMAT_KERNEL_ATTRIB,
        BOOTING_FORMAT_RAMDISK_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_bootimg_format_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.bootimg.BootImgFormat",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = BOOTIMG_FORMAT_DOC,

        .tp_methods     = py_bootimg_format_methods,
        .tp_getset      = py_bootimg_format_getseters,

        .tp_init        = py_bootimg_format_init,
        .tp_new         = py_bootimg_format_new

    };

    return &py_bootimg_format_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format..BootImgFormat'.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_bootimg_format(PyObject *module)
{
    PyTypeObject *type;                     /* Type Python 'BootImgFormat' */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_bootimg_format_type();

    dict = PyModule_GetDict(module);

    if (!ensure_python_known_format_is_registered())
        return false;

    if (!register_class_for_pygobject(dict, G_TYPE_BOOTIMG_FORMAT, type))
        return false;

    return true;

}
