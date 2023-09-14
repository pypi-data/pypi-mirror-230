
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helpers.h - prototypes pour la simplification des interactions de base avec Python
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _PLUGINS_PYCHRYSALIDE_HELPERS_H
#define _PLUGINS_PYCHRYSALIDE_HELPERS_H


#include <Python.h>
#include <assert.h>
#include <glib-object.h>
#include <stdbool.h>
#ifdef INCLUDE_GTK_SUPPORT
#   include <gdk/gdk.h>
#endif



/* ---------------------- ACCELERATEURS POUR PYTHON UNIQUEMENT ---------------------- */


/* Traduit pour Python le bilan d'une comparaison riche. */
PyObject *status_to_rich_cmp_state(int, int);

/* Tente de convertir en élément appelable. */
int convert_to_callable(PyObject *, void *);

/* Indique si une routine Python existe ou non. */
bool has_python_method(PyObject *, const char *);

/* Appelle une routine Python. */
PyObject *run_python_method(PyObject *, const char *, PyObject *);



/* ---------------------------- MISE EN PLACE DE MODULES ---------------------------- */


/* Met en place un nouveau module Python. */
PyObject *build_python_module(PyObject *, PyModuleDef *);

/* Met en place une série de méthodes pour un module Python. */
bool register_python_module_methods(PyObject *, PyMethodDef *);

/* Met en place un objet au sein d'un module Python. */
bool register_python_module_object(PyObject *, PyTypeObject *);



/* --------------------------- CONFORTS CIBLANT PYGOBJECT --------------------------- */


/**
 * Aide à la définition de documentation pour Python.
 */

#define PYTHON_METHOD_DEF(name, args, flags, base, doc) \
    {                                                   \
        #name, (PyCFunction)base ## _ ## name,          \
        flags,                                          \
        #name "(" args ")\n--\n\n" doc                  \
    }

#define PYTHON_WRAPPER_DEF(name, args, flags, doc)      \
    {                                                   \
        #name, (PyCFunction)not_yet_implemented_method, \
        flags,                                          \
        #name "(" args ")\n--\n\n" doc                  \
    }

#define PYTHON_WRAPPER_DEF_WITH(name, args, flags, defcb, doc)  \
    {                                                           \
        #name, (PyCFunction)defcb,                              \
        flags,                                                  \
        #name "(" args ")\n--\n\n" doc                          \
    }

#define PYTHON_VOID_WRAPPER_DEF(name, args, flags, doc) \
    PYTHON_WRAPPER_DEF_WITH(name, args, flags, py_return_none, doc)

#define PYTHON_FALSE_WRAPPER_DEF(name, args, flags, doc) \
    PYTHON_WRAPPER_DEF_WITH(name, args, flags, py_return_false, doc)

#define PYTHON_TRUE_WRAPPER_DEF(name, args, flags, doc) \
    PYTHON_WRAPPER_DEF_WITH(name, args, flags, py_return_true, doc)

/**
 * Il ne semble pas exister de moyen de déterminer
 * si un attribut est inscriptible de façon introspective...
 * L'indication est donc placée dans la documentation.
 */
#define ATTRIB_RO "(ro) "
#define ATTRIB_WO "(wo) "
#define ATTRIB_RW "(rw) "

#define PYTHON_GETSET_DEF(name, get, set, doc, closure) \
    {                                                   \
        name, get, set,                                 \
        doc,                                            \
        closure                                         \
    }

#define PYTHON_CAN_DEF_FULL(name, base, doc)            \
    PYTHON_GETSET_DEF("can_" #name, base ## _can_ ## name, NULL, ATTRIB_RO doc, NULL)

#define PYTHON_IS_DEF_FULL(name, base, doc)             \
    PYTHON_GETSET_DEF("is_" #name, base ## _is_ ## name, NULL, ATTRIB_RO doc, NULL)

#define PYTHON_HAS_DEF_FULL(name, base, doc)            \
    PYTHON_GETSET_DEF(#name, base ## _has_ ## name, NULL, ATTRIB_RO doc, NULL)

#define PYTHON_RAWGET_DEF_FULL(name, base, doc)         \
    PYTHON_GETSET_DEF(#name, base ## _ ## name, NULL, ATTRIB_RO doc, NULL)

#define PYTHON_GET_DEF_FULL(name, base, doc)            \
    PYTHON_GETSET_DEF(#name, base ## _get_ ## name, NULL, ATTRIB_RO doc, NULL)

#define PYTHON_GETSET_DEF_FULL(name, base, doc)         \
    PYTHON_GETSET_DEF(#name, base ## _get_ ## name, base ## _set_ ## name, ATTRIB_RW doc, NULL)

#define PYTHON_GETTER_WRAPPER_DEF(name, doc)    \
    {                                           \
        #name,                                  \
        (getter)not_yet_implemented_getter,     \
         NULL,                                  \
         ATTRIB_RO doc, NULL                    \
    }

/**
 * Quelque chose est mal fait au niveau de l'abstraction GObject.
 * Du coup, Py_TPFLAGS_IS_ABSTRACT n'est pas pris en compte.
 * On force alors la méthode de base pour obtenir un traitement correct.
 *
 * Cf. http://stackoverflow.com/questions/20432335/can-python-abstract-base-classes-inherit-from-c-extensions
 */
#define APPLY_ABSTRACT_FLAG(tp) tp->tp_new = PyBaseObject_Type.tp_new


/* Accompagne la création d'une instance dérivée en Python. */
PyObject *python_constructor_with_dynamic_gtype(PyTypeObject *, GType, PyObject *, PyObject *);

/* Accompagne la création d'une instance dérivée en Python. */
PyObject *python_abstract_constructor_with_dynamic_gtype(PyTypeObject *, GType, GClassInitFunc, PyObject *, PyObject *);


#define CREATE_DYN_CONSTRUCTOR(pyname, gbase)                                                       \
static PyObject *py_ ## pyname ## _new(PyTypeObject *, PyObject *, PyObject *);                     \
static PyObject *py_ ## pyname ## _new(PyTypeObject *type, PyObject *args, PyObject *kwds)          \
{                                                                                                   \
    PyObject *result;                       /* Objet à retourner           */                       \
    result = python_constructor_with_dynamic_gtype(type, gbase, args, kwds);                        \
    return result;                                                                                  \
}


#define CREATE_DYN_ABSTRACT_CONSTRUCTOR(pyname, gbase, cinit)                                       \
static PyObject *py_ ## pyname ## _new(PyTypeObject *, PyObject *, PyObject *);                     \
static PyObject *py_ ## pyname ## _new(PyTypeObject *type, PyObject *args, PyObject *kwds)          \
{                                                                                                   \
    PyObject *result;                       /* Objet à retourner           */                       \
    result = python_abstract_constructor_with_dynamic_gtype(type, gbase, (GClassInitFunc)cinit,     \
                                                            args, kwds);                            \
    return result;                                                                                  \
}


/* Marque l'interdiction d'une instanciation depuis Python. */
PyObject *no_python_constructor_allowed(PyTypeObject *, PyObject *, PyObject *);

/* Marque l'absence d'implémentation pour une méthode donnée. */
PyObject *not_yet_implemented_method(PyObject *, PyObject *);

/* Retourne toujours rien. */
PyObject *py_return_none(PyObject *, PyObject *);

/* Retourne toujours faux. */
PyObject *py_return_false(PyObject *, PyObject *);

/* Retourne toujours vrai. */
PyObject *py_return_true(PyObject *, PyObject *);

/* Marque l'absence d'implémentation pour un attribut donné. */
PyObject *not_yet_implemented_getter(PyObject *, void *);

/* Définit dans le tas de Python un nouveau type. */
PyTypeObject *define_python_dynamic_type(const PyTypeObject *);


/**
 * pygobject_new() prend en compte les références flottantes au moment de la
 * construction d'un objet Python.
 *
 * Et cela pose problème dans la mesure où on ne veut pas transférer à Python
 * la propriété d'un objet, même si celui-ci a une référence flotante.
 *
 * Dans les faits, c'est toujours uniquement le cas pour les composants graphiques,
 * puisque GtkWidget hérite de GInitiallyUnowned, qui force le décompte flottant
 * dans g_initially_unowned_init().
 */
#define new_pygobject_widget(o)             \
    ({                                      \
        if (g_object_is_floating(o))        \
            g_object_ref_sink(o);           \
        pygobject_new(G_OBJECT(o));         \
    })


/* Enregistre correctement une surcouche de conversion GObject. */
bool register_class_for_pygobject(PyObject *, GType, PyTypeObject *);

/* Enregistre correctement une interface GObject pour Python. */
bool register_interface_for_pygobject(PyObject *, GType, PyTypeObject *, const GInterfaceInfo *);

/* Enregistre un type Python dérivant d'un type GLib dynamique. */
bool register_class_for_dynamic_pygobject(GType, PyTypeObject *);

/* Fait suivre à la partie GObject une initialisation nouvelle. */
int forward_pygobjet_init(PyObject *);

/* Tente de convertir en valeur GType. */
int convert_to_gtype(PyObject *, void *);

/* Tente de convertir en instance GObject. */
int convert_to_gobject(PyObject *, void *);

#ifdef INCLUDE_GTK_SUPPORT

/* Tente de convertir en instance de composant GTK. */
int convert_to_gtk_widget(PyObject *, void *);

/* Tente de convertir en instance de conteneur GTK. */
int convert_to_gtk_container(PyObject *, void *);

#endif


#if !defined(INCLUDE_GTK_SUPPORT) && !defined(HOMEMADE_RGBA)

#   define HOMEMADE_RGBA

/**
 * Copie depuis /usr/include/gtk-3.0/gdk/gdkrgba.h
 */
typedef struct _GdkRGBA
{
    gdouble red;
    gdouble green;
    gdouble blue;
    gdouble alpha;

} GdkRGBA;

#endif


/* Construit un objet Python pour une couleur RGBA. */
PyObject *create_gdk_rgba(const GdkRGBA *);

/* Tente de convertir en instance de couleur RGBA. */
int convert_to_gdk_rgba(PyObject *, void *);



/* ----------------------- TRANSFERT DES VALEURS CONSTANTES ------------------------- */


/**
 * Aides à la traduction.
 */

#define ADD_FIELD_TRANSLATION(dict, name, attrib)                   \
    ({                                                              \
        int __ret;                                                  \
        bool __status;                                              \
        __ret = PyDict_SetItemString(dict, name, attrib);           \
        Py_DECREF(attrib);                                          \
        __status = (__ret == 0);                                    \
        __status;                                                   \
    })


#define TRANSLATE_BOOLEAN_FIELD(dict, base, field)                  \
    ({                                                              \
        PyObject *__attrib;                                         \
        __attrib = (base->field ? Py_True : Py_False);              \
        Py_INCREF(__attrib);                                        \
        ADD_FIELD_TRANSLATION(dict, #field, __attrib);              \
    })


#define TRANSLATE_NUMERIC_FIELD(dict, base, field)                  \
    ({                                                              \
        PyObject *__attrib;                                         \
        __attrib = PyLong_FromUnsignedLongLong(base->field);        \
        Py_INCREF(__attrib);                                        \
        ADD_FIELD_TRANSLATION(dict, #field, __attrib);              \
    })


#define RETRIEVE_NUMERIC_FIELD(dict, base, field)                   \
    ({                                                              \
        bool __status;                                              \
        PyObject *__attrib;                                         \
        __status = false;                                           \
        __attrib = PyDict_GetItemString(dict, #field);              \
        if (__attrib != NULL && PyLong_Check(__attrib))             \
        {                                                           \
            base->field = PyLong_AsUnsignedLongLong(__attrib);      \
            __status = (PyErr_Occurred() == NULL);                  \
        }                                                           \
        __status;                                                   \
    })


#define TRANSLATE_BYTES_FIELD(dict, base, field, len)               \
    ({                                                              \
        void *__data;                                               \
        PyObject *__attrib;                                         \
        __data = (void *)&base->field;                              \
        __attrib = PyBytes_FromStringAndSize(__data, len);          \
        Py_INCREF(__attrib);                                        \
        ADD_FIELD_TRANSLATION(dict, #field, __attrib);              \
    })


#define TRANSLATE_STRING_FIELD(dict, base, field)                   \
    ({                                                              \
        PyObject *__attrib;                                         \
        if (base->field != NULL)                                    \
            __attrib = PyUnicode_FromString(base->field);           \
        else                                                        \
        {                                                           \
            __attrib = Py_None;                                     \
            Py_INCREF(Py_None);                                     \
        }                                                           \
        ADD_FIELD_TRANSLATION(dict, #field, __attrib);              \
    })


#define TRANSLATE_ARRAY_FIELD(dict, base, field, array)             \
    ({                                                              \
        PyObject *__attrib;                                         \
        bool __status;                                              \
        __attrib = PyTuple_New(base->field ## _count);              \
        __status = ADD_FIELD_TRANSLATION(dict, #field, __attrib);   \
        if (__status)                                               \
            (*array) = __attrib;                                    \
        else                                                        \
            (*array) = NULL;                                        \
        __status;                                                   \
    })


/* Simplification d'un ajout de constante pour l'appelant */
#define add_const_to_group(d, n, v)                         \
    ({                                                      \
        bool __result;                                      \
        PyObject *__val;                                    \
        int __ret;                                          \
        __val = PyLong_FromUnsignedLong(v);                 \
        if (__val == NULL)                                  \
            __result = false;                               \
        else                                                \
        {                                                   \
            __ret = PyDict_SetItemString(d, n, __val);      \
            Py_DECREF(__val);                               \
            __result = (__ret == 0);                        \
        }                                                   \
        __result;                                           \
    })

/* Officialise un groupe de constantes avec sémentique. */
PyObject *_attach_constants_group(const char *, PyObject *, bool, const char *, PyObject *, const char *);

#define attach_constants_group_to_type(type, flags, name, values, doc)                      \
    ({                                                                                      \
        bool __result;                                                                      \
        PyObject *__new;                                                                    \
        __new = _attach_constants_group(type->tp_name, type->tp_dict, flags, name, values,  \
                                        doc);                                               \
        __result = (__new != NULL);                                                         \
        Py_XDECREF(__new);                                                                  \
        __result;                                                                           \
    })

#define attach_constants_group_to_module(mod, flags, name, values, doc)                     \
    ({                                                                                      \
        bool __result;                                                                      \
        const char *__owner;                                                                \
        PyObject *__dict;                                                                   \
        PyObject *__new;                                                                    \
        __owner = PyModule_GetName(mod);                                                    \
        __dict = PyModule_GetDict(mod);                                                     \
        __new = _attach_constants_group(__owner, __dict, flags, name, values, doc);         \
        __result = (__new != NULL);                                                         \
        Py_XDECREF(__new);                                                                  \
        __result;                                                                           \
    })

/* Officialise un groupe de constantes avec lien GLib. */
PyObject *_attach_constants_group_with_pyg_enum(const char *, PyObject *, bool, const char *, PyObject *, const char *, GType);


#define attach_constants_group_to_type_with_pyg_enum(type, flags, name, values, doc, gtype) \
    ({                                                                                      \
        bool __result;                                                                      \
        PyObject *__new;                                                                    \
        __new = _attach_constants_group_with_pyg_enum(type->tp_name, type->tp_dict, flags,  \
                                                      name, values, doc, gtype);            \
        __result = (__new != NULL);                                                         \
        Py_XDECREF(__new);                                                                  \
        __result;                                                                           \
    })

/* Traduit une valeur constante C en équivalent Python. */
PyObject *_cast_with_constants_group(const char *, const char *, unsigned long);

#define cast_with_constants_group_from_type(type, name, value) \
    _cast_with_constants_group(type->tp_name, name, value)

#define cast_with_constants_group_from_module(owner, name, value) \
    _cast_with_constants_group(owner, name, value)

/* Officialise un groupe de constantes de chaînes de caractères. */
bool _create_string_constants_group(PyObject *, const char *, const char *, PyObject **);

#define create_string_constants_group_to_type(type, name, doc, out) \
    _create_string_constants_group(type->tp_dict, name, doc, out)

#define create_string_constants_group_to_module(mod, name, doc, out)        \
    ({                                                                      \
        bool __result;                                                      \
        PyObject *__dict;                                                   \
        __dict = PyModule_GetDict(mod);                                     \
        __result = _create_string_constants_group(__dict, name, doc, out);  \
        __result;                                                           \
    })

#define extend_string_constants_group(dict, key, str)           \
    ({                                                          \
        bool __result;                                          \
        PyObject *__str_obj;                                    \
        int __ret;                                              \
        __str_obj = PyUnicode_FromString(str);                  \
        __ret = PyDict_SetItemString(dict, key, __str_obj);     \
        Py_DECREF(__str_obj);                                   \
        __result = (__ret == 0);                                \
        __result;                                               \
    })



#endif  /* _PLUGINS_PYCHRYSALIDE_HELPERS_H */
