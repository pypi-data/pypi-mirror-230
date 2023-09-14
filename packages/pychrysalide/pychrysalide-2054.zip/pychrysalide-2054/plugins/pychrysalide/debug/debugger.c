
/* Chrysalide - Outil d'analyse de fichiers binaires
 * debugger.c - instances Python de débogueurs
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


#include "debugger.h"


#include <assert.h>
#include <malloc.h>
#include <pygobject.h>


#include <debug/debugger.h>


#include "../access.h"
#include "../helpers.h"
#include "../arch/vmpa.h"





/* Fournit les identifiants de tous les threads actifs. */
static PyObject *py_binary_debugger_list_all_threads(PyObject *, PyObject *);



/* Lit une valeur de 8 bits à une adresse arbitraire. */
static PyObject *py_binary_debugger_read_memory_u8(PyObject *, PyObject *);

/* Lit une valeur de 16 bits à une adresse arbitraire. */
static PyObject *py_binary_debugger_read_memory_u16(PyObject *, PyObject *);

/* Lit une valeur de 32 bits à une adresse arbitraire. */
static PyObject *py_binary_debugger_read_memory_u32(PyObject *, PyObject *);

/* Lit une valeur de 64 bits à une adresse arbitraire. */
static PyObject *py_binary_debugger_read_memory_u64(PyObject *, PyObject *);

/* Liste l'ensemble des registres appartenant à un groupe. */
static PyObject *py_binary_debugger_get_register_names(PyObject *, PyObject *);

/* Indique la taille associée à un registre donné. */
static PyObject *py_binary_debugger_get_register_size(PyObject *, PyObject *);

/* Lit une valeur de 8 bits à partir d'un registre. */
static PyObject *py_binary_debugger_read_register_u8(PyObject *, PyObject *);

/* Lit une valeur de 16 bits à partir d'un registre. */
static PyObject *py_binary_debugger_read_register_u16(PyObject *, PyObject *);

/* Lit une valeur de 32 bits à partir d'un registre. */
static PyObject *py_binary_debugger_read_register_u32(PyObject *, PyObject *);

/* Lit une valeur de 64 bits à partir d'un registre. */
static PyObject *py_binary_debugger_read_register_u64(PyObject *, PyObject *);

/* Ecrit une valeur de 8 bits dans un registre. */
static PyObject *py_binary_debugger_write_register_u8(PyObject *, PyObject *);

/* Ecrit une valeur de 16 bits dans un registre. */
static PyObject *py_binary_debugger_write_register_u16(PyObject *, PyObject *);

/* Ecrit une valeur de 32 bits dans un registre. */
static PyObject *py_binary_debugger_write_register_u32(PyObject *, PyObject *);

/* Ecrit une valeur de 64 bits dans un registre. */
static PyObject *py_binary_debugger_write_register_u64(PyObject *, PyObject *);



/* Remonte la pile d'appels jusqu'au point courant. */
static PyObject *py_binary_debugger_get_call_stack(PyObject *, PyObject *);



/* Ajoute un point d'arrêt basique en mémoire. */
static PyObject *py_binary_debugger_add_mem_bp(PyObject *, PyObject *);

/* Retire un point d'arrêt basique en mémoire. */
static PyObject *py_binary_debugger_delete_mem_bp(PyObject *, PyObject *);



/* Redémarre le processus de débogage. */
static PyObject *py_binary_debugger_restart(PyObject *, PyObject *);

/* Remet en marche le débogueur courant. */
static PyObject *py_binary_debugger_resume(PyObject *, PyObject *);

/* Relance l'exécution pour une seule instruction. */
static PyObject *py_binary_debugger_stepi(PyObject *, PyObject *);
















/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments non utilisés ici.                           *
*                                                                             *
*  Description : Fournit les identifiants de tous les threads actifs.         *
*                                                                             *
*  Retour      : Liste contenant identifiants et désignations de threads.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_list_all_threads(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    size_t count;                           /* Quantité de threads actifs  */
    dbg_thread_desc *threads;               /* Liste des threads actifs    */
    size_t i;                               /* Boucle de parcours          */
    PyObject *thread;                       /* Détails sur un thread donné */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    threads = g_binary_debugger_list_all_threads(debugger, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        thread = PyTuple_New(2);
        PyTuple_SetItem(result, i, thread);

        PyTuple_SetItem(thread, 0, PyLong_FromLong(threads[i].id));
        PyTuple_SetItem(thread, 1, PyUnicode_FromString(threads[i].name));

    }

    delete_dbg_thread_desc(threads, count);

    return result;

}







/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Lit une valeur de 8 bits à une adresse arbitraire.           *
*                                                                             *
*  Retour      : Valeur lue ou None.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_read_memory_u8(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    int ret;                                /* Bilan de lecture des args.  */
    vmpa2t *addr;                           /* Position interne associée   */
    uint8_t value;                          /* Valeur lue en mémoire       */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "O&", convert_any_to_vmpa, &addr);
    if (!ret) return NULL;

    status = g_binary_debugger_read_memory_u8(debugger, get_virt_addr(addr), &value);

    if (status)
        result = PyLong_FromUnsignedLongLong(value);

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
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Lit une valeur de 16 bits à une adresse arbitraire.          *
*                                                                             *
*  Retour      : Valeur lue ou None.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_read_memory_u16(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    int ret;                                /* Bilan de lecture des args.  */
    vmpa2t *addr;                           /* Position interne associée   */
    uint16_t value;                         /* Valeur lue en mémoire       */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "O&", convert_any_to_vmpa, &addr);
    if (!ret) return NULL;

    status = g_binary_debugger_read_memory_u16(debugger, get_virt_addr(addr), &value);

    if (status)
        result = PyLong_FromUnsignedLongLong(value);

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
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Lit une valeur de 32 bits à une adresse arbitraire.          *
*                                                                             *
*  Retour      : Valeur lue ou None.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_read_memory_u32(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    int ret;                                /* Bilan de lecture des args.  */
    vmpa2t *addr;                           /* Position interne associée   */
    uint32_t value;                         /* Valeur lue en mémoire       */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "O&", convert_any_to_vmpa, &addr);
    if (!ret) return NULL;

    status = g_binary_debugger_read_memory_u32(debugger, get_virt_addr(addr), &value);

    if (status)
        result = PyLong_FromUnsignedLongLong(value);

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
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Lit une valeur de 64 bits à une adresse arbitraire.          *
*                                                                             *
*  Retour      : Valeur lue ou None.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_read_memory_u64(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    int ret;                                /* Bilan de lecture des args.  */
    vmpa2t *addr;                           /* Position interne associée   */
    uint64_t value;                         /* Valeur lue en mémoire       */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "O&", convert_any_to_vmpa, &addr);
    if (!ret) return NULL;

    status = g_binary_debugger_read_memory_u64(debugger, get_virt_addr(addr), &value);

    if (status)
        result = PyLong_FromUnsignedLongLong(value);

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
*  Paramètres  : self = instance de débogueur à consulter.                    *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Liste l'ensemble des registres appartenant à un groupe.      *
*                                                                             *
*  Retour      : Liste de noms à libérer de la mémoire après utilisation.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_get_register_names(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    const char *group;                      /* Nom du registre à manipuler */
    int ret;                                /* Bilan de lecture des args.  */
    char **list;                            /* Liste de noms de registre   */
    size_t count;                           /* Taille de cette liste       */
    size_t i;                               /* Boucle de parcours          */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "|s", &group);
    if (!ret) return NULL;

    list = g_binary_debugger_get_register_names(debugger, group, &count);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        PyTuple_SetItem(result, i, PyUnicode_FromString(list[i]));
        free(list[i]);
    }

    if (list != NULL)
        free(list);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance de débogueur à consulter.                    *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Indique la taille associée à un registre donné.              *
*                                                                             *
*  Retour      : Taille en bits, ou 0 si le registre n'a pas été trouvé.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_get_register_size(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    const char *reg;                        /* Nom du registre à manipuler */
    int ret;                                /* Bilan de lecture des args.  */
    unsigned int size;                      /* Taille associée au registre */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "s", &reg);
    if (!ret) return NULL;

    size = g_binary_debugger_get_register_size(debugger, reg);

    result = PyLong_FromUnsignedLong(size);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Lit une valeur de 8 bits à partir d'un registre.             *
*                                                                             *
*  Retour      : Valeur lue ou None.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_read_register_u8(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    const char *reg;                        /* Nom du registre à manipuler */
    int ret;                                /* Bilan de lecture des args.  */
    uint8_t value;                          /* Valeur lue en mémoire       */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "s", &reg);
    if (!ret) return NULL;

    status = g_binary_debugger_read_register_u8(debugger, reg, &value);

    if (status)
        result = PyLong_FromUnsignedLongLong(value);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Lit une valeur de 16 bits à partir d'un registre.            *
*                                                                             *
*  Retour      : Valeur lue ou None.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_read_register_u16(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    const char *reg;                        /* Nom du registre à manipuler */
    int ret;                                /* Bilan de lecture des args.  */
    uint16_t value;                         /* Valeur lue en mémoire       */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "s", &reg);
    if (!ret) return NULL;

    status = g_binary_debugger_read_register_u16(debugger, reg, &value);

    if (status)
        result = PyLong_FromUnsignedLongLong(value);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Lit une valeur de 32 bits à partir d'un registre.            *
*                                                                             *
*  Retour      : Valeur lue ou None.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_read_register_u32(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    const char *reg;                        /* Nom du registre à manipuler */
    int ret;                                /* Bilan de lecture des args.  */
    uint32_t value;                         /* Valeur lue en mémoire       */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "s", &reg);
    if (!ret) return NULL;

    status = g_binary_debugger_read_register_u32(debugger, reg, &value);

    if (status)
        result = PyLong_FromUnsignedLongLong(value);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Lit une valeur de 64 bits à partir d'un registre.            *
*                                                                             *
*  Retour      : Valeur lue ou None.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_read_register_u64(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    const char *reg;                        /* Nom du registre à manipuler */
    int ret;                                /* Bilan de lecture des args.  */
    uint64_t value;                         /* Valeur lue en mémoire       */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "s", &reg);
    if (!ret) return NULL;

    status = g_binary_debugger_read_register_u64(debugger, reg, &value);

    if (status)
        result = PyLong_FromUnsignedLongLong(value);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Ecrit une valeur de 8 bits dans un registre.                 *
*                                                                             *
*  Retour      : Valeur lue ou None.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_write_register_u8(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    const char *reg;                        /* Nom du registre à manipuler */
    int ret;                                /* Bilan de lecture des args.  */
    uint8_t value;                          /* Valeur lue en mémoire       */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "sB", &reg, &value);
    if (!ret) return NULL;

    status = g_binary_debugger_write_register_u8(debugger, reg, &value);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Ecrit une valeur de 16 bits dans un registre.                *
*                                                                             *
*  Retour      : Valeur lue ou None.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_write_register_u16(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    const char *reg;                        /* Nom du registre à manipuler */
    int ret;                                /* Bilan de lecture des args.  */
    uint16_t value;                         /* Valeur lue en mémoire       */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "sH", &reg, &value);
    if (!ret) return NULL;

    status = g_binary_debugger_write_register_u16(debugger, reg, &value);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Ecrit une valeur de 32 bits dans un registre.                *
*                                                                             *
*  Retour      : Valeur lue ou None.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_write_register_u32(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    const char *reg;                        /* Nom du registre à manipuler */
    int ret;                                /* Bilan de lecture des args.  */
    uint32_t value;                         /* Valeur lue en mémoire       */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "sI", &reg, &value);
    if (!ret) return NULL;

    status = g_binary_debugger_write_register_u32(debugger, reg, &value);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Ecrit une valeur de 64 bits dans un registre.                *
*                                                                             *
*  Retour      : Valeur lue ou None.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_write_register_u64(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    const char *reg;                        /* Nom du registre à manipuler */
    int ret;                                /* Bilan de lecture des args.  */
    uint64_t value;                         /* Valeur lue en mémoire       */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "sK", &reg, &value);
    if (!ret) return NULL;

    status = g_binary_debugger_write_register_u64(debugger, reg, &value);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}








/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Remonte la pile d'appels jusqu'au point courant.             *
*                                                                             *
*  Retour      : Pile d'appels sous forme de liste ou None en cas d'erreur.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_get_call_stack(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    virt_t *callstack;                      /* Pile d'appels obtenue       */
    size_t size;                            /* Hauteur de cette pile       */
    bool status;                            /* Bilan de l'opération        */
    size_t i;                               /* Boucle de parcours          */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    status = g_binary_debugger_get_call_stack(debugger, &callstack, &size);

    if (!status)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        result = PyTuple_New(size);

        for (i = 0; i < size; i++)
            PyTuple_SetItem(result, i, PyLong_FromUnsignedLongLong(callstack[i]));

        if (callstack != NULL)
            free(callstack);

    }

    return result;

}








/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Ajoute un point d'arrêt basique en mémoire.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_add_mem_bp(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    vmpa2t *addr;                           /* Position interne associée   */
    int ret;                                /* Bilan de lecture des args.  */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "O&", convert_any_to_vmpa, &addr);
    if (!ret) return NULL;

    status = g_binary_debugger_add_memory_breakpoint(debugger, get_virt_addr(addr));

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    clean_vmpa_arg(addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments accompagnant l'appel.                       *
*                                                                             *
*  Description : Retire un point d'arrêt basique en mémoire.                  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_delete_mem_bp(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    vmpa2t *addr;                           /* Position interne associée   */
    int ret;                                /* Bilan de lecture des args.  */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    ret = PyArg_ParseTuple(args, "O&", convert_any_to_vmpa, &addr);
    if (!ret) return NULL;

    status = g_binary_debugger_delete_memory_breakpoint(debugger, get_virt_addr(addr));

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    clean_vmpa_arg(addr);

    return result;

}








/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments non utilisés ici.                           *
*                                                                             *
*  Description : Redémarre le processus de débogage.                          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_restart(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    status = g_binary_debugger_restart(debugger);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments non utilisés ici.                           *
*                                                                             *
*  Description : Remet en marche le débogueur courant.                        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_resume(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    status = g_binary_debugger_resume(debugger);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = arguments non utilisés ici.                           *
*                                                                             *
*  Description : Relance l'exécution pour une seule instruction.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_binary_debugger_stepi(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    GBinaryDebugger *debugger;              /* Version GLib du format      */
    bool status;                            /* Bilan de l'opération        */

    debugger = G_BINARY_DEBUGGER(pygobject_get(self));
    assert(debugger != NULL);

    status = g_binary_debugger_stepi(debugger, false);

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

PyTypeObject *get_python_binary_debugger_type(void)
{
    static PyMethodDef py_binary_debugger_methods[] = {
        {
            "list_all_threads", py_binary_debugger_list_all_threads,
            METH_NOARGS,
            "list_all_threads($self, /)\n--\n\nList all current active threads."
        },
        {
            "read_mem_u8", py_binary_debugger_read_memory_u8,
            METH_VARARGS,
            "read_mem_u8($self, addr, /)\n--\n\nRead a 8-bit value from a given address."
        },
        {
            "read_mem_u16", py_binary_debugger_read_memory_u16,
            METH_VARARGS,
            "read_mem_u16($self, addr, /)\n--\n\nRead a 16-bit value from a given address."
        },
        {
            "read_mem_u32", py_binary_debugger_read_memory_u32,
            METH_VARARGS,
            "read_mem_u32($self, addr, /)\n--\n\nRead a 32-bit value from a given address."
        },
        {
            "read_mem_u64", py_binary_debugger_read_memory_u64,
            METH_VARARGS,
            "read_mem_u64($self, addr, /)\n--\n\nRead a 64-bit value from a given address."
        },
        {
            "get_reg_names", py_binary_debugger_get_register_names,
            METH_VARARGS,
            "get_reg_names($self, grp, /)\n--\n\nGet the names of all registers belonging to an optional group."
        },
        {
            "get_reg_size", py_binary_debugger_get_register_size,
            METH_VARARGS,
            "get_reg_size($self, name, /)\n--\n\nGet the size of a given register."
        },
        {
            "read_reg_u8", py_binary_debugger_read_register_u8,
            METH_VARARGS,
            "read_reg_u8($self, reg, /)\n--\n\nRead a 8-bit value from a named register."
        },
        {
            "read_reg_u16", py_binary_debugger_read_register_u16,
            METH_VARARGS,
            "read_reg_u16($self, reg, /)\n--\n\nRead a 16-bit value from a named register."
        },
        {
            "read_reg_u32", py_binary_debugger_read_register_u32,
            METH_VARARGS,
            "read_reg_u32($self, reg, /)\n--\n\nRead a 32-bit value from a named register."
        },
        {
            "read_reg_u64", py_binary_debugger_read_register_u64,
            METH_VARARGS,
            "read_reg_u64($self, reg, /)\n--\n\nRead a 64-bit value from a named register."
        },
        {
            "write_reg_u8", py_binary_debugger_write_register_u8,
            METH_VARARGS,
            "write_reg_u8($self, reg, val, /)\n--\n\nWrite a 8-bit value into a named register."
        },
        {
            "write_reg_u16", py_binary_debugger_write_register_u16,
            METH_VARARGS,
            "write_reg_u16($self, reg, val, /)\n--\n\nWrite a 16-bit value into a named register."
        },
        {
            "write_reg_u32", py_binary_debugger_write_register_u32,
            METH_VARARGS,
            "write_reg_u32($self, reg, val, /)\n--\n\nWrite a 32-bit value into a named register."
        },
        {
            "write_reg_u64", py_binary_debugger_write_register_u64,
            METH_VARARGS,
            "write_reg_u64($self, reg, val, /)\n--\n\nWrite a 64-bit value into a named register."
        },
        {
            "get_call_stack", py_binary_debugger_get_call_stack,
            METH_NOARGS,
            "get_call_stack($self, /)\n--\n\nGet the current call stack."
        },
        {
            "add_mem_bp", py_binary_debugger_add_mem_bp,
            METH_VARARGS,
            "add_mem_bp($self, addr, /)\n--\n\nInsert a memory breakpoint at a given address."
        },
        {
            "delete_mem_bp", py_binary_debugger_delete_mem_bp,
            METH_VARARGS,
            "delete_mem_bp($self, addr, /)\n--\n\nRemove a memory breakpoint at a given address."
        },
        {
            "restart", py_binary_debugger_restart,
            METH_NOARGS,
            "restart($self, /)\n--\n\nRestart the current debugging session."
        },
        {
            "resume", py_binary_debugger_resume,
            METH_NOARGS,
            "resume($self, /)\n--\n\nResume the current debugging session."
        },
        {
            "stepi", py_binary_debugger_stepi,
            METH_NOARGS,
            "stepi($self, /)\n--\n\nExecute one machine instruction, then stop and return to the debugger."
        },
        { NULL }
    };

    static PyGetSetDef py_binary_debugger_getseters[] = {
        { NULL }
    };

    static PyTypeObject py_binary_debugger_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.debug.BinaryDebugger",

        .tp_flags       = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,

        .tp_doc         = "PyChrysalide loaded binary",

        .tp_methods     = py_binary_debugger_methods,
        .tp_getset      = py_binary_debugger_getseters

    };

    return &py_binary_debugger_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.....BinaryDebugger'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_binary_debugger_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BinaryDebugger'*/
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_binary_debugger_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.debug");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_BINARY_DEBUGGER, type))
            return false;

    }

    return true;

}
