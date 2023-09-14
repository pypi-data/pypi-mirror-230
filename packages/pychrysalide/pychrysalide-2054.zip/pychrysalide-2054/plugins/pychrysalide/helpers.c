
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helpers.c - simplification des interactions de base avec Python
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


#include "helpers.h"


#include <assert.h>
#include <malloc.h>
#include <pygobject.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#ifdef INCLUDE_GTK_SUPPORT
#   include <gtk/gtk.h>
#endif


#include <i18n.h>
#include <common/extstr.h>
#include <plugins/dt.h>


#include "access.h"
#include "strenum.h"



/* ---------------------------- MISE EN PLACE DE MODULES ---------------------------- */


/* Ajoute une classe dans les fonctionnalités globales. */
static bool include_python_type_into_features(PyObject *, PyTypeObject *);



/* --------------------------- CONFORTS CIBLANT PYGOBJECT --------------------------- */


/* Message d'erreur affiché. */
#define NO_CONSTRUCTOR_MSG _("Chrysalide does not allow building this kind of object from Python")

/* Message d'erreur affiché puis recherché. */
#define NOT_IMPLEMENTED_ROUTINE_MSG _("Chrysalide method implementation is missing")

/* Message d'erreur affiché puis recherché. */
#define NOT_IMPLEMENTED_GETTER_MSG _("Chrysalide getter implementation is missing")


/* Détermine une documentation adaptée à un type interne. */
static void define_auto_documentation(PyTypeObject *);



/* ---------------------------------------------------------------------------------- */
/*                        ACCELERATEURS POUR PYTHON UNIQUEMENT                        */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : status = bilan de comparaison à traduire.                    *
*                op     = type de comparaison menée.                          *
*                                                                             *
*  Description : Traduit pour Python le bilan d'une comparaison riche.        *
*                                                                             *
*  Retour      : Objet Python à référencer.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *status_to_rich_cmp_state(int status, int op)
{
    PyObject *result;                       /* Bilan àretourner            */

    switch (op)
    {
        case Py_LT:
            result = status < 0 ? Py_True : Py_False;
            break;

        case Py_LE:
            result = status <= 0 ? Py_True : Py_False;
            break;

        case Py_EQ:
            result = status == 0 ? Py_True : Py_False;
            break;

        case Py_NE:
            result = status != 0 ? Py_True : Py_False;
            break;

        case Py_GT:
            result = status > 0 ? Py_True : Py_False;
            break;

        case Py_GE:
            result = status >= 0 ? Py_True : Py_False;
            break;

        default:
            result = Py_NotImplemented;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en élément appelable.                     *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_callable(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyCallable_Check(arg);

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to a callable object");
            break;

        case 1:
            *((PyObject **)dst) = arg;
            break;

        default:
            assert(false);
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = propriétaire de la routine visée.                   *
*                method = désignation de la fonction à appeler.               *
*                                                                             *
*  Description : Indique si une routine Python existe ou non.                 *
*                                                                             *
*  Retour      : Bilan de l'analyse.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool has_python_method(PyObject *module, const char *method)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *func;                         /* Fonction visée              */

    result = (PyObject_HasAttrString(module, method) == 1);

    if (result)
    {
        func = PyObject_GetAttrString(module, method);
        assert(func != NULL);

        result = PyCallable_Check(func);

        Py_DECREF(func);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = propriétaire de la routine visée.                   *
*                method = désignation de la fonction à appeler.               *
*                args   = arguments à associer à l'opération.                 *
*                                                                             *
*  Description : Appelle une routine Python.                                  *
*                                                                             *
*  Retour      : Retour obtenu ou NULL si erreur.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *run_python_method(PyObject *module, const char *method, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */
    PyObject *func;                         /* Fonction visée              */
    PyObject *type;                         /* Type d'exception levée      */
    PyObject *value;                        /* Détails particuliers        */
    PyObject *traceback;                    /* Pile d'appels de l'exception*/
    PyObject *refmsg;                       /* Message de référence        */

    assert(PyGILState_Check() == 1);

    /* Exécution */

    result = NULL;

    func = PyObject_GetAttrString(module, method);
    if (func == NULL) goto check_error;

    if (PyCallable_Check(func))
        result = PyObject_CallObject(func, args);

    Py_DECREF(func);

    /* Répercutions */

 check_error:

    PyErr_Fetch(&type, &value, &traceback);

    if (type != NULL && type == PyExc_NotImplementedError \
        && value != NULL && PyUnicode_Check(value))
    {
        refmsg = PyUnicode_FromString(NOT_IMPLEMENTED_ROUTINE_MSG);

        if (PyUnicode_Compare(value, refmsg) == 0)
        {
            Py_DECREF(value);
            value = PyUnicode_FromFormat(_("method implementation is missing for '%s'"), method);
        }

        Py_DECREF(refmsg);

    }

    PyErr_Restore(type, value, traceback);

    if (result == NULL && PyErr_Occurred() != NULL)
        PyErr_Print();

    if (result == NULL)
        Py_Exit(EXIT_FAILURE);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                              MISE EN PLACE DE MODULES                              */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                def   = définition du module à créer.                        *
*                                                                             *
*  Description : Met en place un nouveau module Python.                       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *build_python_module(PyObject *super, PyModuleDef *def)
{
    PyObject *result;                       /* Création à retourner        */
    int ret;                                /* Bilan d'un appel            */
#if PY_VERSION_HEX >= 0x03070000
    PyObject *modules;                      /* Modules de l'interpréteur   */
#endif
    char *dot;                              /* Dernier point de ce chemin  */

    result = PyModule_Create(def);
    if (result == NULL) goto quick_bad_exit;

    ret = PyState_AddModule(super, def);
    if (ret != 0) goto bad_exit;

#if PY_VERSION_HEX >= 0x03070000
    modules = PyImport_GetModuleDict();
    ret = _PyImport_FixupBuiltin(result, def->m_name, modules);
#else
    ret = _PyImport_FixupBuiltin(result, def->m_name);
#endif
    if (ret != 0) goto bad_exit;

    dot = strrchr(def->m_name, '.');
    assert(dot != NULL);

    Py_INCREF(result);
    ret = PyModule_AddObject(super, dot + 1, result);
    if (ret != 0)
    {
        Py_DECREF(result);
        goto bad_exit;
    }

    register_access_to_python_module(def->m_name, result);

    return result;

 bad_exit:

    Py_DECREF(result);

 quick_bad_exit:

    assert(false);

    return false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                defs   = définitions de méthodes pour module.                *
*                                                                             *
*  Description : Met en place une série de méthodes pour un module Python.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_module_methods(PyObject *module, PyMethodDef *defs)
{
    bool result;                            /* Bilan à retourner           */
    int ret;                                /* Bilan d'un appel            */
    PyMethodDef *iter;                      /* Boucle de parcours          */
    PyObject *features;                     /* Module à recompléter        */
    PyObject *features_dict;                /* Dictionnaire à compléter    */
    PyObject *mod_dict;                     /* Dictionnaire à consulter    */
    PyObject *item;                         /* Nouvel élément à exporter   */

    ret = PyModule_AddFunctions(module, defs);
    result = (ret == 0);

    if (result)
    {
        features = get_access_to_python_module("pychrysalide.features");

        features_dict = PyModule_GetDict(features);

        mod_dict = PyModule_GetDict(module);

        for (iter = defs; iter->ml_name != NULL && result; iter++)
        {
            item = PyDict_GetItemString(mod_dict, iter->ml_name);
            result = (item != NULL);
            assert(result);

            if (result)
            {
                Py_INCREF(item);

                ret = PyDict_SetItemString(features_dict, iter->ml_name, item);
                result = (ret == 0);
                assert(result);
            }

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dict = dictionnaire où conserver une référence au type créé. *
*                type = type dans sa version Python.                          *
*                                                                             *
*  Description : Ajoute une classe dans les fonctionnalités globales.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool include_python_type_into_features(PyObject *dict, PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *features;                     /* Module à recompléter        */
    PyObject *features_dict;                /* Dictionnaire à compléter    */
    char *name;                             /* Désignation de la classe    */
    PyObject *item;                         /* Nouvel élément à exporter   */
    int ret;                                /* Bilan d'une insertion       */

    features = get_access_to_python_module("pychrysalide.features");

    features_dict = PyModule_GetDict(features);

    name = strrchr(type->tp_name, '.');
    assert(name != NULL);

    name++;

    item = PyDict_GetItemString(dict, name);
    result = (item != NULL);
    assert(result);

    Py_INCREF(item);

    ret = PyDict_SetItemString(features_dict, name, item);
    result = (ret == 0);
    assert(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                type   = type à intégrer dans sa version Python.             *
*                                                                             *
*  Description : Met en place un objet au sein d'un module Python.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_python_module_object(PyObject *module, PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    char *name;                             /* Désignation de la classe    */
    int ret;                                /* Bilan d'un appel            */
    PyObject *dict;                         /* Dictionnaire du module      */

    name = strrchr(type->tp_name, '.');
    assert(name != NULL);

    name++;

    Py_INCREF(type);
    ret = PyModule_AddObject(module, name, (PyObject *)type);

    result = (ret == 0);

    if (!result)
        Py_DECREF(type);

    else
    {
        dict = PyModule_GetDict(module);
        result = include_python_type_into_features(dict, type);
    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                             CONFORTS CIBLANT PYGOBJECT                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : type  = type du nouvel objet à mettre en place.              *
*                gbase = type de base natif.                                  *
*                args  = éventuelle liste d'arguments.                        *
*                kwds  = éventuel dictionnaire de valeurs mises à disposition.*
*                                                                             *
*  Description : Accompagne la création d'une instance dérivée en Python.     *
*                                                                             *
*  Retour      : Nouvel objet Python mis en place ou NULL en cas d'échec.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *python_constructor_with_dynamic_gtype(PyTypeObject *type, GType gbase, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type parent version Python  */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = pygobject_lookup_class(gbase);

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(gbase, type->tp_name, NULL, NULL, NULL);

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

 simple_way:

    result = PyType_GenericNew(type, args, kwds);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type  = type du nouvel objet à mettre en place.              *
*                gbase = type de base natif.                                  *
*                cinit = procédure d'initialisation de la classe associée.    *
*                args  = éventuelle liste d'arguments.                        *
*                kwds  = éventuel dictionnaire de valeurs mises à disposition.*
*                                                                             *
*  Description : Accompagne la création d'une instance dérivée en Python.     *
*                                                                             *
*  Retour      : Nouvel objet Python mis en place ou NULL en cas d'échec.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *python_abstract_constructor_with_dynamic_gtype(PyTypeObject *type, GType gbase, GClassInitFunc cinit, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type parent version Python  */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = pygobject_lookup_class(gbase);

    if (type == base)
    {
        result = NULL;
        PyErr_Format(PyExc_RuntimeError, _("%s is an abstract class"), type->tp_name);
        goto exit;
    }

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(gbase, type->tp_name, cinit, NULL, NULL);

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
*  Paramètres  : type = type du nouvel objet à mettre en place.               *
*                args = éventuelle liste d'arguments.                         *
*                kwds = éventuel dictionnaire de valeurs mises à disposition. *
*                                                                             *
*  Description : Marque l'interdiction d'une instanciation depuis Python.     *
*                                                                             *
*  Retour      : NULL pour la levée d'exception.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *no_python_constructor_allowed(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Exception à retourner       */

    result = NULL;

    PyErr_SetString(PyExc_NotImplementedError, NO_CONSTRUCTOR_MSG);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet quelconque dont le code Python hérite.          *
*                args = série d'arguments si présents.                        *
*                                                                             *
*  Description : Marque l'absence d'implémentation pour une méthode donnée.   *
*                                                                             *
*  Retour      : NULL pour la levée d'exception.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *not_yet_implemented_method(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Exception à retourner       */

    result = NULL;

    PyErr_SetString(PyExc_NotImplementedError, NOT_IMPLEMENTED_ROUTINE_MSG);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet quelconque.                                     *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Retourne toujours rien.                                      *
*                                                                             *
*  Retour      : None.                                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_return_none(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet quelconque.                                     *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Retourne toujours faux.                                      *
*                                                                             *
*  Retour      : False.                                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_return_false(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */

    result = Py_False;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet quelconque.                                     *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Retourne toujours vrai.                                      *
*                                                                             *
*  Retour      : False.                                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_return_true(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à retourner           */

    result = Py_True;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet quelconque dont le code Python hérite.       *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Marque l'absence d'implémentation pour un attribut donné.    *
*                                                                             *
*  Retour      : NULL pour la levée d'exception.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *not_yet_implemented_getter(PyObject *self, void *closure)
{
    PyObject *result;                       /* Exception à retourner       */

    result = NULL;

    PyErr_SetString(PyExc_NotImplementedError, NOT_IMPLEMENTED_GETTER_MSG);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : otype = définition à mettre en place dynamiquement.          *
*                                                                             *
*  Description : Définit dans le tas de Python un nouveau type.               *
*                                                                             *
*  Retour      : Nouveau type prêt à emploi.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyTypeObject *define_python_dynamic_type(const PyTypeObject *otype)
{
    PyTypeObject *result;                   /* Définition créée à renvoyer */
    PyType_Slot slots[10];                  /* Emplacements pour infos     */
    PyType_Spec spec;                       /* Définition du type          */
    PyType_Slot *iter;                      /* Boucle de parcours          */
    PyObject *bases;                        /* Bases de construction       */

    bases = PyTuple_Pack(1, &PyType_Type);

    spec.name = otype->tp_name;
    spec.basicsize = otype->tp_basicsize;
    spec.flags = otype->tp_flags;
    spec.slots = slots;

    iter = &slots[0];

    if (otype->tp_doc != NULL)
    {
        iter->slot = Py_tp_doc;
        iter->pfunc = (void *)otype->tp_doc;
        iter++;
    }

    if (otype->tp_methods != NULL)
    {
        iter->slot = Py_tp_methods;
        iter->pfunc = otype->tp_methods;
        iter++;
    }

    if (otype->tp_getset != NULL)
    {
        iter->slot = Py_tp_getset;
        iter->pfunc = otype->tp_getset;
        iter++;
    }

    if (otype->tp_init != NULL)
    {
        iter->slot = Py_tp_init;
        iter->pfunc = otype->tp_init;
        iter++;
    }

    if (otype->tp_new != NULL)
    {
        iter->slot = Py_tp_new;
        iter->pfunc = otype->tp_new;
        iter++;
    }

    iter->slot = 0;

    result = (PyTypeObject *)PyType_FromSpecWithBases(&spec, bases);

    Py_DECREF(bases);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type dans sa version Python.                          *
*                                                                             *
*  Description : Détermine une documentation adaptée à un type interne.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void define_auto_documentation(PyTypeObject *type)
{
    /**
     * L'idée est ici d'éviter la documentation automatique générée par
     * pyg_object_descr_doc_get().
     */

    PyDict_SetItemString(type->tp_dict, "__doc__", PyUnicode_FromString(type->tp_doc));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dict  = dictionnaire où conserver une référence au type créé.*
*                gtype = type dans sa version GLib.                           *
*                type  = type dans sa version Python.                         *
*                                                                             *
*  Description : Enregistre correctement une surcouche de conversion GObject. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_class_for_pygobject(PyObject *dict, GType gtype, PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    GType parent_type;                      /* Type parent version GObject */
    PyTypeObject *base;                     /* Type parent version Python  */

    assert(gtype != G_TYPE_INVALID);

    /**
     * pygobject_register_class() définit type->tp_base à partir des arguments fournis,
     * puis fait appel à PyType_Ready().
     *
     * PyType_Ready() complète la définition via inherit_special() :
     *
     *    type->tp_basicsize = type->tp_base->tp_basicsize
     *
     * Cependant, il y a un appel à mro_internal() avant, qui mène à solid_base()
     * puis à extra_ivars(). Et là :
     *
     *    size_t t_size = type->tp_basicsize;
     *    size_t b_size = base->tp_basicsize;
     *
     *    assert(t_size >= b_size);
     *
     * Si le type de base est spécifié, une taille doit être indiquée.
     *
     * Et quelqu'un doit se coller à la tâche. PyGObject ne fait rien, donc...
     */

    parent_type = g_type_parent(gtype);

    base = pygobject_lookup_class(parent_type);

    if (type->tp_basicsize < base->tp_basicsize)
    {
        assert(type->tp_basicsize == 0);
        type->tp_basicsize = base->tp_basicsize;
    }

    pygobject_register_class(dict, NULL, gtype, type, NULL);

    if (PyErr_Occurred() == NULL)
        result = true;

    else
    {
        PyErr_Print();
        result = false;
    }

    assert(PyErr_Occurred() == NULL);

    /**
     * Création d'un dictionnaire complet pour la simulation d'un "import *".
     */

    if (result && startswith(type->tp_name, "pychrysalide."))
    {
        define_auto_documentation(type);

        result = include_python_type_into_features(dict, type);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dict  = dictionnaire où conserver une référence au type créé.*
*                gtype = type dans sa version GLib.                           *
*                type  = type dans sa version Python.                         *
*                                                                             *
*  Description : Enregistre correctement une interface GObject pour Python.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_interface_for_pygobject(PyObject *dict, GType gtype, PyTypeObject *type, const GInterfaceInfo *info)
{
    bool result;                            /* Bilan à retourner           */
    char *name;                             /* Désignation de la classe    */

    assert(gtype != G_TYPE_INVALID);

    name = strrchr(type->tp_name, '.');
    assert(name != NULL);

    name++;

    pyg_register_interface(dict, name, gtype, type);

    pyg_register_interface_info(gtype, info);

    if (startswith(type->tp_name, "pychrysalide."))
    {
        define_auto_documentation(type);

        result = include_python_type_into_features(dict, type);

    }
    else
        result = true;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : gtype = type dans sa version GLib.                           *
*                type  = type dans sa version Python.                         *
*                                                                             *
*  Description : Enregistre un type Python dérivant d'un type GLib dynamique. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_class_for_dynamic_pygobject(GType gtype, PyTypeObject *type)
{
    bool result;                            /* Bilan à retourner           */
    PyTypeObject *legacy_parent;            /* Type parent d'origine       */
    PyObject *sys_mod_dict;                 /* Dictionnaire des modules    */
    PyObject *modname;                      /* Nom du module du type       */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire dudit module   */
    Py_ssize_t i;                           /* Boucle de parcours          */
    PyObject *mro_base;                     /* Base finale effective       */
    GType itype;                            /* Type d'interface implémentée*/
    GQuark pyginterface_info_key;           /* Clef d'accès non déclarée   */
    const GInterfaceInfo *iinfo;            /* Informations associées      */

    /**
     * Lors de l'appel à pygobject_register_class(), PyGObject remplace systématiquement
     * le type Python fourni par :
     *
     *    Py_TYPE(type) = PyGObject_MetaType;
     *
     * Ce nouveau type est le suivant (cf. gi/types.py) :
     *
     *    class _GObjectMetaBase(type):
     *        """Metaclass for automatically registering GObject classes."""
     *
     * D'une part, comme les enregistrements sont gérés manuellement dans le cas de
     * types dérivés dynamiquement d'objets natifs, ce changement est inutile.
     *
     * D'autre part, il semble avoir un soucis de références (cf. testGarbageCollecting()
     * du fichier de test plugins/plugin.py) :
     *
     *    python3dm: ../Modules/gcmodule.c:379: visit_decref: Assertion `_PyGCHead_REFS(gc) != 0' failed.
     *
     *    #3  __GI___assert_fail ()
     *    #4  visit_decref ()
     *    #5  subtype_traverse ()
     *    #6  subtract_refs ()
     *    #7  collect ()
     *    #8  collect_with_callback ()
     *    #9  gc_collect ()
     *
     * On restaure donc le type d'origine de l'objet Python créé dynamquement pour éviter
     * ce genre de soucis.
     */

    legacy_parent = Py_TYPE(type);

    sys_mod_dict = PyImport_GetModuleDict();

    modname = PyDict_GetItemString(type->tp_dict, "__module__");

    module = PyObject_GetItem(sys_mod_dict, modname);

    dict = PyModule_GetDict(module);

    result = register_class_for_pygobject(dict, gtype, type);

    Py_SET_TYPE(type, legacy_parent);

    /**
     * Comme la mise en place dynamique de nouveau GType court-circuite les
     * mécanismes internes de pygobject, les interfaces implémentées ne sont
     * nominalement plus complétées.
     *
     * On reprend donc la logique copiée depuis le contenu de la fonction
     * pyg_type_add_interfaces() du fichier "pygobject-3.22.0/gi/gobjectmodule.c".
     */

    for (i = 0; i < PyTuple_GET_SIZE(type->tp_mro); i++)
    {
        mro_base = PyTuple_GET_ITEM(type->tp_mro, i);

        if (!PyType_Check(mro_base))
            continue;

        itype = pyg_type_from_object(mro_base);

        if (itype == G_TYPE_INTERFACE)
            continue;

        if (!G_TYPE_IS_INTERFACE(itype))
            continue;

        if (!g_type_is_a(gtype, itype))
        {
            /**
             * Reproduction de pyg_lookup_interface_info().
             */

            pyginterface_info_key = g_quark_from_static_string("PyGInterface::info");

            iinfo = g_type_get_qdata(itype, pyginterface_info_key);
            assert(iinfo != NULL);

            g_type_add_interface_static(gtype, itype, iinfo);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python/GObject à initialiser.                   *
*                                                                             *
*  Description : Fait suivre à la partie GObject une initialisation nouvelle. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int forward_pygobjet_init(PyObject *self)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *new_args;                     /* Nouveaux arguments épurés   */
    PyObject *new_kwds;                     /* Nouveau dictionnaire épuré  */

    new_args = PyTuple_New(0);
    new_kwds = PyDict_New();

    result = PyGObject_Type.tp_init(self, new_args, new_kwds);

    Py_DECREF(new_kwds);
    Py_DECREF(new_args);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en valeur GType.                          *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_gtype(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */
    GType type;                             /* Type obtenu ou 0            */

    type = pyg_type_from_object(arg);

    switch (type)
    {
        case G_TYPE_INVALID:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        default:
            *((GType *)dst) = type;
            result = 1;
            break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en instance GObject.                      *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_gobject(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)&PyGObject_Type);

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to GObject instance");
            break;

        case 1:
            *((GObject **)dst) = G_OBJECT(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en instance de composant GTK.             *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_gtk_widget(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */
    PyObject *gtk_mod;                      /* Module Python Gtk           */
    PyObject *widget_type;                  /* Module "GtkWidget"          */
    int ret;                                /* Bilan d'une conversion      */

    result = 0;

    gtk_mod = PyImport_ImportModule("gi.repository.Gtk");

    if (gtk_mod == NULL)
    {
        PyErr_SetString(PyExc_TypeError, "unable to find the Gtk Python module");
        goto done;
    }

    widget_type = PyObject_GetAttrString(gtk_mod, "Widget");

    Py_DECREF(gtk_mod);

    ret = PyObject_TypeCheck(arg, (PyTypeObject *)widget_type);

    Py_DECREF(widget_type);

    if (!ret)
    {
        PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to GTK widget");
        goto done;
    }

    *((GtkWidget **)dst) = GTK_WIDGET(pygobject_get(arg));

    result = 1;

 done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en instance de conteneur GTK.             *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_gtk_container(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */
    PyObject *gtk_mod;                      /* Module Python Gtk           */
    PyObject *container_type;               /* Module "GtkContainer"          */
    int ret;                                /* Bilan d'une conversion      */

    result = 0;

    gtk_mod = PyImport_ImportModule("gi.repository.Gtk");

    if (gtk_mod == NULL)
    {
        PyErr_SetString(PyExc_TypeError, "unable to find the Gtk Python module");
        goto done;
    }

    container_type = PyObject_GetAttrString(gtk_mod, "Container");

    Py_DECREF(gtk_mod);

    ret = PyObject_TypeCheck(arg, (PyTypeObject *)container_type);

    Py_DECREF(container_type);

    if (!ret)
    {
        PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to GTK container");
        goto done;
    }

    *((GtkContainer **)dst) = GTK_CONTAINER(pygobject_get(arg));

    result = 1;

 done:

    return result;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : color = couleur dans sa définition native à copier.          *
*                                                                             *
*  Description : Construit un objet Python pour une couleur RGBA.             *
*                                                                             *
*  Retour      : Objet Python prêt à emploi ou NULL en cas d'échec.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *create_gdk_rgba(const GdkRGBA *color)
{
    PyObject *result;                       /* Coloration à retourner      */
    PyObject *gdk_mod;                      /* Module Python Gdk           */
    PyObject *rgba_type;                    /* Classe "GtkRGBA"            */
    PyObject *rgba_args;                    /* Arguments pour l'appel      */

    result = NULL;

    gdk_mod = PyImport_ImportModule("gi.repository.Gdk");

    if (gdk_mod == NULL)
    {
        PyErr_SetString(PyExc_TypeError, "unable to find the Gtk Python module");
        goto done;
    }

    rgba_type = PyObject_GetAttrString(gdk_mod, "RGBA");

    Py_DECREF(gdk_mod);

    rgba_args = PyTuple_New(4);
    PyTuple_SetItem(rgba_args, 0, PyFloat_FromDouble(color->red));
    PyTuple_SetItem(rgba_args, 1, PyFloat_FromDouble(color->green));
    PyTuple_SetItem(rgba_args, 2, PyFloat_FromDouble(color->blue));
    PyTuple_SetItem(rgba_args, 3, PyFloat_FromDouble(color->alpha));

    result = PyObject_CallObject(rgba_type, rgba_args);

    Py_DECREF(rgba_args);

 done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en instance de couleur RGBA.              *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_gdk_rgba(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */
    PyObject *gdk_mod;                      /* Module Python Gdk           */
    PyObject *rgba_type;                    /* Module "RGBA"               */
    int ret;                                /* Bilan d'une conversion      */
    PyObject *value;                        /* Valeur d'une composante     */

    result = 0;

    gdk_mod = PyImport_ImportModule("gi.repository.Gdk");

    if (gdk_mod == NULL)
    {
        PyErr_SetString(PyExc_TypeError, "unable to find the Gdk Python module");
        goto done;
    }

    rgba_type = PyObject_GetAttrString(gdk_mod, "RGBA");

    Py_DECREF(gdk_mod);

    ret = PyObject_TypeCheck(arg, (PyTypeObject *)rgba_type);

    Py_DECREF(rgba_type);

    if (!ret)
    {
        PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to GDK RGBA color");
        goto done;
    }

    value = PyObject_GetAttrString(arg, "red");
    assert(PyFloat_Check(value));

    ((GdkRGBA *)dst)->red = PyFloat_AsDouble(value);

    value = PyObject_GetAttrString(arg, "blue");
    assert(PyFloat_Check(value));

    ((GdkRGBA *)dst)->blue = PyFloat_AsDouble(value);

    value = PyObject_GetAttrString(arg, "green");
    assert(PyFloat_Check(value));

    ((GdkRGBA *)dst)->green = PyFloat_AsDouble(value);

    value = PyObject_GetAttrString(arg, "alpha");
    assert(PyFloat_Check(value));

    ((GdkRGBA *)dst)->alpha = PyFloat_AsDouble(value);

    result = 1;

 done:

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                         TRANSFERT DES VALEURS CONSTANTES                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : owner  = désignation du propriétaire du dictionnaire visé.   *
*                dict   = dictionnaire dont le contenu est à compléter.       *
*                flags  = indique le type d'énumération ciblée.               *
*                name   = désignation humaine du groupe à constituer.         *
*                values = noms et valeurs associées.                          *
*                doc    = documentation à associer au groupe.                 *
*                                                                             *
*  Description : Officialise un groupe de constantes avec sémentique.         *
*                                                                             *
*  Retour      : Groupe de constantes mis en place ou NULL en cas d'échec.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *_attach_constants_group(const char *owner, PyObject *dict, bool flags, const char *name, PyObject *values, const char *doc)
{
    PyObject *result;                       /* Instance à retourner        */
    PyObject *enum_mod;                     /* Module Python enum          */
    PyObject *class;                        /* Classe "Enum*"              */
    PyObject *str_obj;                      /* Conversion en Python        */
    int ret;                                /* Bilan d'une insertion       */
    PyObject *args;                         /* Arguments de la construction*/
    PyObject *kwargs;                       /* Mots clefs en complément    */
    char *dot;                              /* Point de séparation         */
    char *module;                           /* Module d'appartenance       */
    char *qualname;                         /* Désignation pour Pickle     */
    PyObject *new;                          /* Nouvelle instance en place  */
    PyObject *features;                     /* Module à recompléter        */
    PyObject *features_dict;                /* Dictionnaire à compléter    */

    result = NULL;

    /* Recherche de la classe Python */

    enum_mod = PyImport_ImportModule("enum");

    if (enum_mod == NULL)
        goto no_mod;

    if (flags)
        class = PyObject_GetAttrString(enum_mod, "IntFlag");
    else
        class = PyObject_GetAttrString(enum_mod, "IntEnum");

    Py_DECREF(enum_mod);

    if (class == NULL)
        goto no_class;

    /* Compléments des paramètres */

    str_obj = PyUnicode_FromString(doc);
    ret = PyDict_SetItemString(values, "__doc__", str_obj);
    Py_DECREF(str_obj);

    if (ret != 0)
        goto doc_error;

    args = PyTuple_New(2);

    ret = PyTuple_SetItem(args, 0, PyUnicode_FromString(name));
    if (ret != 0) goto args_error;

    Py_INCREF(values);
    ret = PyTuple_SetItem(args, 1, values);
    if (ret != 0) goto args_error;

    kwargs = PyDict_New();

    dot = rindex(owner, '.');
    assert(dot != NULL);

    module = strndup(owner, dot - owner);

    str_obj = PyUnicode_FromString(module);
    ret = PyDict_SetItemString(kwargs, "module", str_obj);
    Py_DECREF(str_obj);

    free(module);

    asprintf(&qualname, "%s.%s", dot + 1, name);

    if (ret != 0) goto kwargs_error;

    str_obj = PyUnicode_FromString(qualname);
    ret = PyDict_SetItemString(kwargs, "qualname", str_obj);
    Py_DECREF(str_obj);

    free(qualname);

    if (ret != 0) goto kwargs_error;

    /* Constitution de l'énumération et enregistrement */

    new = PyObject_Call(class, args, kwargs);
    if (new == NULL) goto build_error;

    ret = PyDict_SetItemString(dict, name, new);
    if (ret != 0) goto register_0_error;

    features = get_access_to_python_module("pychrysalide.features");

    features_dict = PyModule_GetDict(features);

    ret = PyDict_SetItemString(features_dict, name, new);
    if (ret != 0) goto register_1_error;

    result = new;
    Py_INCREF(result);

    /* Sortie propre */

 register_1_error:
 register_0_error:

    Py_DECREF(new);

 build_error:
 kwargs_error:

    Py_DECREF(kwargs);

 args_error:

    Py_DECREF(args);

 doc_error:

    Py_DECREF(class);

 no_class:
 no_mod:

    Py_DECREF(values);

    return result;

}

/******************************************************************************
*                                                                             *
*  Paramètres  : owner  = désignation du propriétaire du dictionnaire visé.   *
*                dict   = dictionnaire dont le contenu est à compléter.       *
*                flags  = indique le type d'énumération ciblée.               *
*                name   = désignation humaine du groupe à constituer.         *
*                values = noms et valeurs associées.                          *
*                doc    = documentation à associer au groupe.                 *
*                gtype  = énumération GLib à lier.                            *
*                                                                             *
*  Description : Officialise un groupe de constantes avec lien GLib.          *
*                                                                             *
*  Retour      : Groupe de constantes mis en place ou NULL en cas d'échec.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *_attach_constants_group_with_pyg_enum(const char *owner, PyObject *dict, bool flags, const char *name, PyObject *values, const char *doc, GType gtype)
{
    PyObject *result;                       /* Instance à retourner        */
    PyObject *values_set;                   /* Zone pour nouvelles valeurs */
    int ret;                                /* Bilan d'une insertion       */
    PyObject *new;                          /* Nouvelle instance en place  */
    PyObject *values_src;                   /* Source de nouvelles valeurs */
    PyObject *values_dest;                  /* Destination des valeurs     */

    static GQuark pygenum_class_key = 0;    /* Clef d'accès au marquage    */

    result = NULL;

    /**
     * Le seul intérêt d'un tel enregistrement en bonne et due forme est de
     * permettre une impression, via str() ou repr(), de l'énumération
     * transcrite en GLib via g_enum_register_static() et potentiellement
     * convertie de façon brusque par _pygi_argument_to_object(), lors d'une
     * émission de signal par exemple.
     *
     * La satisfaction de la fonction pyg_enum_from_gtype() est ainsi recherchée.
     * Tous les éléments sont normalement mis en place à partir de la fonction
     * pyg_enum_add().
     */

    /* Préparation du réceptacle */

    values_set = PyDict_New();

    ret = PyDict_SetItemString(values, "__enum_values__", values_set);

    Py_DECREF(values_set);

    if (ret != 0) goto exit;

    /* Création */

    new = _attach_constants_group(owner, dict, flags, name, values, doc);
    if (new == NULL) goto exit;

    /* Actualisation des valeurs */

    values_src = PyDict_GetItemString(((PyTypeObject *)new)->tp_dict, "_value2member_map_");
    if (values_src == NULL) goto exit_without_src;

    values_dest = PyDict_GetItemString(((PyTypeObject *)new)->tp_dict, "__enum_values__");
    if (values_dest == NULL) goto exit_without_dest;

    assert(values_dest == values_set);

    ret = PyDict_Merge(values_dest, values_src, true);

    if (ret == 0)
    {
        result = new;
        Py_INCREF(result);

        if (pygenum_class_key == 0)
            pygenum_class_key = g_quark_from_static_string("PyGEnum::class");

        g_type_set_qdata(gtype, pygenum_class_key, result);

    }

 exit_without_dest:
 exit_without_src:

    Py_DECREF(new);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : owner = désignation du propriétaire du dictionnaire visé.    *
*                name  = désignation humaine du groupe à consulter.           *
*                value = valeur à transmettre à Python.                       *
*                                                                             *
*  Description : Traduit une valeur constante C en équivalent Python.         *
*                                                                             *
*  Retour      : Objet Python résultant ou NULL en cas d'erreur.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *_cast_with_constants_group(const char *owner, const char *name, unsigned long value)
{
    PyObject *result;                       /* Objet Python à retourner    */
    char *dot;                              /* Position du dernier point   */
    char *modname;                          /* Chemin d'accès au module    */
    PyObject *module;                       /* Module à consulter          */
    PyObject *type;                         /* Classe propriétaire         */
    PyObject *class;                        /* Classe "Enum*"              */
    PyObject *args;                         /* Arguments de la construction*/

    result = NULL;

    /* Recherche de la classe Python */

    dot = strrchr(owner, '.');
    assert(dot != NULL);

    modname = strndup(owner, dot - owner);

    module = get_access_to_python_module(modname);

    if (module == NULL)
        goto no_mod;

    type = PyObject_GetAttrString(module, dot + 1);

    if (type == NULL)
        goto no_type;

    class = PyObject_GetAttrString(type, name);

    if (class == NULL)
        goto no_class;

    /* Construction */

    args = Py_BuildValue("(k)", value);

    result = PyObject_CallObject(class, args);

    Py_DECREF(args);

    Py_DECREF(class);

 no_class:

    Py_DECREF(type);

 no_type:
 no_mod:

    free(modname);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dict = dictionnaire dont le contenu est à compléter.         *
*                name = désignation humaine du groupe à constituer.           *
*                doc  = documentation à associer au groupe.                   *
*                out  = dictionnaire à compléter. [OUT]                       *
*                                                                             *
*  Description : Officialise un groupe de constantes de chaînes de caractères.*
*                                                                             *
*  Retour      : true en cas de succès de l'opération, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _create_string_constants_group(PyObject *dict, const char *name, const char *doc, PyObject **out)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *class;                        /* Classe "Enum*"              */
    PyObject *args;                         /* Argument de construction    */
    int ret;                                /* Bilan d'une insertion       */
    PyObject *features;                     /* Module à recompléter        */
    PyObject *features_dict;                /* Dictionnaire à compléter    */

    result = false;

    /* Recherche et instanciation de la classe Python */

    class = (PyObject *)get_python_string_enum_type();

    args = Py_BuildValue("(s)", doc);

    *out = PyObject_CallObject(class, args);

    Py_DECREF(args);

    if (*out == NULL)
        goto exit;

    /* Constitution de l'énumération et enregistrement */

    ret = PyDict_SetItemString(dict, name, *out);
    if (ret != 0) goto register_0_error;

    features = get_access_to_python_module("pychrysalide.features");

    features_dict = PyModule_GetDict(features);

    ret = PyDict_SetItemString(features_dict, name, *out);
    if (ret != 0) goto register_1_error;

    result = true;

    /* Sortie propre */

 register_1_error:
 register_0_error:

    if (!result)
        Py_DECREF(*out);

 exit:

    return result;

}
