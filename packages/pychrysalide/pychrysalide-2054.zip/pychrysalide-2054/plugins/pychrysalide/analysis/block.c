
/* Chrysalide - Outil d'analyse de fichiers binaires
 * block.c - équivalent Python du fichier "analysis/block.c"
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


#include "block.h"


#include <malloc.h>
#include <pygobject.h>


#include <analysis/block.h>


#include "../access.h"
#include "../helpers.h"
#include "../arch/instruction.h"
#include "../arch/vmpa.h"



/* ----------------------------- BLOC DE CODE GENERIQUE ----------------------------- */


/* Indique l'indice d'intégration du bloc dans une liste. */
static PyObject *py_code_block_get_index(PyObject *, void *);

/* Fournit le rang du bloc de code dans le flot d'exécution. */
static PyObject *py_code_block_get_rank(PyObject *, void *);

/* Fournit les détails d'une source de bloc de code. */
static PyObject *py_code_block_get_sources(PyObject *, void *);

/* Fournit les détails des destinations de bloc de code. */
static PyObject *py_code_block_get_destinations(PyObject *, void *);



/* ------------------------- REGROUPEMENT EN LISTE DE BLOCS ------------------------- */


/* Recherche un bloc de code contenant une adresse donnée. */
static PyObject *py_block_list_find_by_addr(PyObject *, PyObject *);

/* Itère sur l'ensemble des blocs de code inclus dans une liste. */
static PyObject *py_block_list_iter(PyObject *);

/* Dénombre les blocs de code inclus dans une liste. */
static PyObject *py_block_list_count(PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                               BLOC DE CODE GENERIQUE                               */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique l'indice d'intégration du bloc dans une liste.       *
*                                                                             *
*  Retour      : Indice valide dans une liste.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_code_block_get_index(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GCodeBlock *block;                      /* Bloc de code à consulter    */
    size_t value;                           /* Valeur à transmettre        */

    block = G_CODE_BLOCK(pygobject_get(self));

    value = g_code_block_get_index(block);

    result = PyLong_FromSize_t(value);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit le rang du bloc de code dans le flot d'exécution.    *
*                                                                             *
*  Retour      : Indice supérieur ou égal à zéro.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_code_block_get_rank(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GCodeBlock *block;                      /* Bloc de code à consulter    */
    size_t value;                           /* Valeur à transmettre        */

    block = G_CODE_BLOCK(pygobject_get(self));

    value = g_code_block_get_rank(block);

    result = PyLong_FromSize_t(value);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les détails d'une source de bloc de code.            *
*                                                                             *
*  Retour      : Liens déterminés vers des bloc de code de source.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_code_block_get_sources(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GCodeBlock *block;                      /* Bloc de code à consulter    */
    size_t count;                           /* Quantité de blocs liés      */
    block_link_t *links;                    /* Liens à traiter             */
    size_t i;                               /* Boucle de parcours          */
    block_link_t *source;                   /* Origine des liens           */
    PyObject *linked;                       /* Source de lien Python       */
    PyObject *type;                         /* Nature du lien en Python    */
#ifndef NDEBUG
    int ret;                                /* Bilan d'une écriture d'arg. */
#endif

#define CODE_BLOCK_SOURCES_ATTRIB PYTHON_GET_DEF_FULL               \
(                                                                   \
    sources, py_code_block,                                         \
    "List of source blocks.\n"                                      \
    "\n"                                                            \
    "Each item of the resulting tuple is a pair of"                 \
    " pychrysalide.analysis.CodeBlock instance and"                 \
    " pychrysalide.arch.ArchInstruction.InstructionLinkType value." \
)

    block = G_CODE_BLOCK(pygobject_get(self));

    links = g_code_block_get_sources(block, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        source = &links[i];

        linked = pygobject_new(G_OBJECT(source->linked));
        type = cast_with_constants_group_from_type(get_python_arch_instruction_type(),
                                                   "InstructionLinkType", source->type);

#ifndef NDEBUG
        ret = PyTuple_SetItem(result, i, Py_BuildValue("(OO)", linked, type));
        assert(ret == 0);
#else
        PyTuple_SetItem(result, i, Py_BuildValue("(OO)", linked, type));
#endif

        unref_block_link(source);

    }

    if (links != NULL)
        free(links);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit les détails des destinations de bloc de code.        *
*                                                                             *
*  Retour      : Liens déterminés vers des bloc de code de destination.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_code_block_get_destinations(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GCodeBlock *block;                      /* Bloc de code à consulter    */
    size_t count;                           /* Quantité de blocs liés      */
    block_link_t *links;                    /* Liens à traiter             */
    size_t i;                               /* Boucle de parcours          */
    block_link_t *dest;                     /* Destination des liens       */
    PyObject *linked;                       /* Destination de lien Python  */
    PyObject *type;                         /* Nature du lien en Python    */
#ifndef NDEBUG
    int ret;                                /* Bilan d'une écriture d'arg. */
#endif

#define CODE_BLOCK_DESTINATIONS_ATTRIB PYTHON_GET_DEF_FULL          \
(                                                                   \
    destinations, py_code_block,                                    \
    "List of destination blocks.\n"                                 \
    "\n"                                                            \
    "Each item of the resulting tuple is a pair of"                 \
    " pychrysalide.analysis.CodeBlock instance and"                 \
    " pychrysalide.arch.ArchInstruction.InstructionLinkType value." \
)

    block = G_CODE_BLOCK(pygobject_get(self));

    links = g_code_block_get_destinations(block, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        dest = &links[i];

        linked = pygobject_new(G_OBJECT(dest->linked));
        type = cast_with_constants_group_from_type(get_python_arch_instruction_type(),
                                                   "InstructionLinkType", dest->type);

#ifndef NDEBUG
        ret = PyTuple_SetItem(result, i, Py_BuildValue("(OO)", linked, type));
        assert(ret == 0);
#else
        PyTuple_SetItem(result, i, Py_BuildValue("(OO)", linked, type));
#endif

        unref_block_link(dest);

    }

    if (links != NULL)
        free(links);

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

PyTypeObject *get_python_code_block_type(void)
{
    static PyMethodDef py_code_block_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_code_block_getseters[] = {
        {
            "index", py_code_block_get_index, NULL,
            "Index of the code block in the parent list, if any.", NULL
        },
        {
            "rank", py_code_block_get_rank, NULL,
            "Rang of the code block.", NULL
        },
        CODE_BLOCK_SOURCES_ATTRIB,
        CODE_BLOCK_DESTINATIONS_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_code_block_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.CodeBlock",

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "PyChrysalide code block",

        .tp_methods     = py_code_block_methods,
        .tp_getset      = py_code_block_getseters,

    };

    return &py_code_block_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.analysis.CodeBlock'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_code_block_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'InstrBlock'    */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_code_block_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_CODE_BLOCK, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en bloc de code.                          *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_code_block(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_code_block_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to code block");
            break;

        case 1:
            *((GCodeBlock **)dst) = G_CODE_BLOCK(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           REGROUPEMENT EN LISTE DE BLOCS                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant une liste de blocs de code.       *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Recherche un bloc de code contenant une adresse donnée.      *
*                                                                             *
*  Retour      : Bloc de code trouvé ou None si aucun.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_block_list_find_by_addr(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Conclusion à retourner      */
    vmpa2t *addr;                           /* Emplacement ciblé           */
    int ret;                                /* Bilan de lecture des args.  */
    GBlockList *list;                       /* Liste de blocs manipulée    */
    GCodeBlock *found;                      /* Eventuel bloc trouvé        */

    ret = PyArg_ParseTuple(args, "O&", convert_any_to_vmpa, &addr);
    if (!ret) return NULL;

    list = G_BLOCK_LIST(pygobject_get(self));

    found = g_block_list_find_by_addr(list, addr);

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

    clean_vmpa_arg(addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                                                                             *
*  Description : Itère sur l'ensemble des blocs de code inclus dans une liste.*
*                                                                             *
*  Retour      : Liste de blocs de code capable d'itération.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_block_list_iter(PyObject *self)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GBlockList *list;                       /* Liste de blocs manipulée    */
    size_t count;                           /* Nombre de blocs présents    */
    size_t i;                               /* Boucle de parcours          */
    GCodeBlock *block;                      /* Bloc de code à intégrer     */

    list = G_BLOCK_LIST(pygobject_get(self));

    count = g_block_list_count_blocks(list);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        block = g_block_list_get_block(list, i);

        PyTuple_SetItem(result, i, pygobject_new(G_OBJECT(block)));

        g_object_unref(G_OBJECT(block));

    }

    result = PySeqIter_New(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Dénombre les blocs de code inclus dans une liste.            *
*                                                                             *
*  Retour      : Quantité de blocs de code.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_block_list_count(PyObject *self, void *closure)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GBlockList *list;                       /* Liste de blocs manipulée    */
    size_t count;                           /* Nombre de blocs présents    */

    list = G_BLOCK_LIST(pygobject_get(self));

    count = g_block_list_count_blocks(list);

    result = PyLong_FromUnsignedLong(count);

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

PyTypeObject *get_python_block_list_type(void)
{
    static PyMethodDef py_block_list_methods[] = {
        {
            "find_by_addr", py_block_list_find_by_addr,
            METH_VARARGS,
            "find_by_addr($self, addr, /)\n--\n\nFind a code block containing a given address."
        },
        { NULL }
    };

    static PyGetSetDef py_block_list_getseters[] = {
        {
            "count", py_block_list_count, NULL,
            "Quantity of code blocks included in the list.", NULL
        },
        { NULL }
    };

    static PyTypeObject py_block_list_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.analysis.BlockList",

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "PyChrysalide basic block",

        .tp_iter        = py_block_list_iter,

        .tp_methods     = py_block_list_methods,
        .tp_getset      = py_block_list_getseters,

    };

    return &py_block_list_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.analysis.BlockList'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_block_list_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BlockList'     */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_block_list_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.analysis");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_BLOCK_LIST, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en liste de blocs de code.                *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_block_list_with_ref(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */
    GBlockList *new;                        /* Nouvelle liste à constituer */
    PyObject *item;                         /* Elément issu de l'itération */
    int ret;                                /* Bilan d'une conversion      */
    GCodeBlock *block;                      /* Bloc de code à intégrer     */

    if (arg == NULL)
    {
        g_clear_object((void **)dst);
        result = 1;
    }

    else
    {
        result = PyObject_IsInstance(arg, (PyObject *)get_python_block_list_type());

        switch (result)
        {
            case -1:
                /* L'exception est déjà fixée par Python */
                result = 0;
                break;

            case 0:

                if (PyIter_Check(arg))
                {
                    new = g_block_list_new(0);

                    result = Py_CLEANUP_SUPPORTED;

                    for (item = PyIter_Next(arg); item != NULL; item = PyIter_Next(arg))
                    {
                        ret = convert_to_code_block(item, &block);

                        if (ret == 1)
                            g_object_ref(G_OBJECT(block));

                        Py_DECREF(item);

                        if (ret != 1)
                        {
                            result = 0;
                            break;
                        }

                        g_block_list_append_block(new, block);

                    }

                    if (result != Py_CLEANUP_SUPPORTED)
                        g_object_unref(G_OBJECT(new));

                    else
                        *((GBlockList **)dst) = new;

                }

                else
                    PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to graph cluster");

                break;

            case 1:
                *((GBlockList **)dst) = G_BLOCK_LIST(pygobject_get(arg));
                break;

            default:
                assert(false);
                break;

        }

    }

    return result;

}
