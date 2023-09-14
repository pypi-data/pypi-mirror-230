
/* Chrysalide - Outil d'analyse de fichiers binaires
 * queue.c - équivalent Python du fichier "core/queue.c"
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


#include "queue.h"


#include <pygobject.h>


#include <core/queue.h>


#include "../access.h"
#include "../helpers.h"



/* Constitue un nouveau groupe de travail global. */
static PyObject *py_queue_setup_global_work_group(PyObject *, PyObject *);

/* Constitue un nouveau petit groupe de travail global. */
static PyObject *py_queue_setup_tiny_global_work_group(PyObject *, PyObject *);

/* Attend que toutes les tâches de tout groupe soient traitées. */
static PyObject *py_queue_wait_for_all_global_works(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Constitue un nouveau groupe de travail global.               *
*                                                                             *
*  Retour      : Nouvel identifiant unique d'un nouveau groupe de travail.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_queue_setup_global_work_group(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    wgroup_id_t wid;                        /* Identifiant de groupe       */

#define QUEUE_SETUP_GLOBAL_WORK_GROUP_METHOD PYTHON_METHOD_DEF  \
(                                                               \
    setup_global_work_group, "",                                \
    METH_NOARGS, py_queue,                                      \
    "Create a new work group for parallel processed jobs.\n"    \
    "\n"                                                        \
    "The quantity of threads allocated for processing future"   \
    " data depends of available CPU cores.\n"                   \
    "\n"                                                        \
    "The returned value is an integer value referring to the"   \
    " unique identifier of a work group."                       \
)

    wid = setup_global_work_group();

    result = PyLong_FromUnsignedLongLong(wid);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = paramètre à récupérer pour le traitement.             *
*                                                                             *
*  Description : Constitue un nouveau petit groupe de travail global.         *
*                                                                             *
*  Retour      : Nouvel identifiant unique d'un nouveau groupe de travail.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_queue_setup_tiny_global_work_group(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    unsigned int count;                     /* Nombre de thread parallèle  */
    int ret;                                /* Bilan de lecture des args.  */
    wgroup_id_t wid;                        /* Identifiant de groupe       */

#define QUEUE_SETUP_TINY_GLOBAL_WORK_GROUP_METHOD PYTHON_METHOD_DEF \
(                                                                   \
    setup_tiny_global_work_group, "/, count = 1",                   \
    METH_VARARGS, py_queue,                                         \
    "Create a new tiny work group for parallel processed jobs.\n"   \
    "\n"                                                            \
    "The *count* argument defines the quantity of threads allocated"\
    " for processing future data.\n"                                \
    "\n"                                                            \
    "The returned value is an integer value referring to the"       \
    " unique identifier of a work group."                           \
)

    result = NULL;

    count = 1;

    ret = PyArg_ParseTuple(args, "|I", &count);
    if (!ret) goto exit;

    if (count < 1)
    {
        PyErr_SetString(PyExc_ValueError, "the provided quantity has to be strictly positive");
        goto exit;
    }

    wid = setup_tiny_global_work_group(count);

    result = PyLong_FromUnsignedLongLong(wid);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Attend que toutes les tâches de tout groupe soient traitées. *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_queue_wait_for_all_global_works(PyObject *self, PyObject *args)
{
#define QUEUE_WAIT_FOR_ALL_GLOBAL_WORKS_METHOD PYTHON_METHOD_DEF    \
(                                                                   \
    wait_for_all_global_works, "",                                  \
    METH_NOARGS, py_queue,                                          \
    "Wait for all global tasks being processed."                    \
)

    wait_for_all_global_works();

    Py_RETURN_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Définit une extension du module 'core' à compléter.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_core_module_with_queue(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_queue_methods[] = {
        QUEUE_SETUP_GLOBAL_WORK_GROUP_METHOD,
        QUEUE_SETUP_TINY_GLOBAL_WORK_GROUP_METHOD,
        QUEUE_WAIT_FOR_ALL_GLOBAL_WORKS_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.core");

    result = register_python_module_methods(module, py_queue_methods);

    return result;

}
