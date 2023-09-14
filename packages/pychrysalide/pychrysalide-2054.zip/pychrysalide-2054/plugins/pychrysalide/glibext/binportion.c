
/* Chrysalide - Outil d'analyse de fichiers binaires
 * binportion.c - équivalent Python du fichier "glibext/gbinportion.c"
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


#include "binportion.h"


#include <pygobject.h>


#include <i18n.h>
#include <glibext/gbinportion-int.h>
#include <plugins/dt.h>


#include "constants.h"
#include "../access.h"
#include "../helpers.h"
#include "../arch/vmpa.h"



/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_bin_portion_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_bin_portion_init(PyObject *, PyObject *, PyObject *);

/* Effectue une comparaison avec un objet Python 'BinPortion'. */
static PyObject *py_binary_portion_richcompare(PyObject *, PyObject *, int);

/* Assure qu'une portion ne dépasse pas une position donnée. */
static PyObject *py_binary_portion_limit_range(PyObject *, PyObject *);

/* Fournit la description attribuée à une partie de code. */
static PyObject *py_binary_portion_get_desc(PyObject *, void *);

/* Attribue une description humaine à une partie de code. */
static int py_binary_portion_set_desc(PyObject *, PyObject *, void *);

/* Fournit l'emplacement d'une partie de code binaire. */
static PyObject *py_binary_portion_get_range(PyObject *, void *);

/* Indique la nature de la portion en terme d'originalité. */
static PyObject *py_binary_portion_get_continuation(PyObject *, void *);

/* Définit la nature de la portion en terme d'originalité. */
static int py_binary_portion_set_continuation(PyObject *, PyObject *, void *);

/* Fournit les droits associés à une partie de code. */
static PyObject *py_binary_portion_get_rights(PyObject *, void *);

/* Définit les droits associés à une partie de code. */
static int py_binary_portion_set_rights(PyObject *, PyObject *, void *);



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

static PyObject *py_bin_portion_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_binary_portion_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_BIN_PORTION, type->tp_name, NULL, NULL, NULL);

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

static int py_bin_portion_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    const char *code;                       /* Identifiant de couleur      */
    vmpa2t *addr;                           /* Emplacement de portion      */
    unsigned long long size;                /* Taille de la portion        */
    int ret;                                /* Bilan de lecture des args.  */
    GBinPortion *portion;                   /* Portion à manipuler         */

    static char *kwlist[] = { "code", "addr", "size", NULL };

#define BINARY_PORTION_DOC                                                      \
    "The BinPortion object handles parts of binaries usually formally"          \
    " identified in binary formats, like program segments or sections for ELF"  \
    " files for example.\n"                                                     \
    "\n"                                                                        \
    "Instances can be created using the following constructor:\n"               \
    "\n"                                                                        \
    "    BinPortion(code, addr, size)"                                          \
    "\n"                                                                        \
    "Where code is the CSS class style for the rendering color to use, addr is" \
    " the starting point of the portion in memory, as a pychrysalide.arch.vmpa" \
    " value, and size is the size of the portion."                              \

    /* Récupération des paramètres */

    ret = PyArg_ParseTupleAndKeywords(args, kwds, "sO&K", kwlist,
                                      &code, convert_any_to_vmpa, &addr, &size);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1)
    {
        clean_vmpa_arg(addr);
        return -1;
    }

    /* Eléments de base */

    portion = G_BIN_PORTION(pygobject_get(self));

    portion->code = strdup(code);

    init_mrange(&portion->range, addr, size);

    clean_vmpa_arg(addr);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a  = premier object Python à consulter.                      *
*                b  = second object Python à consulter.                       *
*                op = type de comparaison menée.                              *
*                                                                             *
*  Description : Effectue une comparaison avec un objet Python 'BinPortion'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_portion_richcompare(PyObject *a, PyObject *b, int op)
{
    PyObject *result;                       /* Bilan à retourner           */
    int ret;                                /* Bilan de lecture des args.  */
    const GBinPortion *portion_a;           /* Premier élément à traiter   */
    const GBinPortion *portion_b;           /* Second élément à traiter    */
    int status;                             /* Résultat d'une comparaison  */

    ret = PyObject_IsInstance(b, (PyObject *)get_python_binary_portion_type());
    if (!ret)
    {
        result = Py_NotImplemented;
        goto cmp_done;
    }

    portion_a = G_BIN_PORTION(pygobject_get(a));
    portion_b = G_BIN_PORTION(pygobject_get(b));

    status = g_binary_portion_compare(&portion_a, &portion_b);

    result = status_to_rich_cmp_state(status, op);

 cmp_done:

    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant une portion de binaire.           *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Assure qu'une portion ne dépasse pas une position donnée.    *
*                                                                             *
*  Retour      : True si la portion a été modifiée, False sinon.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_portion_limit_range(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    unsigned long long max;                 /* Taille maximale à accorder  */
    int ret;                                /* Bilan de lecture des args.  */
    GBinPortion *portion;                   /* Version GLib du type        */
    bool status;                            /* Bilan de la modification    */

#define BINARY_SYMBOL_LIMIT_RANGE_METHOD PYTHON_METHOD_DEF          \
(                                                                   \
    limit_range, "$self, max, /",                                   \
    METH_VARARGS, py_binary_portion,                                \
    "Ensure the portion range does not cross a boundary size.\n"    \
    "\n"                                                            \
    "An integer value is expected as the maximum size of the"       \
    " portion.\n"                                                   \
    "\n"                                                            \
    "A boolean value indicating the success of the operation is"    \
    " returned."                                                    \
)

    ret = PyArg_ParseTuple(args, "K", &max);
    if (!ret) return NULL;

    portion = G_BIN_PORTION(pygobject_get(self));

    status = g_binary_portion_limit_range(portion, max);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant une portion de binaire.           *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Procède à l'inclusion d'une portion dans une autre.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_portion_include(PyObject *self, PyObject *args)
{
    GBinPortion *sub;                       /* Sous-portion à inclure      */
    int ret;                                /* Bilan de lecture des args.  */
    GBinPortion *portion;                   /* Version GLib du type        */

#define BINARY_SYMBOL_INCLUDE_METHOD PYTHON_METHOD_DEF              \
(                                                                   \
    include, "$self, sub, /",                                       \
    METH_VARARGS, py_binary_portion,                                \
    "Include another binary portion as a child item.\n"             \
    "\n"                                                            \
    "The sub portion has to be a pychrysalide.glibext.BinPortion"   \
    " instance."                                                    \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_binary_portion, &sub);
    if (!ret) return NULL;

    portion = G_BIN_PORTION(pygobject_get(self));

    g_object_ref(G_OBJECT(sub));
    g_binary_portion_include(portion, sub);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la description attribuée à une partie de code.       *
*                                                                             *
*  Retour      : Nom donné à la partie.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_portion_get_desc(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GBinPortion *portion;                   /* Version GLib du type        */
    const char *desc;                       /* Description récupérée       */

#define BINARY_PORTION_DESC_ATTRIB PYTHON_GETSET_DEF_FULL   \
(                                                           \
    desc, py_binary_portion,                                \
    "Human description for the binary portion, as a"        \
    " simple string."                                       \
)

    portion = G_BIN_PORTION(pygobject_get(self));

    desc = g_binary_portion_get_desc(portion);

    result = PyUnicode_FromString(desc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Attribue une description humaine à une partie de code.       *
*                                                                             *
*  Retour      : 0.                                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_portion_set_desc(PyObject *self, PyObject *value, void *closure)
{
    GBinPortion *portion;                   /* Version GLib du type        */
    const char *desc;                       /* Description à définir       */

    if (!PyUnicode_Check(value))
    {
        PyErr_SetString(PyExc_TypeError, _("The attribute value must be a string."));
        return -1;
    }

    portion = G_BIN_PORTION(pygobject_get(self));

    desc = PyUnicode_DATA(value);

    g_binary_portion_set_desc(portion, desc);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit l'emplacement d'une partie de code binaire.          *
*                                                                             *
*  Retour      : Espace de couverture associé à la portion.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_portion_get_range(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GBinPortion *portion;                   /* Version GLib du type        */
    const mrange_t *range;                  /* Espace de couverture        */

#define BINARY_PORTION_RANGE_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                           \
    range, py_binary_portion,                               \
    "Area covered by the binary portion.\n"                 \
    "\n"                                                    \
    "This property is a pychrysalide.arch.mrange instance." \
)

    portion = G_BIN_PORTION(pygobject_get(self));

    range = g_binary_portion_get_range(portion);

    result = build_from_internal_mrange(range);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique la nature de la portion en terme d'originalité.      *
*                                                                             *
*  Retour      : True si la portion est la suite d'une portion découpée.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_portion_get_continuation(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GBinPortion *portion;                   /* Version GLib du type        */
    bool status;                            /* Bilan d'une consultation    */

#define BINARY_PORTION_CONTINUATION_ATTRIB PYTHON_GETSET_DEF_FULL   \
(                                                                   \
    continuation, py_binary_portion,                                \
    "Tell if the current portion is a continuation of another"      \
    " one.\n"                                                       \
    "\n"                                                            \
    "If a section belongs to several parents, it is cut into"       \
    " several parts when included in the portion tree."             \
)

    portion = G_BIN_PORTION(pygobject_get(self));

    status = g_binary_portion_is_continuation(portion);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit la nature de la portion en terme d'originalité.      *
*                                                                             *
*  Retour      : 0.                                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_portion_set_continuation(PyObject *self, PyObject *value, void *closure)
{
    GBinPortion *portion;                   /* Version GLib du type        */
    bool status;                            /* Valeur à manipuler          */

    if (!PyBool_Check(value))
    {
        PyErr_SetString(PyExc_TypeError, _("The attribute value must be a boolean."));
        return -1;
    }

    portion = G_BIN_PORTION(pygobject_get(self));

    status = (value == Py_True);

    g_binary_portion_mark_as_continued(portion, status);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les droits associés à une partie de code.            *
*                                                                             *
*  Retour      : Droits d'accès de la partie.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_portion_get_rights(PyObject *self, void *closure)
{
    PyObject *result;                       /* Résultat à retourner        */
    GBinPortion *portion;                   /* Version GLib du type        */
    PortionAccessRights rights;             /* Bilan d'une consultation    */

#define BINARY_PORTION_RIGHTS_ATTRIB PYTHON_GETSET_DEF_FULL         \
(                                                                   \
    rights, py_binary_portion,                                      \
    "Access rights declared for the binary portion, as a"           \
    " pychrysalide.glibext.BinPortion.PortionAccessRights value."   \
)

    portion = G_BIN_PORTION(pygobject_get(self));

    rights = g_binary_portion_get_rights(portion);

    result = cast_with_constants_group_from_type(get_python_binary_portion_type(), "PortionAccessRights", rights);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Définit les droits associés à une partie de code.            *
*                                                                             *
*  Retour      : 0.                                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_binary_portion_set_rights(PyObject *self, PyObject *value, void *closure)
{
    GBinPortion *portion;                   /* Version GLib du type        */
    PortionAccessRights rights;             /* Valeur à manipuler          */

    if (convert_to_portion_access_rights(value, &rights) != 1)
        return -1;

    portion = G_BIN_PORTION(pygobject_get(self));

    g_binary_portion_set_rights(portion, rights);

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

PyTypeObject *get_python_binary_portion_type(void)
{
    static PyMethodDef py_binary_portion_methods[] = {
        BINARY_SYMBOL_LIMIT_RANGE_METHOD,
        BINARY_SYMBOL_INCLUDE_METHOD,
        { NULL }
    };

    static PyGetSetDef py_binary_portion_getseters[] = {
        BINARY_PORTION_DESC_ATTRIB,
        BINARY_PORTION_RANGE_ATTRIB,
        BINARY_PORTION_CONTINUATION_ATTRIB,
        BINARY_PORTION_RIGHTS_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_binary_portion_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.BinPortion",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = BINARY_PORTION_DOC,

        .tp_richcompare = py_binary_portion_richcompare,

        .tp_methods     = py_binary_portion_methods,
        .tp_getset      = py_binary_portion_getseters,

        .tp_init        = py_bin_portion_init,
        .tp_new         = py_bin_portion_new,

    };

    return &py_binary_portion_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.glibext.BinPortion'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_binary_portion_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BinPortion'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_binary_portion_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_BIN_PORTION, type))
            return false;

        if (!define_binary_portion_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en portion de binaire.                    *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_binary_portion(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_binary_portion_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to binary portion");
            break;

        case 1:
            *((GBinPortion **)dst) = G_BIN_PORTION(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
