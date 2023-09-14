
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pool.c - équivalent Python du fichier "plugins/dex/pool.c"
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


#include "pool.h"


#include <pygobject.h>


#include <plugins/pychrysalide/helpers.h>


#include "translate.h"
#include "../pool.h"



/* Reconstitue les éléments bruts d'un type Dex. */
static PyObject *py_dex_pool_get_raw_type(PyObject *, PyObject *);

/* Reconstitue les éléments bruts d'un champ Dex. */
static PyObject *py_dex_pool_get_raw_field(PyObject *, PyObject *);

/* Reconstitue les éléments bruts d'une routine Dex. */
static PyObject *py_dex_pool_get_raw_prototype(PyObject *, PyObject *);

/* Reconstitue les éléments bruts d'une méthode Dex. */
static PyObject *py_dex_pool_get_raw_method(PyObject *, PyObject *);

/* Reconstitue les éléments bruts d'une classe Dex. */
static PyObject *py_dex_pool_get_raw_class(PyObject *, PyObject *);

/* Fournit la liste de toutes les chaînes de la table globale. */
static PyObject *py_dex_pool_get_strings(PyObject *, void *);

/* Fournit la liste de tous les types de la table globale. */
static PyObject *py_dex_pool_get_types(PyObject *, void *);

/* Fournit la liste de tous les champs de la table globale. */
static PyObject *py_dex_pool_get_fields(PyObject *, void *);

/* Fournit la liste de tous les prototypes de la table globale. */
static PyObject *py_dex_pool_get_prototypes(PyObject *, void *);

/* Fournit la liste de toutes les méthodes de la table globale. */
static PyObject *py_dex_pool_get_methods(PyObject *, void *);

/* Fournit la liste de toutes les classes de la table globale. */
static PyObject *py_dex_pool_get_classes(PyObject *, void *);



#define DEX_POOL_DOC                                                    \
    "DexPool is the class collecting all resources of a Dex format."    \
    "\n"                                                                \
    "The pool is populated when the format gets analyzed."



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet représentant une table de ressources Dex.       *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Reconstitue les éléments bruts d'un type Dex.                *
*                                                                             *
*  Retour      : Instance mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_pool_get_raw_type(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned int index;                     /* Indice de l'élément visé    */
    int ret;                                /* Bilan de lecture des args.  */
    GDexPool *pool;                         /* Table de ressources Dex     */
    type_id_item type_id;                 /* Elément à transmettre       */
    bool status;                            /* Bilan de l'opération        */

#define DEX_POOL_GET_RAW_TYPE_METHOD PYTHON_METHOD_DEF                                      \
(                                                                                           \
    get_raw_type, "$self, index, /",                                                        \
    METH_VARARGS, py_dex_pool,                                                              \
    "Provide the raw data of a given type in the Dex pool as a pychrysalide.StructObject"   \
    " instance."                                                                            \
    "\n"                                                                                    \
    "Indexes start at 0.\n"                                                                 \
    "\n"                                                                                    \
    "All the fields are extracted from the Dex *type_id_item* structure:\n"                 \
    "* descriptor_idx: index into the string_ids list for the descriptor string.\n"         \
    "\n"                                                                                    \
    "In case of error, the function returns None."                                          \
)

    ret = PyArg_ParseTuple(args, "I", &index);
    if (!ret) return NULL;

    pool = G_DEX_POOL(pygobject_get(self));

    status = g_dex_pool_get_raw_type(pool, index, &type_id);

    if (status)
        result = translate_dex_type_id_to_python(&type_id);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet représentant une table de ressources Dex.       *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Reconstitue les éléments bruts d'un champ Dex.               *
*                                                                             *
*  Retour      : Instance mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_pool_get_raw_field(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned int index;                     /* Indice de l'élément visé    */
    int ret;                                /* Bilan de lecture des args.  */
    GDexPool *pool;                         /* Table de ressources Dex     */
    field_id_item field_id;                 /* Elément à transmettre       */
    bool status;                            /* Bilan de l'opération        */

#define DEX_POOL_GET_RAW_FIELD_METHOD PYTHON_METHOD_DEF                                     \
(                                                                                           \
    get_raw_field, "$self, index, /",                                                       \
    METH_VARARGS, py_dex_pool,                                                              \
    "Provide the raw data of a given field in the Dex pool as a pychrysalide.StructObject"  \
    " instance."                                                                            \
    "\n"                                                                                    \
    "Indexes start at 0.\n"                                                                 \
    "\n"                                                                                    \
    "All the fields are extracted from the Dex *field_id_item* structure:\n"                \
    "* class_idx: index into the type_ids list for the definer of the field ;\n"            \
    "* type_idx: index into the type_ids list for the type of the field ;\n"                \
    "* name_idx: index into the string_ids list for the name of the field.\n"               \
    "\n"                                                                                    \
    "In case of error, the function returns None."                                          \
)

    ret = PyArg_ParseTuple(args, "I", &index);
    if (!ret) return NULL;

    pool = G_DEX_POOL(pygobject_get(self));

    status = g_dex_pool_get_raw_field(pool, index, &field_id);

    if (status)
        result = translate_dex_field_id_to_python(&field_id);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet représentant une table de ressources Dex.       *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Reconstitue les éléments bruts d'une routine Dex.            *
*                                                                             *
*  Retour      : Instance mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_pool_get_raw_prototype(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned int index;                     /* Indice de l'élément visé    */
    int ret;                                /* Bilan de lecture des args.  */
    GDexPool *pool;                         /* Table de ressources Dex     */
    proto_id_item proto_id;                 /* Elément à transmettre       */
    bool status;                            /* Bilan de l'opération        */

#define DEX_POOL_GET_RAW_PROTOTYPE_METHOD PYTHON_METHOD_DEF                                     \
(                                                                                               \
    get_raw_prototype, "$self, index, /",                                                       \
    METH_VARARGS, py_dex_pool,                                                                  \
    "Provide the raw data of a given prototype in the Dex pool as a pychrysalide.StructObject"  \
    " instance."                                                                                \
    "\n"                                                                                        \
    "Indexes start at 0.\n"                                                                     \
    "\n"                                                                                        \
    "All the fields are extracted from the Dex *proto_id_item* structure:\n"                    \
    "* shorty_idx: index into the *string_ids* list for the short-form descriptor string ;\n"   \
    "* return_type_idx: index into the *type_ids* list for the return type ;\n"                 \
    "* parameters_off: offset from the start of the Dex file to the list of parameter types."   \
    "\n"                                                                                        \
    "In case of error, the function returns None."                                              \
)

    ret = PyArg_ParseTuple(args, "I", &index);
    if (!ret) return NULL;

    pool = G_DEX_POOL(pygobject_get(self));

    status = g_dex_pool_get_raw_prototype(pool, index, &proto_id);

    if (status)
        result = translate_dex_proto_id_to_python(&proto_id);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet représentant une table de ressources Dex.       *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Reconstitue les éléments bruts d'une méthode Dex.            *
*                                                                             *
*  Retour      : Instance mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_pool_get_raw_method(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned int index;                     /* Indice de l'élément visé    */
    int ret;                                /* Bilan de lecture des args.  */
    GDexPool *pool;                         /* Table de ressources Dex     */
    method_id_item method_id;               /* Elément à transmettre       */
    bool status;                            /* Bilan de l'opération        */

#define DEX_POOL_GET_RAW_METHOD_METHOD PYTHON_METHOD_DEF                                    \
(                                                                                           \
    get_raw_method, "$self, index, /",                                                      \
    METH_VARARGS, py_dex_pool,                                                              \
    "Provide the raw data of a given method in the Dex pool as a pychrysalide.StructObject" \
    " instance."                                                                            \
    "\n"                                                                                    \
    "Indexes start at 0.\n"                                                                 \
    "\n"                                                                                    \
    "All the fields are extracted from the Dex *method_id_item* structure:\n"               \
    "* class_idx: index into the type_ids list for the definer of the method ;\n"           \
    "* proto_idx: index into the proto_ids list for the prototype of the method ;\n"        \
    "* name_idx: index into the string_ids list for the name of the method.\n"              \
    "\n"                                                                                    \
    "In case of error, the function returns None."                                          \
)

    ret = PyArg_ParseTuple(args, "I", &index);
    if (!ret) return NULL;

    pool = G_DEX_POOL(pygobject_get(self));

    status = g_dex_pool_get_raw_method(pool, index, &method_id);

    if (status)
        result = translate_dex_method_id_to_python(&method_id);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet représentant une table de ressources Dex.       *
*                args = arguments fournis pour l'opération.                   *
*                                                                             *
*  Description : Reconstitue les éléments bruts d'une classe Dex.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_pool_get_raw_class(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    unsigned int index;                     /* Indice de l'élément visé    */
    int ret;                                /* Bilan de lecture des args.  */
    GDexPool *pool;                         /* Table de ressources Dex     */
    class_def_item class_def;               /* Elément à transmettre       */
    bool status;                            /* Bilan de l'opération        */

#define DEX_POOL_GET_RAW_CLASS_METHOD PYTHON_METHOD_DEF                                         \
(                                                                                               \
    get_raw_class, "$self, index, /",                                                           \
    METH_VARARGS, py_dex_pool,                                                                  \
    "Provide the raw data of a given class in the Dex pool as a pychrysalide.StructObject"      \
    " instance."                                                                                \
    "\n"                                                                                        \
    "Indexes start at 0.\n"                                                                     \
    "\n"                                                                                        \
    "All the fields are extracted from the Dex *class_def_item* structure:\n"                   \
    "* class_idx: index into the type_ids list for this class ;\n"                              \
    "* access_flags: access flags for the class (public, final, etc.) ;\n"                      \
    "* superclass_idx: index into the type_ids list for the superclass, or the constant value"  \
    " NO_INDEX if the class has no superclass ;\n"                                              \
    "* interfaces_off: offset from the start of the file to the list of interfaces, or 0"       \
    " if there are none ;\n"                                                                    \
    "* source_file_idx: index into the string_ids list for the name of the file containing"     \
    " the original source for (at least most of) this class, or the special value NO_INDEX to"  \
    " represent a lack of this information ;\n"                                                 \
    "* annotations_off: offset from the start of the file to the annotations structure, or 0"   \
    " if there are no annotation ;\n"                                                           \
    "* class_data_off: offset from the start of the file to the associated class data, or 0"    \
    " if there is no class data ;\n"                                                            \
    "* static_values_off: offset from the start of the file to the list of initial values"      \
    " for static fields, or 0 if there are none.\n"                                             \
    "\n"                                                                                        \
    "In case of error, the function returns None."                                              \
)

    ret = PyArg_ParseTuple(args, "I", &index);
    if (!ret) return NULL;

    pool = G_DEX_POOL(pygobject_get(self));

    status = g_dex_pool_get_raw_class(pool, index, &class_def);

    if (status)
        result = translate_dex_class_definition_to_python(&class_def);

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
*  Description : Fournit la liste de toutes les chaînes de la table globale.  *
*                                                                             *
*  Retour      : Liste vide ou remplie de chaînes.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_pool_get_strings(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexPool *pool;                         /* Version native              */
    uint32_t count;                         /* Nombre d'éléments à traiter */
    uint32_t i;                             /* Boucle de parcours          */
    const char *string;                     /* Chaîne à intégrer           */
    PyObject *str;                          /* Chaîne au format Python     */

#define DEX_POOL_STRINGS_ATTRIB PYTHON_GET_DEF_FULL                         \
(                                                                           \
    strings, py_dex_pool,                                                   \
    "Strings inside the Dex pool."                                          \
    "\n"                                                                    \
    "These objects are the Chrysalide version of all *string_id_item*"      \
    " structures stored in the Dex format header."                          \
)

    pool = G_DEX_POOL(pygobject_get(self));

    count = g_dex_pool_count_strings(pool);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        string = g_dex_pool_get_string(pool, i, NULL, NULL);

        if (string == NULL)
        {
            str = Py_None;
            Py_INCREF(str);
        }

        else
            str = PyUnicode_FromString(string);

        PyTuple_SetItem(result, i, str);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la liste de tous les types de la table globale.      *
*                                                                             *
*  Retour      : Liste vide ou remplie de types.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_pool_get_types(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexPool *pool;                         /* Version native              */
    uint32_t count;                         /* Nombre d'éléments à traiter */
    uint32_t i;                             /* Boucle de parcours          */
    GDataType *type;                        /* Type à intégrer             */
    PyObject *tp;                           /* Type au format Python       */

#define DEX_POOL_TYPES_ATTRIB PYTHON_GET_DEF_FULL                           \
(                                                                           \
    types, py_dex_pool,                                                     \
    "Types inside the Dex pool."                                            \
    "\n"                                                                    \
    "These objects are the Chrysalide version of all *type_id_item*"        \
    " structures stored in the Dex format header."                          \
)

    pool = G_DEX_POOL(pygobject_get(self));

    count = g_dex_pool_count_types(pool);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        type = g_dex_pool_get_type_(pool, i);

        if (type == NULL)
        {
            tp = Py_None;
            Py_INCREF(tp);
        }

        else
        {
            tp = pygobject_new(G_OBJECT(type));
            g_object_unref(type);
        }

        PyTuple_SetItem(result, i, tp);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la liste de tous les champs de la table globale.     *
*                                                                             *
*  Retour      : Liste vide ou remplie de méthodes.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_pool_get_fields(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexPool *pool;                         /* Version native              */
    uint32_t count;                         /* Nombre d'éléments à traiter */
    uint32_t i;                             /* Boucle de parcours          */
    GBinVariable *variable;                 /* Champ à intégrer            */
    PyObject *var;                          /* Champ au format Python      */

#define DEX_POOL_FIELDS_ATTRIB PYTHON_GET_DEF_FULL                          \
(                                                                           \
    fields, py_dex_pool,                                                    \
    "Fields inside the Dex pool."                                           \
    "\n"                                                                    \
    "These objects are the Chrysalide version of all *field_id_item*"       \
    " structures stored in the Dex format header."                          \
)

    pool = G_DEX_POOL(pygobject_get(self));

    count = g_dex_pool_count_fields(pool);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        variable = g_dex_pool_get_field(pool, i);

        if (variable == NULL)
        {
            var = Py_None;
            Py_INCREF(var);
        }

        else
        {
            var = pygobject_new(G_OBJECT(variable));
            g_object_unref(variable);
        }

        PyTuple_SetItem(result, i, var);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la liste de tous les prototypes de la table globale. *
*                                                                             *
*  Retour      : Liste vide ou remplie de méthodes.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_pool_get_prototypes(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexPool *pool;                         /* Version native              */
    uint32_t count;                         /* Nombre d'éléments à traiter */
    uint32_t i;                             /* Boucle de parcours          */
    GBinRoutine *routine;                   /* Routine à intégrer          */
    PyObject *rtn;                          /* Routine au format Python    */

#define DEX_POOL_PROTOTYPES_ATTRIB PYTHON_GET_DEF_FULL                      \
(                                                                           \
    prototypes, py_dex_pool,                                                \
    "Prototypes inside the Dex pool."                                       \
    "\n"                                                                    \
    "These objects are the Chrysalide version of all *proto_id_item*"       \
    " structures stored in the Dex format header."                          \
)

    pool = G_DEX_POOL(pygobject_get(self));

    count = g_dex_pool_count_prototypes(pool);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        routine = g_dex_pool_get_prototype(pool, i);

        if (routine == NULL)
        {
            rtn = Py_None;
            Py_INCREF(rtn);
        }

        else
        {
            rtn = pygobject_new(G_OBJECT(routine));
            g_object_unref(routine);
        }

        PyTuple_SetItem(result, i, rtn);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la liste de toutes les méthodes de la table globale. *
*                                                                             *
*  Retour      : Liste vide ou remplie de méthodes.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_pool_get_methods(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexPool *pool;                         /* Version native              */
    uint32_t count;                         /* Nombre d'éléments à traiter */
    uint32_t i;                             /* Boucle de parcours          */
    GDexMethod *method;                     /* Méthode à intégrer          */
    PyObject *meth;                         /* Méthode au format Python    */

#define DEX_POOL_METHODS_ATTRIB PYTHON_GET_DEF_FULL                         \
(                                                                           \
    methods, py_dex_pool,                                                   \
    "Methods inside the Dex pool."                                          \
    "\n"                                                                    \
    "These objects are the Chrysalide version of all *method_id_item*"      \
    " structures stored in the Dex format header."                          \
)

    pool = G_DEX_POOL(pygobject_get(self));

    count = g_dex_pool_count_methods(pool);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        method = g_dex_pool_get_method(pool, i);

        if (method == NULL)
        {
            meth = Py_None;
            Py_INCREF(meth);
        }

        else
        {
            meth = pygobject_new(G_OBJECT(method));
            g_object_unref(method);
        }

        PyTuple_SetItem(result, i, meth);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la liste de toutes les classes de la table globale.  *
*                                                                             *
*  Retour      : Liste vide ou remplie de classes.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_dex_pool_get_classes(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GDexPool *pool;                         /* Version native              */
    size_t count;                           /* Nombre d'éléments à traiter */
    size_t i;                               /* Boucle de parcours          */
    GDexClass *class;                       /* Classe du format à intégrer */

#define DEX_POOL_CLASSES_ATTRIB PYTHON_GET_DEF_FULL                         \
(                                                                           \
    classes, py_dex_pool,                                                   \
    "Classes inside the Dex pool."                                          \
    "\n"                                                                    \
    "These objects are the Chrysalide version of all *class_def_item*"      \
    " structures stored in the Dex format header."                          \
)

    pool = G_DEX_POOL(pygobject_get(self));

    count = g_dex_pool_count_classes(pool);

    result = PyTuple_New(count);

    for (i = 0; i < count; i++)
    {
        class = g_dex_pool_get_class(pool, i);
        assert(class != NULL);

        PyTuple_SetItem(result, i, pygobject_new(G_OBJECT(class)));

        g_object_unref(G_OBJECT(class));

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

PyTypeObject *get_python_dex_pool_type(void)
{
    static PyMethodDef py_dex_pool_methods[] = {
        DEX_POOL_GET_RAW_TYPE_METHOD,
        DEX_POOL_GET_RAW_FIELD_METHOD,
        DEX_POOL_GET_RAW_PROTOTYPE_METHOD,
        DEX_POOL_GET_RAW_METHOD_METHOD,
        DEX_POOL_GET_RAW_CLASS_METHOD,
        { NULL }
    };

    static PyGetSetDef py_dex_pool_getseters[] = {
        DEX_POOL_STRINGS_ATTRIB,
        DEX_POOL_TYPES_ATTRIB,
        DEX_POOL_FIELDS_ATTRIB,
        DEX_POOL_METHODS_ATTRIB,
        DEX_POOL_PROTOTYPES_ATTRIB,
        DEX_POOL_CLASSES_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_dex_pool_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.format.dex.DexPool",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = DEX_POOL_DOC,

        .tp_methods     = py_dex_pool_methods,
        .tp_getset      = py_dex_pool_getseters

    };

    return &py_dex_pool_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.format.dex.DexPool'.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_dex_pool(PyObject *module)
{
    PyTypeObject *type;                     /* Type Python 'DexPool'       */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_dex_pool_type();

    dict = PyModule_GetDict(module);

    if (!register_class_for_pygobject(dict, G_TYPE_DEX_POOL, type))
        return false;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en table de ressources pour format Dex.   *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_dex_pool(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_dex_pool_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to loaded binary");
            break;

        case 1:
            *((GDexPool **)dst) = G_DEX_POOL(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
