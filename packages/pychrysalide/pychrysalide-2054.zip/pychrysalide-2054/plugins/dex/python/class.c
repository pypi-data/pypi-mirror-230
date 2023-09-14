
/* Chrysalide - Outil d'analyse de fichiers binaires
 * class.c - équivalent Python du fichier "plugins/dex/class.c"
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#include "class.h"


#include <pygobject.h>


#include <plugins/pychrysalide/helpers.h>


#include "format.h"
#include "translate.h"
#include "../class.h"



#define DEX_CLASS_DOC                                               \
    "The DexClass object handles a class defined in a DEX file."


/* Fournit la définition brute d'une classe. */
static PyObject *py_dex_class_get_definition(PyObject *, void *);

/* Fournit la définition brute des données d'une classe. */
static PyObject *py_dex_class_get_data(PyObject *, void *);

/* Indique le type Android d'une classe. */
static PyObject *py_dex_class_get_type(PyObject *, void *);

/* Indique le type Android parent d'une classe. */
static PyObject *py_dex_class_get_super(PyObject *, void *);

/* Indique le type Android des interfaces d'une classe. */
static PyObject *py_dex_class_get_interfaces(PyObject *, void *);

/* Fournit les champs chargés correspondant à une classe donnée. */
static PyObject *py_dex_class_get_fields(PyObject *, void *);

/* Fournit les méthodes chargées correspondant à un type donné. */
static PyObject *py_dex_class_get_methods(PyObject *, void *);

/* Retrouve si possible le nom du fichier source d'une classe. */
static PyObject *py_dex_class_get_source_file(PyObject *, void *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la définition brute d'une classe.                    *
*                                                                             *
*  Retour      : Données brutes issues du binaire chargé.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_class_get_definition(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexClass *class;                       /* Version native              */
    const class_def_item *item;             /* Elément à traiter           */

#define DEX_CLASS_DEFINITION_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                           \
    definition, py_dex_class,                               \
    "Native definition of the Dex class."                   \
)

    class = G_DEX_CLASS(pygobject_get(self));

    item = g_dex_class_get_definition(class);

    result = translate_dex_class_definition_to_python(item);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la définition brute des données d'une classe.        *
*                                                                             *
*  Retour      : Données brutes issues du binaire chargé ou None si aucune.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_class_get_data(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexClass *class;                       /* Version native              */
    const class_data_item *item;            /* Elément à traiter           */

#define DEX_CLASS_DATA_ATTRIB PYTHON_GET_DEF_FULL   \
(                                                   \
    data, py_dex_class,                             \
    "Native data of the Dex class, if any."         \
)

    class = G_DEX_CLASS(pygobject_get(self));

    item = g_dex_class_get_data(class);

    if (item == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
        result = translate_dex_class_data_to_python(item);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le type Android d'une classe.                        *
*                                                                             *
*  Retour      : Type de classe ou None en cas d'erreur.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_class_get_type(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexClass *class;                       /* Version native              */
    GDataType *type;                        /* Type de classe              */

#define DEX_CLASS_TYPE_ATTRIB PYTHON_GET_DEF_FULL       \
(                                                       \
    type, py_dex_class,                                 \
    "Android type of the Dex class, None on error."     \
)

    class = G_DEX_CLASS(pygobject_get(self));

    type = g_dex_class_get_class_type(class);

    if (type == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        result = pygobject_new(G_OBJECT(type));

        g_object_unref(G_OBJECT(type));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le type Android parent d'une classe.                 *
*                                                                             *
*  Retour      : Type de classe ou None en cas d'erreur.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_class_get_super(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexClass *class;                       /* Version native              */
    GDataType *type;                        /* Type de classe              */

#define DEX_CLASS_SUPER_ATTRIB PYTHON_GET_DEF_FULL          \
(                                                           \
    super, py_dex_class,                                    \
    "Android type of the parent Dex class, None on error."  \
)

    class = G_DEX_CLASS(pygobject_get(self));

    type = g_dex_class_get_superclass_type(class);

    if (type == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        result = pygobject_new(G_OBJECT(type));

        g_object_unref(G_OBJECT(type));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique le type Android des interfaces d'une classe.         *
*                                                                             *
*  Retour      : Types de classe ou None en cas d'erreur ou d'absence.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_class_get_interfaces(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexClass *class;                       /* Version native              */
    size_t count;                           /* Nombre d'interfaces         */
    GDataType **types;                      /* Types d'interfaces          */
    size_t i;                               /* Boucle de parcours          */
    PyObject *type;                         /* Type à ajouter à la liste   */

#define DEX_CLASS_INTERFACES_ATTRIB PYTHON_GET_DEF_FULL             \
(                                                                   \
    interfaces, py_dex_class,                                       \
    "Interface Android types of the Dex class, None if none and"    \
    " None on error."                                               \
)

    class = G_DEX_CLASS(pygobject_get(self));

    types = g_dex_class_get_interface_types(class, &count);

    if (count == 0)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        result = PyTuple_New(count);

        for (i = 0; i < count; i++)
        {
            if (types[i] == NULL)
            {
                type = Py_None;
                Py_INCREF(type);
            }
            else
            {
                type = pygobject_new(G_OBJECT(types[i]));
                g_object_unref(G_OBJECT(types[i]));
            }

            PyTuple_SetItem(result, i, type);

        }

    }

    if (types != NULL)
        free(types);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = méthodes d'instance si non nul, statiques sinon.   *
*                                                                             *
*  Description : Fournit les champs chargés correspondant à une classe donnée.*
*                                                                             *
*  Retour      : Champs de classe ou None en cas d'erreur ou d'absence.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_class_get_fields(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexClass *class;                       /* Version native              */
    bool instance;                          /* Type de champs ciblés       */
    size_t count;                           /* Nombre d'interfaces         */
    size_t i;                               /* Boucle de parcours          */
    GDexField *field;                       /* Champ à convertir           */
    PyObject *fld;                          /* Objet à ajouter à la liste  */

#define DEX_CLASS_STATIC_FIELDS_ATTRIB PYTHON_GETSET_DEF            \
(                                                                   \
    "static_fields", py_dex_class_get_fields, NULL,                 \
    "List of static fields of the Dex class, None if none and"      \
    " None on error.",                                              \
    NULL                                                            \
)

#define DEX_CLASS_INSTANCE_FIELDS_ATTRIB PYTHON_GETSET_DEF          \
(                                                                   \
    "static_fields", py_dex_class_get_fields, NULL,                 \
    "List of instance fields of the Dex class, None if none and"    \
    " None on error.",                                              \
    (void *)1                                                       \
)

    class = G_DEX_CLASS(pygobject_get(self));

    instance = (closure != NULL);

    count = g_dex_class_count_fields(class, instance);

    if (count == 0)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        result = PyTuple_New(count);

        for (i = 0; i < count; i++)
        {
            field = g_dex_class_get_field(class, instance, i);

            if (field == NULL)
            {
                fld = Py_None;
                Py_INCREF(fld);
            }
            else
            {
                fld = pygobject_new(G_OBJECT(field));
                g_object_unref(G_OBJECT(field));
            }

            PyTuple_SetItem(result, i, fld);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = méthodes directes si non nul, virtuelles sinon.    *
*                                                                             *
*  Description : Fournit les méthodes chargées correspondant à un type donné. *
*                                                                             *
*  Retour      : Types de classe ou None en cas d'erreur ou d'absence.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_class_get_methods(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexClass *class;                       /* Version native              */
    bool virtual;                           /* Type de méthodes ciblées    */
    size_t count;                           /* Nombre d'interfaces         */
    size_t i;                               /* Boucle de parcours          */
    GDexMethod *method;                     /* Méthode à convertir         */
    PyObject *meth;                         /* Objet à ajouter à la liste  */

#define DEX_CLASS_DIRECT_METHODS_ATTRIB PYTHON_GETSET_DEF           \
(                                                                   \
    "direct_methods", py_dex_class_get_methods, NULL,               \
    "List of direct methods of the Dex class, None if none and"     \
    " None on error.",                                              \
    (void *)1                                                       \
)

#define DEX_CLASS_VIRTUAL_METHODS_ATTRIB PYTHON_GETSET_DEF          \
(                                                                   \
    "virtual_methods", py_dex_class_get_methods, NULL,              \
    "List of virtual methods of the Dex class, None if none and"    \
    " None on error.",                                              \
    NULL                                                            \
)

    class = G_DEX_CLASS(pygobject_get(self));

    virtual = (closure == NULL);

    count = g_dex_class_count_methods(class, virtual);

    if (count == 0)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
    {
        result = PyTuple_New(count);

        for (i = 0; i < count; i++)
        {
            method = g_dex_class_get_method(class, virtual, i);

            if (method == NULL)
            {
                meth = Py_None;
                Py_INCREF(meth);
            }
            else
            {
                meth = pygobject_new(G_OBJECT(method));
                g_object_unref(G_OBJECT(method));
            }

            PyTuple_SetItem(result, i, meth);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Retrouve si possible le nom du fichier source d'une classe.  *
*                                                                             *
*  Retour      : Nom du fichier trouvé ou None si aucun.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_class_get_source_file(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexClass *class;                       /* Version native              */
    const char *file;                       /* Fichier à l'origine du code */

#define DEX_CLASS_SOURCE_FILE_ATTRIB PYTHON_GET_DEF_FULL        \
(                                                                   \
    source_file, py_dex_class,                                  \
    "Source file of the Dex class, None on error."                                               \
)

    class = G_DEX_CLASS(pygobject_get(self));

    file = g_dex_class_get_source_file(class);

    if (file == NULL)
    {
        result = Py_None;
        Py_INCREF(result);
    }

    else
        result = PyUnicode_FromString(file);

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

PyTypeObject *get_python_dex_class_type(void)
{
    static PyMethodDef py_dex_class_methods[] = {
        { NULL }
    };

    static PyGetSetDef py_dex_class_getseters[] = {
        DEX_CLASS_DEFINITION_ATTRIB,
        DEX_CLASS_DATA_ATTRIB,
        DEX_CLASS_TYPE_ATTRIB,
        DEX_CLASS_SUPER_ATTRIB,
        DEX_CLASS_INTERFACES_ATTRIB,
        DEX_CLASS_STATIC_FIELDS_ATTRIB,
        DEX_CLASS_INSTANCE_FIELDS_ATTRIB,
        DEX_CLASS_DIRECT_METHODS_ATTRIB,
        DEX_CLASS_VIRTUAL_METHODS_ATTRIB,
        DEX_CLASS_SOURCE_FILE_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_dex_class_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.dex.DexClass",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = DEX_CLASS_DOC,

        .tp_methods     = py_dex_class_methods,
        .tp_getset      = py_dex_class_getseters

    };

    return &py_dex_class_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.dex.DexClass'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_dex_class(PyObject *module)
{
    PyTypeObject *type;                     /* Type Python 'DexClass'      */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_dex_class_type();

    dict = PyModule_GetDict(module);

    if (!register_class_for_pygobject(dict, G_TYPE_DEX_CLASS, type))
        return false;

    return true;

}
