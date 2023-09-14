
/* Chrysalide - Outil d'analyse de fichiers binaires
 * logs.c - équivalent Python du fichier "core/logs.c"
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


#include "logs.h"


#include <pygobject.h>


#include <core/logs.h>
#include <plugins/self.h>


#include "constants.h"
#include "../access.h"
#include "../core.h"
#include "../helpers.h"



/* Fournit la verbosité des messages système. */
static PyObject *py_logs_get_verbosity(PyObject *, PyObject *);

/* Définit la verbosité des messages système. */
static PyObject *py_logs_set_verbosity(PyObject *, PyObject *);

/* Affiche un message dans le journal des messages système. */
static PyObject *py_logs_log_message(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Fournit la verbosité des messages système.                   *
*                                                                             *
*  Retour      : Plus faible niveau des types de message affichés.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_logs_get_verbosity(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Conversion à retourner      */
    LogMessageType verbosity;               /* Niveau de filtre de message */

#define LOGS_GET_VERBOSITY_METHOD PYTHON_METHOD_DEF                         \
(                                                                           \
    get_verbosity, "",                                                      \
    METH_NOARGS, py_logs,                                                   \
    "Get the log verbosity, as a pychrysalide.core.LogMessageType level.\n" \
    "\n"                                                                    \
    "A *COUNT* value means no log gets displayed, a null value means"       \
    " all kinds of logs get printed."                                       \
)

    verbosity = get_log_verbosity();

    result = cast_with_constants_group_from_module("pychrysalide.core", "LogMessageType", verbosity);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Définit la verbosité des messages système.                   *
*                                                                             *
*  Retour      : Rien en équivalent Python.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_logs_set_verbosity(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    LogMessageType verbosity;               /* Niveau de filtre de message */

#define LOGS_SET_VERBOSITY_METHOD PYTHON_METHOD_DEF                         \
(                                                                           \
    set_verbosity, "level, /",                                              \
    METH_VARARGS, py_logs,                                                  \
    "Set the log verbosity. The provided level has to be castable into a"   \
    " pychrysalide.core.LogMessageType value.\n"                            \
    "\n"                                                                    \
    "A *COUNT* value means no log gets displayed, a null value means"       \
    " all kinds of logs get printed."                                       \
)

    if (!PyArg_ParseTuple(args, "O&", convert_to_log_message_type, &verbosity))
        return NULL;

    set_log_verbosity(verbosity);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Affiche un message dans le journal des messages système.     *
*                                                                             *
*  Retour      : Rien en équivalent Python.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_logs_log_message(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    LogMessageType type;                    /* Espèce du message           */
    const char *msg;                        /* Contenu du message          */

#define LOGS_LOG_MESSAGE_METHOD PYTHON_METHOD_DEF                           \
(                                                                           \
    log_message, "type, msg, /",                                            \
    METH_VARARGS, py_logs,                                                  \
    "Display a message in the log window, in graphical mode, or in the"     \
    " console output if none.\n"                                            \
    "\n"                                                                    \
    "The type of the message has to be a pychrysalide.core.LogMessageType"  \
    " value."                                                               \
)

    if (!PyArg_ParseTuple(args, "O&s", convert_to_log_message_type, &type, &msg))
        return NULL;

    log_plugin_simple_message(type, msg);

    result = Py_None;
    Py_INCREF(result);

    return result;

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

bool populate_core_module_with_logs(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_logs_methods[] = {
        LOGS_GET_VERBOSITY_METHOD,
        LOGS_SET_VERBOSITY_METHOD,
        LOGS_LOG_MESSAGE_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.core");

    result = register_python_module_methods(module, py_logs_methods);

    if (result)
        result = define_core_logs_constants(module);

    return result;

}
