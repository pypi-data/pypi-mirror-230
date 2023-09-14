
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instruction.c - équivalent Python du fichier "arch/instruction.h"
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


#include "instruction.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>
#include <pygobject.h>


#include <i18n.h>
#include <arch/instruction-int.h>
#include <plugins/dt.h>


#include "constants.h"
#include "operand.h"
#include "vmpa.h"
#include "../access.h"
#include "../helpers.h"
#include "../glibext/linegen.h"



static G_DEFINE_QUARK(cached_keyword, get_cached_keyword);



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_arch_instruction_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise la classe générique des instructions. */
static void py_arch_instruction_init_gclass(GArchInstructionClass *, gpointer);

CREATE_DYN_ABSTRACT_CONSTRUCTOR(arch_instruction, G_TYPE_ARCH_INSTRUCTION, py_arch_instruction_init_gclass);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_arch_instruction_init(PyObject *, PyObject *, PyObject *);

/* Fournit le nom humain de l'instruction manipulée. */
static const char *py_arch_instruction_get_class_keyword(GArchInstruction *);



/* --------------------------- MANIPULATION DES OPERANDES --------------------------- */


/* Attache un opérande supplémentaire à une instruction. */
static PyObject *py_arch_instruction_attach_extra_operand(PyObject *, PyObject *);

/* Fournit tous les opérandes d'une instruction. */
static PyObject *py_arch_instruction_get_operands(PyObject *, void *);

/* Remplace un opérande d'une instruction par un autre. */
static PyObject *py_arch_instruction_replace_operand(PyObject *, PyObject *);

/* Détache un opérande liée d'une instruction. */
static PyObject *py_arch_instruction_detach_operand(PyObject *, PyObject *);

/* Détermine le chemin conduisant à un opérande. */
static PyObject *py_arch_instruction_find_operand_path(PyObject *, PyObject *);

/* Obtient l'opérande correspondant à un chemin donné. */
static PyObject *py_arch_instruction_get_operand_from_path(PyObject *, PyObject *);



/* ------------------- DEFINITION DES LIAISONS ENTRE INSTRUCTIONS ------------------- */


/* Fournit les origines d'une instruction donnée. */
static PyObject *py_arch_instruction_get_sources(PyObject *, void *);

/* Fournit les destinations d'une instruction donnée. */
static PyObject *py_arch_instruction_get_destinations(PyObject *, void *);



/* --------------------- INSTRUCTIONS D'ARCHITECTURES EN PYTHON --------------------- */


/* Fournit l'identifiant unique pour un ensemble d'instructions. */
static PyObject *py_arch_instruction_get_unique_id(PyObject *, void *);

/* Fournit la place mémoire d'une instruction. */
static PyObject *py_arch_instruction_get_range(PyObject *, void *);

/* Définit la localisation d'une instruction. */
static int py_arch_instruction_set_range(PyObject *, PyObject *, void *);

/* Fournit le nom humain de l'instruction manipulée. */
static PyObject *py_arch_instruction_get_keyword(PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : class  = classe à initialiser.                               *
*                unused = données non utilisées ici.                          *
*                                                                             *
*  Description : Initialise la classe générique des instructions.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void py_arch_instruction_init_gclass(GArchInstructionClass *class, gpointer unused)
{
    GArchInstructionClass *instr;           /* Encore une autre vision...  */

    instr = G_ARCH_INSTRUCTION_CLASS(class);

    instr->get_keyword = (get_instruction_keyword_fc)py_arch_instruction_get_class_keyword;

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

static int py_arch_instruction_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    unsigned short int uid;                 /* Indentifiant unique de type */
    const char *keyword;                    /* Désignation d'instruction   */
    int ret;                                /* Bilan de lecture des args.  */
    GArchInstruction *instr;                /* Instruction à manipuler     */
    GQuark cache_key;                       /* Emplacement local           */

    static char *kwlist[] = { "uid", "keyword", NULL };

    /* Récupération des paramètres */

    ret = PyArg_ParseTupleAndKeywords(args, kwds, "Hs", kwlist, &uid, &keyword);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    instr = G_ARCH_INSTRUCTION(pygobject_get(self));

    cache_key = get_cached_keyword_quark();

    g_object_set_qdata_full(G_OBJECT(instr), cache_key, strdup(keyword), g_free);

    g_arch_instruction_set_unique_id(G_ARCH_INSTRUCTION(instr), uid);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction d'assemblage à consulter.                *
*                                                                             *
*  Description : Fournit le nom humain de l'instruction manipulée.            *
*                                                                             *
*  Retour      : Mot clef de bas niveau.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static const char *py_arch_instruction_get_class_keyword(GArchInstruction *instr)
{
    const char *result;                     /* Désignation à retourner     */
    GQuark cache_key;                       /* Emplacement local           */

    cache_key = get_cached_keyword_quark();

    result = g_object_get_qdata(G_OBJECT(instr), cache_key);
    assert(result != NULL);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                             MANIPULATION DES OPERANDES                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = architecture concernée par la procédure.              *
*                args = instruction représentant le point de départ.          *
*                                                                             *
*  Description : Attache un opérande supplémentaire à une instruction.        *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_instruction_attach_extra_operand(PyObject *self, PyObject *args)
{
    GArchOperand *op;                       /* Opérande concerné à ajouter */
    int ret;                                /* Bilan de lecture des args.  */
    GArchInstruction *instr;                /* Instruction manipulée       */

    ret = PyArg_ParseTuple(args, "O&", convert_to_arch_operand, &op);
    if (!ret) return NULL;

    instr = G_ARCH_INSTRUCTION(pygobject_get(self));

    g_object_ref(G_OBJECT(op));

    g_arch_instruction_attach_extra_operand(instr, op);

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self   = objet représentant une instruction.                 *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Fournit tous les opérandes d'une instruction.                *
*                                                                             *
*  Retour      : Valeur associée à la propriété consultée.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_instruction_get_operands(PyObject *self, void *unused)
{
    PyObject *result;                       /* Instance à retourner        */
    GArchInstruction *instr;                /* Version native              */
    size_t count;                           /* Nombre d'opérandes présents */
    size_t i;                               /* Boucle de parcours          */
    GArchOperand *operand;                  /* Opérande à manipuler        */
    PyObject *opobj;                        /* Version Python              */
#ifndef NDEBUG
    int ret;                                /* Bilan d'une écriture d'arg. */
#endif

    instr = G_ARCH_INSTRUCTION(pygobject_get(self));

    g_arch_instruction_lock_operands(instr);

    count = _g_arch_instruction_count_operands(instr);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        operand = _g_arch_instruction_get_operand(instr, i);

        opobj = pygobject_new(G_OBJECT(operand));

#ifndef NDEBUG
        ret = PyTuple_SetItem(result, i, Py_BuildValue("O", opobj));
        assert(ret == 0);
#else
        PyTuple_SetItem(result, i, Py_BuildValue("O", opobj));
#endif

        g_object_unref(G_OBJECT(operand));

    }

    g_arch_instruction_unlock_operands(instr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = architecture concernée par la procédure.              *
*                args = instruction représentant le point de départ.          *
*                                                                             *
*  Description : Remplace un opérande d'une instruction par un autre.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_instruction_replace_operand(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GArchOperand *old;                      /* Ancien opérande à remplacer */
    GArchOperand *new;                      /* Nouvel opérande à intégrer  */
    int ret;                                /* Bilan de lecture des args.  */
    GArchInstruction *instr;                /* Instruction manipulée       */
    bool status;                            /* Bilan de l'opération        */

    ret = PyArg_ParseTuple(args, "O&O&", convert_to_arch_operand, &old, convert_to_arch_operand, &new);
    if (!ret) return NULL;

    instr = G_ARCH_INSTRUCTION(pygobject_get(self));

    status = g_arch_instruction_replace_operand(instr, old, new);

    if (status)
        g_object_ref(G_OBJECT(new));

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = architecture concernée par la procédure.              *
*                args = instruction représentant le point de départ.          *
*                                                                             *
*  Description : Détache un opérande liée d'une instruction.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_instruction_detach_operand(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    GArchOperand *target;                   /* Opérande ciblé par l'action */
    int ret;                                /* Bilan de lecture des args.  */
    GArchInstruction *instr;                /* Instruction manipulée       */
    bool status;                            /* Bilan de l'opération        */

    ret = PyArg_ParseTuple(args, "O&", convert_to_arch_operand, &target);
    if (!ret) return NULL;

    instr = G_ARCH_INSTRUCTION(pygobject_get(self));

    status = g_arch_instruction_detach_operand(instr, target);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = architecture concernée par la procédure.              *
*                args = instruction représentant le point de départ.          *
*                                                                             *
*  Description : Détermine le chemin conduisant à un opérande.                *
*                                                                             *
*  Retour      : Chemin d'accès à l'opérande ou None en cas d'absence.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_instruction_find_operand_path(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Chemin à retourner          */
    GArchOperand *target;                   /* Opérande ciblé par l'action */
    int ret;                                /* Bilan de lecture des args.  */
    GArchInstruction *instr;                /* Instruction manipulée       */
    char *path;                             /* Chemin déterminé            */

#define ARCH_INSTRUCTION_FIND_OPERAND_PATH_METHOD PYTHON_METHOD_DEF         \
(                                                                           \
    find_operand_path, "$self, target, /",                                  \
    METH_VARARGS, py_arch_instruction,                                      \
    "Compute the path leading to an instruction operand.\n"                 \
    "\n"                                                                    \
    "The *target* has to be an instance of pychrysalide.arch.ArchOperand"   \
    " included in the instruction.\n"                                       \
    "\n"                                                                    \
    "The result is a string of the form 'n[:n:n:n]', where n is an"         \
    " internal index, or None if the *target* is not found. This kind of"   \
    " path is aimed to be built for the"                                    \
    " pychrysalide.arch.ArchInstruction.find_operand_path() function."      \
)

    ret = PyArg_ParseTuple(args, "O&", convert_to_arch_operand, &target);
    if (!ret) return NULL;

    instr = G_ARCH_INSTRUCTION(pygobject_get(self));

    path = g_arch_instruction_find_operand_path(instr, target);

    if (path != NULL)
    {
        result = PyUnicode_FromString(path);
        free(path);
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
*  Description : Obtient l'opérande correspondant à un chemin donné.          *
*                                                                             *
*  Retour      : Opérande trouvé ou None en cas d'échec.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_instruction_get_operand_from_path(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvaille à retourner      */
    const char *path;                       /* Chemin à parcourir          */
    int ret;                                /* Bilan de lecture des args.  */
    GArchInstruction *instr;                /* Instruction manipulée       */
    GArchOperand *op;                       /* Opérande retrouvé           */

#define ARCH_INSTRUCTION_GET_OPERAND_FROM_PATH_METHOD PYTHON_METHOD_DEF     \
(                                                                           \
    get_operand_from_path, "$self, path, /",                                \
    METH_VARARGS, py_arch_instruction,                                      \
    "Retrieve an operand from an instruction by its path.\n"                \
    "\n"                                                                    \
    "This *path* is a string of the form 'n[:n:n:n]', where n is an"        \
    " internal index. Such a path is usually built by the"                  \
    " pychrysalide.arch.ArchInstruction.find_operand_path() function.\n"    \
    "\n"                                                                    \
    "The result is an pychrysalide.arch.ArchOperand instance, or"           \
    " None if no operand was found."                                        \
)

    ret = PyArg_ParseTuple(args, "s", &path);
    if (!ret) return NULL;

    instr = G_ARCH_INSTRUCTION(pygobject_get(self));

    op = g_arch_instruction_get_operand_from_path(instr, path);

    if (op != NULL)
    {
        result = pygobject_new(G_OBJECT(op));
        g_object_unref(G_OBJECT(op));
    }
    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                     DEFINITION DES LIAISONS ENTRE INSTRUCTIONS                     */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self   = instruction d'architecture à manipuler.             *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Fournit les origines d'une instruction donnée.               *
*                                                                             *
*  Retour      : Nombre de ces origines.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_instruction_get_sources(PyObject *self, void *unused)
{
    PyObject *result;                       /* Instance à retourner        */
    GArchInstruction *instr;                /* Version native              */
    size_t count;                           /* Nombre de liens présents    */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *source;             /* Origine des liens           */
    PyObject *linked;                       /* Source de lien Python       */
    PyObject *type;                         /* Nature du lien en Python    */
#ifndef NDEBUG
    int ret;                                /* Bilan d'une écriture d'arg. */
#endif

#define ARCH_INSTRUCTION_SOURCES_ATTRIB PYTHON_GET_DEF_FULL                 \
(                                                                           \
    sources, py_arch_instruction,                                           \
    "Provide the instructions list driving to the current instruction.\n"   \
    "\n"                                                                    \
    "Each item of the resulting tuple is a pair of"                         \
    " pychrysalide.arch.ArchInstruction instance and"                       \
    " pychrysalide.arch.ArchInstruction.InstructionLinkType value."         \
)

    instr = G_ARCH_INSTRUCTION(pygobject_get(self));

    g_arch_instruction_lock_src(instr);

    count = g_arch_instruction_count_sources(instr);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        source = g_arch_instruction_get_source(instr, i);

        linked = pygobject_new(G_OBJECT(source->linked));
        type = cast_with_constants_group_from_type(get_python_arch_instruction_type(),
                                                   "InstructionLinkType", source->type);

#ifndef NDEBUG
        ret = PyTuple_SetItem(result, i, Py_BuildValue("(OO)", linked, type));
        assert(ret == 0);
#else
        PyTuple_SetItem(result, i, Py_BuildValue("(OO)", linked, type));
#endif

        unref_instr_link(source);

    }

    g_arch_instruction_unlock_src(instr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self   = instruction d'architecture à manipuler.             *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Fournit les destinations d'une instruction donnée.           *
*                                                                             *
*  Retour      : Nombre de ces destinations.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_instruction_get_destinations(PyObject *self, void *unused)
{
    PyObject *result;                       /* Instance à retourner        */
    GArchInstruction *instr;                /* Version native              */
    size_t count;                           /* Nombre de liens présents    */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *dest;               /* Destination des liens       */
    PyObject *linked;                       /* Destination de lien Python  */
    PyObject *type;                         /* Nature du lien en Python    */
#ifndef NDEBUG
    int ret;                                /* Bilan d'une écriture d'arg. */
#endif

#define ARCH_INSTRUCTION_DESTINATIONS_ATTRIB PYTHON_GET_DEF_FULL            \
(                                                                           \
    destinations, py_arch_instruction,                                      \
    "Provide the instructions list following the current instruction.\n"    \
    "\n"                                                                    \
    "Each item of the resulting tuple is a pair of"                         \
    " pychrysalide.arch.ArchInstruction instance and"                       \
    " pychrysalide.arch.ArchInstruction.InstructionLinkType value."         \
)

    instr = G_ARCH_INSTRUCTION(pygobject_get(self));

    g_arch_instruction_lock_dest(instr);

    count = g_arch_instruction_count_destinations(instr);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        dest = g_arch_instruction_get_destination(instr, i);

        linked = pygobject_new(G_OBJECT(dest->linked));
        type = cast_with_constants_group_from_type(get_python_arch_instruction_type(),
                                                   "InstructionLinkType", dest->type);

#ifndef NDEBUG
        ret = PyTuple_SetItem(result, i, Py_BuildValue("(OO)", linked, type));
        assert(ret == 0);
#else
        PyTuple_SetItem(result, i, Py_BuildValue("(OO)", linked, type));
#endif

        unref_instr_link(dest);

    }

    g_arch_instruction_unlock_dest(instr);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       INSTRUCTIONS D'ARCHITECTURES EN PYTHON                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant une instruction.               *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Fournit l'identifiant unique pour un ensemble d'instructions.*
*                                                                             *
*  Retour      : Identifiant unique par type d'instruction.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_instruction_get_unique_id(PyObject *self, void *closure)
{
    PyObject *result;                       /* Conversion à retourner      */
    GArchInstruction *instr;                /* Version native              */
    itid_t uid;                             /* Identifiant unique associé  */

    instr = G_ARCH_INSTRUCTION(pygobject_get(self));

    uid = g_arch_instruction_get_unique_id(instr);

    result = PyLong_FromUnsignedLong(uid);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant une instruction.               *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Fournit la place mémoire d'une instruction.                  *
*                                                                             *
*  Retour      : Valeur associée à la propriété consultée.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_instruction_get_range(PyObject *self, void *closure)
{
    PyObject *result;                       /* Conversion à retourner      */
    GArchInstruction *instr;                /* Version native              */
    const mrange_t *range;                  /* Espace mémoire à exporter   */

    instr = G_ARCH_INSTRUCTION(pygobject_get(self));
    range = g_arch_instruction_get_range(instr);

    result = build_from_internal_mrange(range);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Définit la localisation d'une instruction.                   *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_arch_instruction_set_range(PyObject *self, PyObject *value, void *closure)
{
    int ret;                                /* Bilan d'analyse             */
    mrange_t *range;                        /* Espace mémoire à manipuler  */
    GArchInstruction *instr;                /* Version native              */

    ret = PyObject_IsInstance(value, (PyObject *)get_python_mrange_type());
    if (!ret) return -1;

    range = get_internal_mrange(value);

    instr = G_ARCH_INSTRUCTION(pygobject_get(self));
    g_arch_instruction_set_range(instr, range);

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self   = classe représentant une instruction.                *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Fournit le nom humain de l'instruction manipulée.            *
*                                                                             *
*  Retour      : Valeur associée à la propriété consultée.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_arch_instruction_get_keyword(PyObject *self, void *unused)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GArchInstruction *instr;                /* Version native              */
    const char *kw;                         /* Valeur récupérée            */

    instr = G_ARCH_INSTRUCTION(pygobject_get(self));
    kw = g_arch_instruction_get_keyword(instr);

    result = PyUnicode_FromString(kw);

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

PyTypeObject *get_python_arch_instruction_type(void)
{
    static PyMethodDef py_arch_instruction_methods[] = {
        {
            "attach_operand", py_arch_instruction_attach_extra_operand,
            METH_VARARGS,
            "attach_operand($self, op, /)\n--\n\nAdd a new operand to the instruction."
        },
        {
            "replace_operand", py_arch_instruction_replace_operand,
            METH_VARARGS,
            "replace_operand($self, old, new, /)\n--\n\nReplace an old instruction operand by a another one."
        },
        {
            "detach_operand", py_arch_instruction_detach_operand,
            METH_VARARGS,
            "detach_operand($self, target, /)\n--\n\nRemove an operand from the instruction."
        },
        ARCH_INSTRUCTION_FIND_OPERAND_PATH_METHOD,
        ARCH_INSTRUCTION_GET_OPERAND_FROM_PATH_METHOD,
        { NULL }
    };

    static PyGetSetDef py_arch_instruction_getseters[] = {
        {
            "uid", py_arch_instruction_get_unique_id, NULL,
            "Provide the unique identification number given to this kind of instruction.", NULL
        },
        {
            "range", py_arch_instruction_get_range, py_arch_instruction_set_range,
            "Give access to the memory range covered by the current instruction.", NULL
        },
        {
            "keyword", (getter)py_arch_instruction_get_keyword, (setter)NULL,
            "Give le name of the assembly instruction.", NULL
        },
        {
            "operands", (getter)py_arch_instruction_get_operands, (setter)NULL,
            "Provide the list of instruction attached operands.", NULL
        },
        ARCH_INSTRUCTION_SOURCES_ATTRIB,
        ARCH_INSTRUCTION_DESTINATIONS_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_arch_instruction_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.ArchInstruction",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IS_ABSTRACT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "PyChrysalide instruction for a given architecture.",

        .tp_methods     = py_arch_instruction_methods,
        .tp_getset      = py_arch_instruction_getseters,

        .tp_init        = py_arch_instruction_init,
        .tp_new         = py_arch_instruction_new,

    };

    return &py_arch_instruction_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.arch.ArchInstruction'. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_arch_instruction_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'ArchInstruc...'*/
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_arch_instruction_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.arch");

        dict = PyModule_GetDict(module);

        if (!ensure_python_line_generator_is_registered())
            return false;

        if (!register_class_for_pygobject(dict, G_TYPE_ARCH_INSTRUCTION, type))
            return false;

        if (!define_arch_instruction_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en instruction d'architecture.            *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_arch_instruction(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_arch_instruction_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to arch instruction");
            break;

        case 1:
            *((GArchInstruction **)dst) = G_ARCH_INSTRUCTION(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
