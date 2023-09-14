
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.c - équivalent Python du fichier "arch/processor.c"
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


#include "processor.h"


#include <malloc.h>
#include <pygobject.h>


#include <i18n.h>
#include <arch/processor-int.h>
#include <plugins/dt.h>


#include "constants.h"
#include "context.h"
#include "instriter.h"
#include "instruction.h"
#include "vmpa.h"
#include "../access.h"
#include "../helpers.h"
#include "../analysis/content.h"
#include "../format/executable.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_arch_processor_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise la classe des descriptions de fichier binaire. */
static void py_arch_processor_init_gclass(GArchProcessorClass *, gpointer);

/* Initialise une instance de processeur d'architecture. */
static void py_arch_processor_init_ginstance(GArchProcessor *, GArchProcessor *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_arch_processor_init(PyObject *, PyObject *, PyObject *);

/* Fournit la désignation interne du processeur d'architecture. */
static char *py_arch_processor_get_key_wrapper(const GArchProcessor *);

/* Fournit le nom humain de l'architecture visée. */
static char *py_arch_processor_get_desc_wrapper(const GArchProcessor *);

/* Fournit la taille de l'espace mémoire d'une architecture. */
static MemoryDataSize py_arch_processor_get_memory_size_wrapper(const GArchProcessor *);

/* Fournit la taille min. des instructions d'une architecture. */
static MemoryDataSize py_arch_processor_get_instruction_min_size_wrapper(const GArchProcessor *);

/* Indique si l'architecture possède un espace virtuel ou non. */
static bool py_arch_processor_has_virtual_space_wrapper(const GArchProcessor *);

/* Fournit un contexte propre au processeur d'une architecture. */
static GProcContext *py_arch_processor_get_context_wrapper(const GArchProcessor *);

/* Désassemble une instruction dans un flux de données. */
static GArchInstruction *py_arch_processor_disassemble_wrapper(const GArchProcessor *, GProcContext *, const GBinContent *, vmpa2t *, GExeFormat *);



/* ---------------------------- DEFINITION DE PROCESSEUR ---------------------------- */


/* Fournit la désignation interne du processeur d'architecture. */
static PyObject *py_arch_processor_get_key(PyObject *, void *);

/* Fournit le nom humain de l'architecture visée. */
static PyObject *py_arch_processor_get_desc(PyObject *, void *);

/* Fournit le boustime du processeur d'une architecture. */
static PyObject *py_arch_processor_get_endianness(PyObject *, void *);

/* Fournit la taille de l'espace mémoire d'une architecture. */
static PyObject *py_arch_processor_get_memory_size(PyObject *, void *);

/* Fournit la taille min. des instructions d'une architecture. */
static PyObject *py_arch_processor_get_ins_min_size(PyObject *, void *);

/* Indique si l'architecture possède un espace virtuel ou non. */
static PyObject *py_arch_processor_has_virtual_space(PyObject *, void *);

/* Fournit un contexte propre au processeur d'une architecture. */
static PyObject *py_arch_processor_get_context(PyObject *, PyObject *);

/* Désassemble une instruction dans un flux de données. */
static PyObject *py_arch_processor_disassemble(PyObject *, PyObject *);



/* ------------------ CONSERVATION DES SOUCIS DURANT LE CHARGEMENT ------------------ */


/* Etend la liste des soucis détectés avec de nouvelles infos. */
static PyObject *py_arch_processor_add_error(PyObject *, PyObject *);

/* Fournit les éléments concernant tous les soucis détectés. */
static PyObject *py_arch_processor_get_errors(PyObject *, void *);



/* ------------------ MANIPULATIONS DES INSTRUCTIONS DESASSEMBLEES ------------------ */


/* Fournit les instructions désassemblées pour une architecture. */
static PyObject *py_arch_processor_get_instrs(PyObject *, void *);

/* Note les instructions désassemblées avec une architecture. */
static int py_arch_processor_set_instrs(PyObject *, PyObject *, void *);

/* Recherche une instruction d'après son adresse. */
static PyObject *py_arch_processor_find_instr_by_addr(PyObject *, PyObject *);



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

static PyObject *py_arch_processor_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_arch_processor_type();

    if (type == base)
    {
        result = NULL;
        PyErr_Format(PyExc_RuntimeError, _("%s is an abstract class"), type->tp_name);
        goto exit;
    }

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_ARCH_PROCESSOR, type->tp_name,
                               (GClassInitFunc)py_arch_processor_init_gclass, NULL,
                               (GInstanceInitFunc)py_arch_processor_init_ginstance);

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

    result = PyType_GenericNew(type, args, kwds);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class  = classe à initialiser.                               *
*                unused = données non utilisées ici.                          *
*                                                                             *
*  Description : Initialise la classe générique des processeurs.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_arch_processor_init_gclass(GArchProcessorClass *class, gpointer unused)
{
    class->get_key = py_arch_processor_get_key_wrapper;
    class->get_desc = py_arch_processor_get_desc_wrapper;
    class->get_memsize = py_arch_processor_get_memory_size_wrapper;
    class->get_inssize = py_arch_processor_get_instruction_min_size_wrapper;
    class->has_vspace = py_arch_processor_has_virtual_space_wrapper;

    class->get_ctx = py_arch_processor_get_context_wrapper;
    class->disassemble = py_arch_processor_disassemble_wrapper;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc  = instance à initialiser.                              *
*                class = classe du type correspondant.                        *
*                                                                             *
*  Description : Initialise une instance de processeur d'architecture.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_arch_processor_init_ginstance(GArchProcessor *proc, GArchProcessor *class)
{

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

static int py_arch_processor_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    unsigned int endianness;                /* Boutisme du processeur      */
    int ret;                                /* Bilan de lecture des args.  */
    GArchProcessor *proc;                   /* Processeur à manipuler      */

    static char *kwlist[] = { "endianness", NULL };

#define ARCH_PROCESSOR_DOC                                              \
    "The ArchProcessor object aims to get subclassed to create"         \
    " processors for new architectures.\n"                              \
    "\n"                                                                \
    "Several items have to be defined as class attributes in the final" \
    " class:\n"                                                         \
    "* *_key*: a string providing a small name used to identify the"    \
    " architecture;\n"                                                  \
    "* *_desc*: a string for a human readable description of the"       \
    " new architecture;\n"                                              \
    "* *_memory_size*: size of the memory space, as a"                  \
    " pychrysalide.analysis.BinContent.MemoryDataSize value;\n"         \
    "* *_ins_min_size*: size of the smallest instruction, as a"         \
    " pychrysalide.analysis.BinContent.MemoryDataSize value;\n"         \
    "* *_virtual_space*: a boolean value indicating if the architecture"\
    " supports a virtual space.\n"                                      \
    "\n"                                                                \
    "Calls to the *__init__* constructor of this abstract object expect"\
    " the following arguments as keyword parameters:\n"                 \
    "* *endianness*: endianness to apply to the binary content to"      \
    " disassemble, as a pychrysalide.analysis.BinContent.SourceEndian"  \
    " value."

    /* Récupération des paramètres */

    ret = PyArg_ParseTupleAndKeywords(args, kwds, "I", kwlist, &endianness);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    proc = G_ARCH_PROCESSOR(pygobject_get(self));

    proc->endianness = endianness;

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit la désignation interne du processeur d'architecture. *
*                                                                             *
*  Retour      : Simple chaîne de caractères.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_arch_processor_get_key_wrapper(const GArchProcessor *proc)
{
    char *result;                           /* Désignation à renvoyer      */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pykey;                        /* Clef en objet Python        */
    int ret;                                /* Bilan d'une conversion      */

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(proc));

    if (PyObject_HasAttrString(pyobj, "_key"))
    {
        pykey = PyObject_GetAttrString(pyobj, "_key");

        if (pykey != NULL)
        {
            ret = PyUnicode_Check(pykey);

            if (ret)
                result = strdup(PyUnicode_AsUTF8(pykey));

            Py_DECREF(pykey);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit le nom humain de l'architecture visée.               *
*                                                                             *
*  Retour      : Désignation humaine associée au processeur.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *py_arch_processor_get_desc_wrapper(const GArchProcessor *proc)
{
    char *result;                           /* Désignation à renvoyer      */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pydesc;                       /* Description en objet Python */
    int ret;                                /* Bilan d'une conversion      */

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(proc));

    if (PyObject_HasAttrString(pyobj, "_desc"))
    {
        pydesc = PyObject_GetAttrString(pyobj, "_desc");

        if (pydesc != NULL)
        {
            ret = PyUnicode_Check(pydesc);

            if (ret)
                result = strdup(PyUnicode_AsUTF8(pydesc));

            Py_DECREF(pydesc);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit la taille de l'espace mémoire d'une architecture.    *
*                                                                             *
*  Retour      : Taille de l'espace mémoire.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static MemoryDataSize py_arch_processor_get_memory_size_wrapper(const GArchProcessor *proc)
{
    MemoryDataSize result;                  /* Taille  à retourner         */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pysize;                       /* Taille en objet Python      */
    int ret;                                /* Bilan d'une conversion      */

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(proc));

    if (PyObject_HasAttrString(pyobj, "_memory_size"))
    {
        pysize = PyObject_GetAttrString(pyobj, "_memory_size");

        if (pysize != NULL)
        {
            ret = PyLong_Check(pysize);

            if (ret)
                result = PyLong_AsUnsignedLong(pysize);

            Py_DECREF(pysize);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit la taille min. des instructions d'une architecture.  *
*                                                                             *
*  Retour      : Taille d'encodage des instructions.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static MemoryDataSize py_arch_processor_get_instruction_min_size_wrapper(const GArchProcessor *proc)
{
    MemoryDataSize result;                  /* Taille  à retourner         */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pysize;                       /* Taille en objet Python      */
    int ret;                                /* Bilan d'une conversion      */

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(proc));

    if (PyObject_HasAttrString(pyobj, "_ins_min_size"))
    {
        pysize = PyObject_GetAttrString(pyobj, "_ins_min_size");

        if (pysize != NULL)
        {
            ret = PyLong_Check(pysize);

            if (ret)
                result = PyLong_AsUnsignedLong(pysize);

            Py_DECREF(pysize);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Indique si l'architecture possède un espace virtuel ou non.  *
*                                                                             *
*  Retour      : true si un espace virtuel existe, false sinon.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool py_arch_processor_has_virtual_space_wrapper(const GArchProcessor *proc)
{
    bool result;                            /* Indication à retourner      */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyhas;                        /* Présence en objet Python    */
    int ret;                                /* Bilan d'une conversion      */

    result = false;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(proc));

    if (PyObject_HasAttrString(pyobj, "_virtual_space"))
    {
        pyhas = PyObject_GetAttrString(pyobj, "_virtual_space");

        if (pyhas != NULL)
        {
            ret = PyBool_Check(pyhas);

            if (ret)
                result = (pyhas == Py_True);

            Py_DECREF(pyhas);

        }

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture visée par la procédure.                  *
*                                                                             *
*  Description : Fournit un contexte propre au processeur d'une architecture. *
*                                                                             *
*  Retour      : Nouveau contexte mis à disposition.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GProcContext *py_arch_processor_get_context_wrapper(const GArchProcessor *proc)
{
    GProcContext *result;                   /* Instance à retourner        */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pyctx;                        /* Contexte en objet Python    */
    int ret;                                /* Bilan d'une conversion      */
    GArchProcessorClass *class;             /* Classe de l'objet courant   */
    GArchProcessorClass *parent;            /* Classe parente              */

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(proc));

    if (has_python_method(pyobj, "_get_context"))
    {
        pyctx = run_python_method(pyobj, "_get_context", NULL);

        if (pyctx == NULL)
            result = NULL;

        else
        {
            ret = convert_to_proc_context(pyctx, &result);

            if (ret == 1)
                g_object_ref(G_OBJECT(result));
            else
            {
                PyErr_Clear();
                result = NULL;
            }

            Py_DECREF(pyctx);

        }

    }

    else
    {
        class = G_ARCH_PROCESSOR_GET_CLASS(proc);
        parent = g_type_class_peek_parent(class);

        result = parent->get_ctx(proc);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc    = architecture visée par la procédure.               *
*                ctx     = contexte lié à l'exécution du processeur.          *
*                content = flux de données à analyser.                        *
*                pos     = position courante dans ce flux. [OUT]              *
*                format  = format du fichier contenant le code.               *
*                                                                             *
*  Description : Désassemble une instruction dans un flux de données.         *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *py_arch_processor_disassemble_wrapper(const GArchProcessor *proc, GProcContext *ctx, const GBinContent *content, vmpa2t *pos, GExeFormat *format)
{
    GArchInstruction *result;               /* Instance à retourner        */
    PyGILState_STATE gstate;                /* Sauvegarde d'environnement  */
    PyObject *pyobj;                        /* Objet Python concerné       */
    PyObject *pypos;                        /* Position en objet Python    */
    PyObject *args;                         /* Arguments pour l'appel      */
    PyObject *pyins;                        /* Instruction en objet Python */
    int ret;                                /* Bilan d'une conversion      */

    result = NULL;

    gstate = PyGILState_Ensure();

    pyobj = pygobject_new(G_OBJECT(proc));

    if (has_python_method(pyobj, "_disassemble"))
    {
        pypos = build_from_internal_vmpa(pos);
        Py_INCREF(pypos);

        args = PyTuple_New(4);
        PyTuple_SetItem(args, 0, pygobject_new(G_OBJECT(ctx)));
        PyTuple_SetItem(args, 1, pygobject_new(G_OBJECT(content)));
        PyTuple_SetItem(args, 2, pypos);
        PyTuple_SetItem(args, 3, pygobject_new(G_OBJECT(format)));

        pyins = run_python_method(pyobj, "_disassemble", args);

        Py_DECREF(args);

        if (pyins != NULL)
        {
            ret = convert_to_arch_instruction(pyins, &result);

            if (ret == 1)
                g_object_ref(G_OBJECT(result));
            else
            {
                PyErr_Clear();
                result = NULL;
            }

            Py_DECREF(pyins);

            copy_vmpa(pos, get_internal_vmpa(pypos));

        }

        Py_DECREF(pypos);

    }

    Py_DECREF(pyobj);

    PyGILState_Release(gstate);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                              DEFINITION DE PROCESSEUR                              */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la désignation interne du processeur d'architecture. *
*                                                                             *
*  Retour      : Simple chaîne de caractères.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_processor_get_key(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GArchProcessor *proc;                   /* Version GLib de l'opérande  */
    char *key;                              /* Désignation du processeur   */

#define ARCH_PROCESSOR_KEY_ATTRIB PYTHON_GET_DEF_FULL           \
(                                                               \
    key, py_arch_processor,                                     \
    "Provide the small name used to identify the architecture," \
    " as a code string."                                        \
)

    proc = G_ARCH_PROCESSOR(pygobject_get(self));
    assert(proc != NULL);

    key = g_arch_processor_get_key(proc);

    if (key != NULL)
    {
        result = PyUnicode_FromString(key);
        free(key);
    }
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
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le nom humain de l'architecture visée.               *
*                                                                             *
*  Retour      : Désignation humaine associée au processeur.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_processor_get_desc(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GArchProcessor *proc;                   /* Version GLib de l'opérande  */
    char *desc;                              /* Désignation du processeur   */

#define ARCH_PROCESSOR_DESC_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                           \
    desc, py_arch_processor,                                \
    "Provide a human readable description of the new"       \
    " architecture, as a simple string."                    \
)

    proc = G_ARCH_PROCESSOR(pygobject_get(self));
    assert(proc != NULL);

    desc = g_arch_processor_get_desc(proc);

    if (desc != NULL)
    {
        result = PyUnicode_FromString(desc);
        free(desc);
    }
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
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le boustime du processeur d'une architecture.        *
*                                                                             *
*  Retour      : Boutisme associé au processeur.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_processor_get_endianness(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GArchProcessor *proc;                   /* Version GLib de l'opérande  */
    SourceEndian endianness;                /* Boutisme du processeur      */

#define ARCH_PROCESSOR_ENDIANNESS_ATTRIB PYTHON_GET_DEF_FULL    \
(                                                               \
    endianness, py_arch_processor,                              \
    "Provide the processor endianness, as a"                    \
    " pychrysalide.analysis.BinContent.SourceEndian value."     \
)

    proc = G_ARCH_PROCESSOR(pygobject_get(self));
    assert(proc != NULL);

    endianness = g_arch_processor_get_endianness(proc);

    result = cast_with_constants_group_from_type(get_python_binary_content_type(), "SourceEndian", endianness);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la taille de l'espace mémoire d'une architecture.    *
*                                                                             *
*  Retour      : Taille de l'espace mémoire.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_processor_get_memory_size(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GArchProcessor *proc;                   /* Version GLib de l'opérande  */
    MemoryDataSize size;                    /* Type de donnée représentée  */

#define ARCH_PROCESSOR_MEMORY_SIZE_ATTRIB PYTHON_GET_DEF_FULL       \
(                                                                   \
    memory_size, py_arch_processor,                                 \
    "Provide the size of the architecture memory address space,"    \
    " as a pychrysalide.analysis.BinContent.MemoryDataSize value."  \
)

    proc = G_ARCH_PROCESSOR(pygobject_get(self));
    assert(proc != NULL);

    size = g_arch_processor_get_memory_size(proc);

    result = cast_with_constants_group_from_type(get_python_binary_content_type(), "MemoryDataSize", size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la taille min. des instructions d'une architecture.  *
*                                                                             *
*  Retour      : Taille d'encodage des instructions.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_processor_get_ins_min_size(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GArchProcessor *proc;                   /* Version GLib de l'opérande  */
    MemoryDataSize size;                    /* Type de donnée représentée  */

#define ARCH_PROCESSOR_INS_MIN_SIZE_ATTRIB PYTHON_GET_DEF_FULL      \
(                                                                   \
    ins_min_size, py_arch_processor,                                \
    "Provide the minimal size of one processor instruction, as a"   \
    " pychrysalide.analysis.BinContent.MemoryDataSize value."       \
)

    proc = G_ARCH_PROCESSOR(pygobject_get(self));
    assert(proc != NULL);

    size = g_arch_processor_get_instruction_min_size(proc);

    result = cast_with_constants_group_from_type(get_python_binary_content_type(), "MemoryDataSize", size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique si l'architecture possède un espace virtuel ou non.  *
*                                                                             *
*  Retour      : True si un espace virtuel existe, False sinon.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_processor_has_virtual_space(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GArchProcessor *proc;                   /* Architecture visée          */
    bool status;                            /* Bilan de consultation       */

#define ARCH_PROCESSOR_VIRTUAL_SPACE_ATTRIB PYTHON_HAS_DEF_FULL     \
(                                                                   \
    virtual_space, py_arch_processor,                               \
    "Tell if the processor provides a virtual address space. This"  \
    " status is a boolean value."                                   \
)

    proc = G_ARCH_PROCESSOR(pygobject_get(self));

    status = g_arch_processor_has_virtual_space(proc);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = architecture concernée par la procédure.              *
*                args = instruction représentant le point de départ.          *
*                                                                             *
*  Description : Fournit un contexte propre au processeur d'une architecture. *
*                                                                             *
*  Retour      : Nouveau contexte mis à disposition.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_processor_get_context(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GArchProcessor *proc;                   /* Processeur manipulé         */
    GProcContext *ctx;                      /* Nouveau contexte en place   */

    proc = G_ARCH_PROCESSOR(pygobject_get(self));

    ctx = g_arch_processor_get_context(proc);

    if (ctx != NULL)
    {
        result = pygobject_new(G_OBJECT(ctx));
        g_object_unref(G_OBJECT(ctx));
    }
    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = architecture concernée par la procédure.              *
*                args = instruction représentant le point de départ.          *
*                                                                             *
*  Description : Désassemble une instruction dans un flux de données.         *
*                                                                             *
*  Retour      : Instruction mise en place ou None en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_processor_disassemble(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GProcContext *ctx;                      /* Contexte de désassemblage   */
    GBinContent *content;                   /* Contenu binaire à parcourir */
    vmpa2t *addr;                           /* Position d'analyse courante */
    GExeFormat *format;                     /* Format de fichier associé   */
    int ret;                                /* Bilan de lecture des args.  */
    GArchProcessor *proc;                   /* Processeur manipulé         */
    GArchInstruction *instr;                /* Instruction mise en place   */

    ret = PyArg_ParseTuple(args, "O&O&OO&",
                           convert_to_proc_context, &ctx,
                           convert_to_binary_content, &content,
                           convert_any_to_vmpa, &addr,
                           convert_to_executable_format, &format);
    if (!ret) return NULL;

    proc = G_ARCH_PROCESSOR(pygobject_get(self));

    instr = g_arch_processor_disassemble(proc, ctx, content, addr, format);

    if (instr != NULL)
    {
        result = pygobject_new(G_OBJECT(instr));
        g_object_unref(G_OBJECT(instr));
    }
    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    clean_vmpa_arg(addr);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                    CONSERVATION DES SOUCIS DURANT LE CHARGEMENT                    */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = architecture concernée par la procédure.              *
*                args = instruction représentant le point de départ.          *
*                                                                             *
*  Description : Etend la liste des soucis détectés avec de nouvelles infos.  *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_processor_add_error(PyObject *self, PyObject *args)
{
    ArchProcessingError type;               /* Type d'erreur détectée      */
    vmpa2t *addr;                           /* Position d'une erreur       */
    const char *desc;                       /* Description d'une erreur    */
    int ret;                                /* Bilan de lecture des args.  */
    GArchProcessor *proc;                   /* Processeur manipulé         */

#define ARCH_PROCESSOR_ADD_ERROR_METHOD PYTHON_METHOD_DEF           \
(                                                                   \
    add_error, "$self, type, addr, desc, /",                        \
    METH_VARARGS, py_arch_processor,                                \
    "Extend the list of detected disassembling errors.\n"           \
    "\n"                                                            \
    "The type of error has to be one of the"                        \
    " pychrysalide.arch.ArchProcessor.ArchProcessingError flags."   \
    " The location of the error is a pychrysalide.arch.vmpa"        \
    " instance and a one-line description should give some details" \
    " about what has failed."                                       \
)

    ret = PyArg_ParseTuple(args, "O&O&s", convert_to_arch_processing_error, &type,
                           convert_any_to_vmpa, &addr, &desc);
    if (!ret) return NULL;

    proc = G_ARCH_PROCESSOR(pygobject_get(self));

    g_arch_processor_add_error(proc, type, addr, desc);

    clean_vmpa_arg(addr);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les éléments concernant tous les soucis détectés.    *
*                                                                             *
*  Retour      : Liste des erreurs relevées au niveau de l'assembleur.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_processor_get_errors(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    GArchProcessor *proc;                   /* Architecture visée          */
    size_t count;                           /* Nombre d'éléments à traiter */
    size_t i;                               /* Boucle de parcours          */
#ifndef NDEBUG
    bool status;                            /* Bilan d'un appel            */
#endif
    ArchProcessingError type;               /* Type d'erreur détectée      */
    vmpa2t addr;                            /* Position d'une erreur       */
    char *desc;                             /* Description d'une erreur    */
    PyObject *py_type;                      /* Version Python du type      */
    PyObject *error;                        /* Nouvelle erreur à rajouter  */

#define ARCH_PROCESSOR_ERRORS_ATTRIB PYTHON_GET_DEF_FULL                                \
(                                                                                       \
    errors, py_arch_processor,                                                          \
    "List of all detected errors which occurred during the disassembling process.\n"    \
    "\n"                                                                                \
    "The result is a tuple of (pychrysalide.arch.ArchProcessor.ArchProcessingError,"    \
    " pychrysalide.arch.vmpa, string) values, providing a location and a description"   \
    " for each error."                                                                  \
)

    proc = G_ARCH_PROCESSOR(pygobject_get(self));

    g_arch_processor_lock_errors(proc);

    count = g_arch_processor_count_errors(proc);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
#ifndef NDEBUG
        status = g_arch_processor_get_error(proc, i, &type, &addr, &desc);
        assert(status);
#else
        g_arch_processor_get_error(proc, i, &type, &addr, &desc);
#endif

        py_type = cast_with_constants_group_from_type(get_python_arch_processor_type(),
                                                      "ArchProcessingError", type);
        error = Py_BuildValue("OO&s", py_type, build_from_internal_vmpa, &addr, desc);
        Py_DECREF(py_type);

        PyTuple_SetItem(result, i, error);

    }

    g_arch_processor_unlock_errors(proc);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                    MANIPULATIONS DES INSTRUCTIONS DESASSEMBLEES                    */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les instructions désassemblées pour une architecture.*
*                                                                             *
*  Retour      : Liste des instructions désassemblées ou None si aucune.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_processor_get_instrs(PyObject *self, void *closure)
{
    PyObject *result;                       /* Instance Python à retourner */
    PyTypeObject *iterator_type;            /* Type Python de l'itérateur  */
    PyObject *args;                         /* Liste des arguments d'appel */

    iterator_type = get_python_instr_iterator_type();

    args = Py_BuildValue("On", self, 0);

    result = PyObject_CallObject((PyObject *)iterator_type, args);

    Py_DECREF(args);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Note les instructions désassemblées avec une architecture.   *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_arch_processor_set_instrs(PyObject *self, PyObject *value, void *closure)
{
    size_t count;                           /* Nombre d'instructions       */
    GArchInstruction **list;                /* Liste d'instructions        */
    size_t i;                               /* Boucle de parcours          */
    PyObject *instr;                        /* Instruction en Python       */
    GArchProcessor *proc;                   /* Architecture visée          */

    if (!PyTuple_Check(value))
    {
        PyErr_SetString(PyExc_TypeError, _("The attribute value must be a tuple of instructions."));
        return -1;
    }

    count = PyTuple_Size(value);

    list = (GArchInstruction **)calloc(count, sizeof(GArchInstruction *));

    for (i = 0; i < count; i++)
    {
        instr = PyTuple_GetItem(value, i);

        if (!PyObject_TypeCheck(value, get_python_arch_instruction_type()))
        {
            PyErr_SetString(PyExc_TypeError, _("The attribute value must be a tuple of instructions."));
            count = i;
            goto papsi_error;
        }

        list[i] = G_ARCH_INSTRUCTION(pygobject_get(instr));
        g_object_ref(G_OBJECT(list[i]));

    }

    proc = G_ARCH_PROCESSOR(pygobject_get(self));

    g_arch_processor_set_instructions(proc, list, count);

    return 0;

 papsi_error:

    for (i = 0; i < count; i++)
        g_object_unref(G_OBJECT(list[i]));

    free(list);

    return -1;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = processeur d'architecture à manipuler.                *
*                args = instruction représentant le point de départ.          *
*                                                                             *
*  Description : Recherche une instruction d'après son adresse.               *
*                                                                             *
*  Retour      : Instruction trouvée à l'adresse donnée, None si aucune.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_processor_find_instr_by_addr(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GArchProcessor *proc;                   /* Processeur manipulé         */
    proc_cv_info_t conv;                    /* Informations de conversion  */
    int ret;                                /* Bilan de lecture des args.  */
    GArchInstruction *found;                /* Instruction liée trouvée    */

    proc = G_ARCH_PROCESSOR(pygobject_get(self));

    conv.proc = proc;

    ret = PyArg_ParseTuple(args, "O&", convert_to_vmpa_using_processor, &conv);
    if (!ret) return NULL;

    found = g_arch_processor_find_instr_by_address(proc, conv.vmpa);

    if (found != NULL)
    {
        result = pygobject_new(G_OBJECT(found));
        g_object_unref(G_OBJECT(found));
    }

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                              DEFINITION DE PROCESSEUR                              */
/* ---------------------------------------------------------------------------------- */


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

PyTypeObject *get_python_arch_processor_type(void)
{
    static PyMethodDef py_arch_processor_methods[] = {
        {
            "get_context", py_arch_processor_get_context,
            METH_NOARGS,
            "get_context($self, /)\n--\n\nProvide a new disassembly context."
        },
        {
            "disassemble", py_arch_processor_disassemble,
            METH_VARARGS,
            "disassemble($self, context, content, pos, format, /)\n--\n\nDisassemble a portion of binary content into one instruction."
        },
        ARCH_PROCESSOR_ADD_ERROR_METHOD,
        {
            "find_instr_by_addr", py_arch_processor_find_instr_by_addr,
            METH_VARARGS,
            "find_instr_by_addr($self, addr, /)\n--\n\nLook for an instruction located at a given address."
        },
        { NULL }
    };

    static PyGetSetDef py_arch_processor_getseters[] = {
        ARCH_PROCESSOR_KEY_ATTRIB,
        ARCH_PROCESSOR_DESC_ATTRIB,
        ARCH_PROCESSOR_ENDIANNESS_ATTRIB,
        ARCH_PROCESSOR_MEMORY_SIZE_ATTRIB,
        ARCH_PROCESSOR_INS_MIN_SIZE_ATTRIB,
        ARCH_PROCESSOR_VIRTUAL_SPACE_ATTRIB,
        ARCH_PROCESSOR_ERRORS_ATTRIB,
        {
            "instrs", py_arch_processor_get_instrs, py_arch_processor_set_instrs,
            "Give access to the disassembled instructions run by the current processor.", NULL
        },
        { NULL }
    };

    static PyTypeObject py_arch_processor_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.ArchProcessor",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IS_ABSTRACT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = ARCH_PROCESSOR_DOC,

        .tp_methods     = py_arch_processor_methods,
        .tp_getset      = py_arch_processor_getseters,

        .tp_init        = py_arch_processor_init,
        .tp_new         = py_arch_processor_new,

    };

    return &py_arch_processor_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.arch.ArchProcessor'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_arch_processor_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ArchProcessor' */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_arch_processor_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_ARCH_PROCESSOR, type))
            return false;

        if (!define_arch_processor_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en processeur d'architecture.             *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_arch_processor(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_arch_processor_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to arch processor");
            break;

        case 1:
            *((GArchProcessor **)dst) = G_ARCH_PROCESSOR(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                              TRADUCTION D'EMPLACEMENT                              */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : obj  = objet Python à convertir en emplacement.              *
*                info = informations utiles à l'opération.                    *
*                                                                             *
*  Description : Réalise une conversion d'un objet Python en localisation.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_vmpa_using_processor(PyObject *obj, proc_cv_info_t *info)
{
    int result;                             /* Bilan à retourner           */
    int ret;                                /* Bilan d'une consultation    */

    ret = PyObject_IsInstance(obj, (PyObject *)get_python_vmpa_type());

    if (ret)
    {
        info->vmpa = get_internal_vmpa(obj);
        result = 1;
    }

    else
    {
        ret = PyObject_IsInstance(obj, (PyObject *)&PyLong_Type);

        if (ret)
        {
            info->vmpa = &info->tmp;

            if (g_arch_processor_has_virtual_space(info->proc))
                init_vmpa(info->vmpa, VMPA_NO_PHYSICAL, PyLong_AsUnsignedLongLong(obj));
            else
                init_vmpa(info->vmpa, PyLong_AsUnsignedLongLong(obj), VMPA_NO_VIRTUAL);

            result = 1;

        }

        else
            result = 0;

    }

    if (result == 0)
        PyErr_Format(PyExc_TypeError, _("unable to convert object to VMPA location"));

    return result;

}
