
/* Chrysalide - Outil d'analyse de fichiers binaires
 * parser.c - équivalent Python du fichier "plugins/yaml/parser.c"
 *
 * Copyright (C) 2019-2023 Cyrille Bagard
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


#include "parser.h"


#include <pygobject.h>
#include <string.h>


#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>


#include "../parser.h"



/* Crée une arborescence YAML pour contenu au format adapté. */
static PyObject *py_yaml_parse_from_text(PyObject *, PyObject *);

/* Crée une arborescence YAML pour fichier au format adapté. */
static PyObject *py_yaml_parse_from_file(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = arguments fournis lors de l'appel à la fonction.      *
*                                                                             *
*  Description : Crée une arborescence YAML pour contenu au format adapté.    *
*                                                                             *
*  Retour      : Arborescence YAML mise en place ou NULL en cas d'échec.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_yaml_parse_from_text(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *text;                       /* Chaîne à traiter.           */
    int ret;                                /* Bilan de lecture des args.  */
    GYamlNode *root;                        /* Noeud racine obtenu         */

#define YAML_PARSE_FROM_TEXT_METHOD PYTHON_METHOD_DEF                   \
(                                                                       \
    parse_from_text, "text, /",                                         \
    METH_VARARGS, py_yaml,                                              \
    "Parse a YAML content in order to build the relative YAML tree.\n"  \
    "\n"                                                                \
    "The *text* argument is a string containg a markup content to"      \
    " parse.\n"                                                         \
    "\n"                                                                \
    "The result is a pychrysalide.plugins.yaml.YamlNode instance"       \
    " or None in case of error."                                        \
)

    ret = PyArg_ParseTuple(args, "s", &text);
    if (!ret) return NULL;

    root = parse_yaml_from_text(text, strlen(text));

    if (root != NULL)
    {
        result = pygobject_new(G_OBJECT(root));
        g_object_unref(G_OBJECT(root));
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
*  Paramètres  : self = NULL car méthode statique.                            *
*                args = arguments fournis lors de l'appel à la fonction.      *
*                                                                             *
*  Description : Crée une arborescence YAML pour fichier au format adapté.    *
*                                                                             *
*  Retour      : Arborescence YAML mise en place ou NULL en cas d'échec.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_yaml_parse_from_file(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Instance à retourner        */
    const char *filename;                   /* Chemin vers des définitions */
    int ret;                                /* Bilan de lecture des args.  */
    GYamlNode *root;                        /* Noeud racine obtenu         */

#define YAML_PARSE_FROM_FILE_METHOD PYTHON_METHOD_DEF                   \
(                                                                       \
    parse_from_file, "filename, /",                                     \
    METH_VARARGS, py_yaml,                                              \
    "Parse a YAML content in order to build the relative YAML tree.\n"  \
    "\n"                                                                \
    "The *filename* argument is a string for a path pointing to a YAML" \
    " content. This path can be either a real filename or a resource"   \
    " URI.\n"                                                           \
    "\n"                                                                \
    "The result is a pychrysalide.plugins.yaml.YamlNode instance"       \
    " or None in case of error."                                        \
)

    ret = PyArg_ParseTuple(args, "s", &filename);
    if (!ret) return NULL;

    root = parse_yaml_from_file(filename);

    if (root != NULL)
    {
        result = pygobject_new(G_OBJECT(root));
        g_object_unref(G_OBJECT(root));
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
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Définit une extension du module 'plugins.yaml' à compléter.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_yaml_module_with_parsers(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Module à recompléter        */

    static PyMethodDef py_yaml_methods[] = {
        YAML_PARSE_FROM_TEXT_METHOD,
        YAML_PARSE_FROM_FILE_METHOD,
        { NULL }
    };

    module = get_access_to_python_module("pychrysalide.plugins.yaml");

    result = register_python_module_methods(module, py_yaml_methods);

    return result;

}
