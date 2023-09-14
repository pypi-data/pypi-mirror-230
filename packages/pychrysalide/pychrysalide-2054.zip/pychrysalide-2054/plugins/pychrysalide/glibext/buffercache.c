
/* Chrysalide - Outil d'analyse de fichiers binaires
 * buffercache.c - équivalent Python du fichier "glibext/buffercache.c"
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include "buffercache.h"


#include <pygobject.h>


#include <glibext/buffercache-int.h>
#include <plugins/dt.h>


#include "constants.h"
#include "bufferline.h"
#include "linegen.h"
#include "../access.h"
#include "../helpers.h"
#include "../analysis/content.h"



/* ------------------------ GLUE POUR CREATION DEPUIS PYTHON ------------------------ */


/* Accompagne la création d'une instance dérivée en Python. */
static PyObject *py_buffer_cache_new(PyTypeObject *, PyObject *, PyObject *);

/* Initialise une instance sur la base du dérivé de GObject. */
static int py_buffer_cache_init(PyObject *, PyObject *, PyObject *);



/* -------------------------- TAMPON POUR CODE DESASSEMBLE -------------------------- */


/* Met à disposition un encadrement des accès aux lignes. */
static PyObject *py_buffer_cache_lock(PyObject *, PyObject *);

/* Met à disposition un encadrement des accès aux lignes. */
static PyObject *py_buffer_cache_unlock(PyObject *, PyObject *);

/* Insère un générateur dans des lignes à une position donnée. */
static PyObject *py_buffer_cache_insert_at(PyObject *, PyObject *);

/* Retire une ligne du tampon. */
static PyObject *py_buffer_cache_delete_at(PyObject *, PyObject *);

/* Retire un type de générateur de lignes. */
static PyObject *py_buffer_cache_delete_type_at(PyObject *, PyObject *);

/* Ajoute en fin de tampon un générateur de lignes. */
static PyObject *py_buffer_cache_append(PyObject *, PyObject *);

/* Etend un tampon avec un générateur de lignes unique. */
static PyObject *py_buffer_cache_extend_with(PyObject *, PyObject *);

/* Réduit le tampon à une quantité de lignes précise. */
static PyObject *py_buffer_cache_truncate(PyObject *, PyObject *);

/* Ajoute une propriété particulière à une ligne. */
static PyObject *py_buffer_cache_add_line_flag(PyObject *, PyObject *);

/* Détermine l'ensemble des propriétés attachées à une ligne. */
static PyObject *py_buffer_cache_get_line_flags(PyObject *, PyObject *);

/* Retire une propriété particulière attachée à une ligne. */
static PyObject *py_buffer_cache_remove_line_flag(PyObject *, PyObject *);

#ifdef INCLUDE_GTK_SUPPORT

/* Retrouve une ligne au sein d'un tampon avec un indice. */
static PyObject *py_buffer_cache_find_line_by_index(PyObject *, PyObject *);

#endif

/* Avance autant que possible vers une ligne idéale. */
static PyObject *py_buffer_cache_look_for_flag(PyObject *, PyObject *);

/* Indique l'éventuel contenu binaire associé au cache. */
static PyObject *py_buffer_cache_get_content(PyObject *, void *);

/* Fournit la hauteur d'impression d'une ligne visualisée. */
static PyObject *py_buffer_cache_get_line_height(PyObject *, void *);

/* Fournit la taille réservée pour la marge gauche. */
static PyObject *py_buffer_cache_get_left_margin(PyObject *, void *);

/* Fournit la position de départ pour l'impression de texte. */
static PyObject *py_buffer_cache_get_text_position(PyObject *, void *);

/* Compte le nombre de lignes rassemblées dans un tampon. */
static PyObject *py_buffer_cache_get_lines_count(PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                          GLUE POUR CREATION DEPUIS PYTHON                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type du nouvel objet à mettre en place.               *
*                args = éventuelle liste d'arguments.                         *
*                kwds = éventuel dictionnaire de valeurs mises à disposition. *
*                                                                             *
*  Description : Accompagne la création d'une instance dérivée en Python.     *
*                                                                             *
*  Retour      : Nouvel objet Python mis en place ou NULL en cas d'échec.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *result;                       /* Objet à retourner           */
    PyTypeObject *base;                     /* Type de base à dériver      */
    bool first_time;                        /* Evite les multiples passages*/
    GType gtype;                            /* Nouveau type de processeur  */
    bool status;                            /* Bilan d'un enregistrement   */

    /* Validations diverses */

    base = get_python_buffer_cache_type();

    if (type == base)
        goto simple_way;

    /* Mise en place d'un type dédié */

    first_time = (g_type_from_name(type->tp_name) == 0);

    gtype = build_dynamic_type(G_TYPE_BUFFER_CACHE, type->tp_name, NULL, NULL, NULL);

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

static int py_buffer_cache_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    GBinContent *content;                   /* Instance GLib du contenu    */
    int ret;                                /* Bilan de lecture des args.  */
    GBufferCache *cache;                    /* Version GLib du tampon      */

#define BUFFER_CACHE_DOC                                                    \
    "The BufferCache object manages a group of lines intended to get"       \
    " printed onto the screen or into a file.\n"                            \
    "\n"                                                                    \
    "These lines are cached and rebuilt when needed.\n"                     \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    BufferCache(content=None)"                                         \
    "\n"                                                                    \
    "Where content is a pychrysalide.analysis.BinContent instance, if"      \
    " defined. This content is provided to lines as argument when the"      \
    " lines get printed, so it may not be always useful and thus can be"    \
    " discarded when creating a new buffer cache."                          \

    /* Récupération des paramètres */

    content = NULL;

    ret = PyArg_ParseTuple(args, "|O&", convert_to_binary_content_or_none, &content);
    if (!ret) return -1;

    /* Initialisation d'un objet GLib */

    ret = forward_pygobjet_init(self);
    if (ret == -1) return -1;

    /* Eléments de base */

    cache = G_BUFFER_CACHE(pygobject_get(self));

    if (content != NULL)
    {
        cache->content = content;
        g_object_ref(G_OBJECT(content));
    }

    return 0;

}



/* ---------------------------------------------------------------------------------- */
/*                            TAMPON POUR CODE DESASSEMBLE                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un tampon de code.                *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Met à disposition un encadrement des accès aux lignes.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_lock(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    int write;                              /* Type de verrou à poser      */
    int ret;                                /* Bilan de lecture des args.  */
    GBufferCache *cache;                    /* Tampon natif à consulter    */

#define BUFFER_CACHE_LOCK_METHOD PYTHON_METHOD_DEF                  \
(                                                                   \
    lock, "$self, /, write=False",                                  \
    METH_VARARGS, py_buffer_cache,                                  \
    "Lock for access the content of a buffer cache instance.\n"     \
    "\n"                                                            \
    "The *write* parameter is a boolean value which has to be set"  \
    " if the access to perform will modify the buffer cache.\n"     \
    "\n"                                                            \
    "Each call of this method has to followed by a call to"         \
    " pychrysalide.glibext.BufferCache.unlock(), with the same"     \
    " *write* parameter."                                           \
)

    write = 0;

    ret = PyArg_ParseTuple(args, "|p", &write);
    if (!ret) return NULL;

    cache = G_BUFFER_CACHE(pygobject_get(self));

    g_buffer_cache_lock_unlock(cache, write, true);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un tampon de code.                *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Met à disposition un encadrement des accès aux lignes.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_unlock(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    int write;                              /* Type de verrou à poser      */
    int ret;                                /* Bilan de lecture des args.  */
    GBufferCache *cache;                    /* Tampon natif à consulter    */

#define BUFFER_CACHE_UNLOCK_METHOD PYTHON_METHOD_DEF                \
(                                                                   \
    unlock, "$self, /, write=False",                                \
    METH_VARARGS, py_buffer_cache,                                  \
    "Unlock the content of a buffer cache instance.\n"              \
    "\n"                                                            \
    "The *write* parameter is a boolean value which has to be set"  \
    " if the performed access has modified the buffer cache.\n"     \
)

    write = 0;

    ret = PyArg_ParseTuple(args, "|p", &write);
    if (!ret) return NULL;

    cache = G_BUFFER_CACHE(pygobject_get(self));

    g_buffer_cache_lock_unlock(cache, write, false);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un tampon de code.                *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Insère un générateur dans des lignes à une position donnée.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_insert_at(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    size_t index;                           /* Indice de ligne à supprimer */
    GLineGenerator *generator;              /* Générateur à associer       */
    BufferLineFlags flags;                  /* Particularités nominales    */
    int before;                             /* Insertion avant ?           */
    int after;                              /* Insertion après ?           */
    int ret;                                /* Bilan de lecture des args.  */
    GBufferCache *cache;                    /* Tampon natif à consulter    */

#define BUFFER_CACHE_INSERT_AT_METHOD PYTHON_METHOD_DEF             \
(                                                                   \
    insert_at, "$self, index, generator, /, flags="                 \
    "pychrysalide.glibext.BufferLine.BufferLineFlags.NONE,"         \
    " before=False, after=False",                                   \
    METH_VARARGS, py_buffer_cache,                                  \
    "Add an extra content generator to a given line.\n"             \
    "\n"                                                            \
    "The new content generator for the line at, before or after"    \
    " the provided index is a pychrysalide.glibext.LineGenerator"   \
    " instance. Nominal properties can be set for this line as"     \
    " extra pychrysalide.glibext.BufferLine.BufferLineFlags"        \
    " values.\n"                                                    \
    "\n"                                                            \
    "An write access lock has to be held for the cache; see the"    \
    " pychrysalide.glibext.BufferCache.lock() function."            \
)

    flags = BLF_NONE;
    before = 0;
    after = 0;

    ret = PyArg_ParseTuple(args, "nO&|O&pp", &index, convert_to_line_generator, &generator,
                           convert_to_buffer_line_flags, &flags, &before, &after);
    if (!ret) return NULL;

    cache = G_BUFFER_CACHE(pygobject_get(self));

    g_buffer_cache_insert_at(cache, index, generator, flags, before, after);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un tampon de code.                *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Retire une ligne du tampon.                                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_delete_at(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    size_t index;                           /* Indice de ligne à supprimer */
    int ret;                                /* Bilan de lecture des args.  */
    GBufferCache *cache;                    /* Tampon natif à consulter    */

#define BUFFER_CACHE_DELETE_AT_METHOD PYTHON_METHOD_DEF                 \
(                                                                       \
    delete_at, "$self, index, /",                                       \
    METH_VARARGS, py_buffer_cache,                                      \
    "Delete the line at the *index* position from a buffer cache.\n"    \
    "\n"                                                                \
    "An write access lock has to be held for the cache; see the"        \
    " pychrysalide.glibext.BufferCache.lock() function."                \
)

    ret = PyArg_ParseTuple(args, "n", &index);
    if (!ret) return NULL;

    cache = G_BUFFER_CACHE(pygobject_get(self));

    g_buffer_cache_delete_at(cache, index);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un tampon de code.                *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Retire un type de générateur de lignes.                      *
*                                                                             *
*  Retour      : Générateur éventuellement trouvé ou NULL si aucun.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_delete_type_at(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    size_t index;                           /* Indice de ligne à supprimer */
    PyObject *py_gtype;                     /* Version Python d'un GType   */
    int before;                             /* Insertion avant ?           */
    int after;                              /* Insertion après ?           */
    int ret;                                /* Bilan de lecture des args.  */
    GType gtype;                            /* Type de générateur visé     */
    GBufferCache *cache;                    /* Tampon natif à consulter    */
    GLineGenerator *generator;              /* Générateur retiré ou NULL   */

#define BUFFER_CACHE_DELETE_TYPE_AT_METHOD PYTHON_METHOD_DEF                \
(                                                                           \
    delete_type_at, "$self, index, gtype, /, before=False, after=False",    \
    METH_VARARGS, py_buffer_cache,                                          \
    "Delete the first generator of a given type found inside a line of a"   \
    " buffer cache.\n"                                                      \
    "\n"                                                                    \
    "The target type has to be a gobject.GType, usually provided by the"    \
    " *__gtype__* attribute of a generator interface. The generator is"     \
    " deleted from the line at, before or after the provided index.\n"      \
    "\n"                                                                    \
    "The function returns the deleted generator as a"                       \
    " pychrysalide.glibext.LineGenerator instance, or None if none found.\n"\
    "\n"                                                                    \
    "An write access lock has to be held for the cache; see the"            \
    " pychrysalide.glibext.BufferCache.lock() function."                    \
)

    before = 0;
    after = 0;

    ret = PyArg_ParseTuple(args, "nO|pp", &index, &py_gtype, &before, &after);
    if (!ret) return NULL;

    gtype = pyg_type_from_object(py_gtype);
    if (gtype == 0) return NULL;

    cache = G_BUFFER_CACHE(pygobject_get(self));

    generator = g_buffer_cache_delete_type_at(cache, index, gtype, before, after);

    if (generator != NULL)
    {
        result = pygobject_new(G_OBJECT(generator));
        g_object_unref(G_OBJECT(generator));
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
*  Paramètres  : self = classe représentant un tampon de code.                *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Ajoute en fin de tampon un générateur de lignes.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_append(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    GLineGenerator *generator;              /* Générateur à associer       */
    BufferLineFlags flags;                  /* Particularités nominales    */
    int ret;                                /* Bilan de lecture des args.  */
    GBufferCache *cache;                    /* Tampon natif à consulter    */

#define BUFFER_CACHE_APPEND_METHOD PYTHON_METHOD_DEF                \
(                                                                   \
    append, "$self, generator, /, flags="                           \
    "pychrysalide.glibext.BufferLine.BufferLineFlags.NONE",         \
    METH_VARARGS, py_buffer_cache,                                  \
    "Append a new line at the end of a buffer cache.\n"             \
    "\n"                                                            \
    "The content generator for this new line is a"                  \
    " pychrysalide.glibext.LineGenerator instance. Nominal"         \
    " properties can be set for the line as extra"                  \
    " pychrysalide.glibext.BufferLine.BufferLineFlags values.\n"    \
    "\n"                                                            \
    "An write access lock has to be held for the cache; see the"    \
    " pychrysalide.glibext.BufferCache.lock() function."            \
)

    flags = BLF_NONE;

    ret = PyArg_ParseTuple(args, "O&|O&", convert_to_line_generator, &generator,
                           convert_to_buffer_line_flags, &flags);
    if (!ret) return NULL;

    cache = G_BUFFER_CACHE(pygobject_get(self));

    g_buffer_cache_append(cache, generator, flags);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un tampon de code.                *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Etend un tampon avec un générateur de lignes unique.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_extend_with(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    size_t count;                           /* Quantité de lignes à créer  */
    GLineGenerator *generator;              /* Générateur à associer       */
    int ret;                                /* Bilan de lecture des args.  */
    GBufferCache *cache;                    /* Tampon natif à consulter    */

#define BUFFER_CACHE_EXTEND_WITH_METHOD PYTHON_METHOD_DEF           \
(                                                                   \
    extend_with, "$self, count, generator, /",                      \
    METH_VARARGS, py_buffer_cache,                                  \
    "Extend the buffer cache so it will contain *count* lines.\n"   \
    "\n"                                                            \
    "The *count* number should be greater than the current line"    \
    " quantity, otherwise the call makes no sense. The generator"   \
    " is a pychrysalide.glibext.LineGenerator instance used to"     \
    " produce the extra new lines on demand."                       \
    "\n"                                                            \
    "An write access lock has to be held for the cache; see the"    \
    " pychrysalide.glibext.BufferCache.lock() function."            \
)

    ret = PyArg_ParseTuple(args, "nO&", &count, convert_to_line_generator, &generator);
    if (!ret) return NULL;

    cache = G_BUFFER_CACHE(pygobject_get(self));

    g_buffer_cache_extend_with(cache, count, generator);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un tampon de code.                *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Réduit le tampon à une quantité de lignes précise.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_truncate(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    size_t max;                             /* Nombre de lignes au maximum */
    int ret;                                /* Bilan de lecture des args.  */
    GBufferCache *cache;                    /* Tampon natif à consulter    */

#define BUFFER_CACHE_TRUNCATE_METHOD PYTHON_METHOD_DEF                  \
(                                                                       \
    truncate, "$self, max, /",                                          \
    METH_VARARGS, py_buffer_cache,                                      \
    "Shrink the buffer cache so it will contain at most *max* lines.\n" \
    "\n"                                                                \
    "The *max* number should be lesser than the current line quantity," \
    " otherwise no effect will happen."                                 \
    "\n"                                                                \
    "An write access lock has to be held for the cache; see the"        \
    " pychrysalide.glibext.BufferCache.lock() function."                \
)

    ret = PyArg_ParseTuple(args, "n", &max);
    if (!ret) return NULL;

    cache = G_BUFFER_CACHE(pygobject_get(self));

    g_buffer_cache_truncate(cache, max);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = tampon de lignes à venir consulter.                   *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Ajoute une propriété particulière à une ligne.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_add_line_flag(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    size_t index;                           /* Indice de la ligne visée    */
    BufferLineFlags flag;                   /* Drapeau à considérer        */
    int ret;                                /* Bilan de lecture des args.  */
    GBufferCache *cache;                    /* Tampon natif à consulter    */

#define BUFFER_CACHE_ADD_LINE_FLAG_METHOD PYTHON_METHOD_DEF         \
(                                                                   \
    add_line_flag, "$self, index, flag, /",                         \
    METH_VARARGS, py_buffer_cache,                                  \
    "Add one optional flag to those assigned to a given buffer"     \
    " line. The line is located using the *index* argument.\n"      \
    "\n"                                                            \
    "The *index* has to be a simple integer, and the *flag* a"      \
    " pychrysalide.glibext.BufferLine.BufferLineFlags value.\n"     \
    "\n"                                                            \
    "An write access lock has to be held for the cache; see the"    \
    " pychrysalide.glibext.BufferCache.lock() function."            \
)

    ret = PyArg_ParseTuple(args, "nO&", &index, convert_to_buffer_line_flags, &flag);
    if (!ret) return NULL;

    cache = G_BUFFER_CACHE(pygobject_get(self));

    g_buffer_cache_add_line_flag(cache, index, flag);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un tampon de code.                *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Détermine l'ensemble des propriétés attachées à une ligne.   *
*                                                                             *
*  Retour      : Somme de toutes les propriétés enregistrées.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_get_line_flags(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    size_t index;                           /* Indice de la ligne visée    */
    int ret;                                /* Bilan de lecture des args.  */
    GBufferCache *cache;                    /* Tampon natif à consulter    */
    BufferLineFlags flags;                  /* Fanions conservés           */

#define BUFFER_CACHE_GET_LINE_FLAGS_METHOD PYTHON_METHOD_DEF            \
(                                                                       \
    get_line_flags, "$self, index, /",                                  \
    METH_VARARGS, py_buffer_cache,                                      \
    "Provide the optional flags assigned to a given buffer line. The"   \
    " line is located using the *index* argument.\n"                    \
    "\n"                                                                \
    "The result is a pychrysalide.glibext.BufferLine.BufferLineFlags"   \
    " value.\n"                                                         \
    "\n"                                                                \
    "An read access lock has to be held for the cache; see the"         \
    " pychrysalide.glibext.BufferCache.lock() function."                \
)

    ret = PyArg_ParseTuple(args, "n", &index);
    if (!ret) return NULL;

    cache = G_BUFFER_CACHE(pygobject_get(self));

    flags = g_buffer_cache_get_line_flags(cache, index);

    result = cast_with_constants_group_from_type(get_python_buffer_line_type(), "BufferLineFlags", flags);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = tampon de lignes à venir consulter.                   *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Retire une propriété particulière attachée à une ligne.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_remove_line_flag(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    size_t index;                           /* Indice de la ligne visée    */
    BufferLineFlags flag;                   /* Drapeau à considérer        */
    int ret;                                /* Bilan de lecture des args.  */
    GBufferCache *cache;                    /* Tampon natif à consulter    */

#define BUFFER_CACHE_REMOVE_LINE_FLAG_METHOD PYTHON_METHOD_DEF          \
(                                                                       \
    remove_line_flag, "$self, index, flag, /",                          \
    METH_VARARGS, py_buffer_cache,                                      \
    "Remove one optional flag from those assigned to a given buffer"    \
    " line. The line is located using the *index* argument.\n"          \
    "\n"                                                                \
    "The *index* has to be a simple integer, and the *flag* a"          \
    " pychrysalide.glibext.BufferLine.BufferLineFlags value.\n"         \
    "\n"                                                                \
    "An write access lock has to be held for the cache; see the"        \
    " pychrysalide.glibext.BufferCache.lock() function."                \
)

    ret = PyArg_ParseTuple(args, "nO&", &index, convert_to_buffer_line_flags, &flag);
    if (!ret) return NULL;

    cache = G_BUFFER_CACHE(pygobject_get(self));

    g_buffer_cache_remove_line_flag(cache, index, flag);

    result = Py_None;
    Py_INCREF(result);

    return result;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un tampon de code.                *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Retrouve une ligne au sein d'un tampon avec un indice.       *
*                                                                             *
*  Retour      : Line retrouvée ou None en cas d'échec.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_find_line_by_index(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    size_t index;                           /* Indice de la ligne visée    */
    int ret;                                /* Bilan de lecture des args.  */
    GBufferCache *cache;                    /* Tampon natif à consulter    */
    GBufferLine *line;                      /* Ligne trouvée ?             */

#define BUFFER_CACHE_FIND_LINE_BY_INDEX_METHOD PYTHON_METHOD_DEF        \
(                                                                       \
    find_line_by_index, "$self, index, /",                              \
    METH_VARARGS, py_buffer_cache,                                      \
    "Retrieve the line contained in a buffer cache at a given index.\n" \
    "\n"                                                                \
    "The result is a pychrysalide.glibext.BufferLine instance or"       \
    " None.\n"                                                          \
    "\n"                                                                \
    "An read access lock has to be held for the cache; see the"         \
    " pychrysalide.glibext.BufferCache.lock() function."                \
)

    ret = PyArg_ParseTuple(args, "n", &index);
    if (!ret) return NULL;

    cache = G_BUFFER_CACHE(pygobject_get(self));

    line = g_buffer_cache_find_line_by_index(cache, index);

    if (line != NULL)
    {
        result = pygobject_new(G_OBJECT(line));
        g_object_unref(G_OBJECT(line));
    }

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

    return result;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : self = classe représentant un tampon de code.                *
*                args = arguments fournis à l'appel.                          *
*                                                                             *
*  Description : Avance autant que possible vers une ligne idéale.            *
*                                                                             *
*  Retour      : Indice de la ligne recherchée, si elle existe.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_look_for_flag(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Trouvailles à retourner     */
    size_t index;                           /* Indice de la ligne visée    */
    BufferLineFlags flag;                   /* Particularité à retrouver   */
    int ret;                                /* Bilan de lecture des args.  */
    GBufferCache *cache;                    /* Tampon natif à consulter    */
    size_t found;                           /* Indice de la ligne trouvée  */

#define BUFFER_CACHE_LOOK_FOR_FLAG_METHOD PYTHON_METHOD_DEF             \
(                                                                       \
    look_for_flag, "$self, index, flag, /",                             \
    METH_VARARGS, py_buffer_cache,                                      \
    "Iterate the buffer cache lines from a starting index until a"      \
    " line with flags matching the provided flag is met.\n"             \
    "\n"                                                                \
    "The *flag* argument has to be a"                                   \
    " pychrysalide.glibext.BufferLine.BufferLineFlags value.\n"         \
    "\n"                                                                \
    "The result is an index equal or greater than the starting index"   \
    " or, if no match is found, the number of lines in the buffer"      \
    " cache.\n"                                                         \
    "\n"                                                                \
    "An read access lock has to be held for the cache; see the"         \
    " pychrysalide.glibext.BufferCache.lock() function."                \
)

    ret = PyArg_ParseTuple(args, "nO&", &index, convert_to_buffer_line_flags, &flag);
    if (!ret) return NULL;

    cache = G_BUFFER_CACHE(pygobject_get(self));

    found = g_buffer_cache_look_for_flag(cache, index, flag);

    result = PyLong_FromSize_t(found);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Indique l'éventuel contenu binaire associé au cache.         *
*                                                                             *
*  Retour      : Eventuel contenu renseigné ou None.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_get_content(PyObject *self, void *closure)
{
    PyObject *result;                       /* Contenu binaire à retourner */
    GBufferCache *cache;                    /* Tampon natif à consulter    */
    GBinContent *content;                   /* Contenu éventuel à renvoyer */

#define BUFFER_CACHE_CONTENT_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                           \
    content, py_buffer_cache,                               \
    "Binary content linked to the buffer cache, as a"       \
    " pychrysalide.analysis.BinContent instance, or None."  \
)

    cache = G_BUFFER_CACHE(pygobject_get(self));

    content = g_buffer_cache_get_content(cache);

    if (content != NULL)
    {
        result = pygobject_new(G_OBJECT(content));
        g_object_unref(G_OBJECT(content));
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
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la hauteur d'impression d'une ligne visualisée.      *
*                                                                             *
*  Retour      : Hauteur de ligne en pixels.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_get_line_height(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBufferCache *cache;                    /* Tampon natif à consulter    */
    gint height;                            /* Valeur obtenue du cache     */

#define BUFFER_CACHE_LINE_HEIGHT_ATTRIB PYTHON_GET_DEF_FULL \
(                                                           \
    line_height, py_buffer_cache,                           \
    "Height of a line printed from the buffer cache."       \
)

    cache = G_BUFFER_CACHE(pygobject_get(self));

    height = g_buffer_cache_get_line_height(cache);

    result = PyLong_FromLong(height);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la taille réservée pour la marge gauche.             *
*                                                                             *
*  Retour      : Largeur en pixels.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_get_left_margin(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBufferCache *cache;                    /* Tampon natif à consulter    */
    gint width;                             /* Valeur obtenue du cache     */

#define BUFFER_CACHE_LEFT_MARGIN_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                               \
    left_margin, py_buffer_cache,                               \
    "Width of the left margin inside of a buffer cache output." \
)

    cache = G_BUFFER_CACHE(pygobject_get(self));

    width = g_buffer_cache_get_left_margin(cache);

    result = PyLong_FromLong(width);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Fournit la position de départ pour l'impression de texte.    *
*                                                                             *
*  Retour      : Position en pixels.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_get_text_position(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBufferCache *cache;                    /* Tampon natif à consulter    */
    gint pos;                               /* Valeur obtenue du cache     */

#define BUFFER_CACHE_TEXT_POSITION_ATTRIB PYTHON_GET_DEF_FULL               \
(                                                                           \
    text_position, py_buffer_cache,                                         \
    "Starting position of the text on the left of a buffer cache output."   \
)

    cache = G_BUFFER_CACHE(pygobject_get(self));

    pos = g_buffer_cache_get_text_position(cache);

    result = PyLong_FromLong(pos);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = objet Python concerné par l'appel.                 *
*                closure = non utilisé ici.                                   *
*                                                                             *
*  Description : Compte le nombre de lignes rassemblées dans un tampon.       *
*                                                                             *
*  Retour      : Nombre de lignes constituant le tampon.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_buffer_cache_get_lines_count(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    GBufferCache *cache;                    /* Tampon natif à consulter    */
    size_t count;                           /* Décompte de première main   */

#define BUFFER_CACHE_LINES_COUNT_ATTRIB PYTHON_GET_DEF_FULL     \
(                                                               \
    lines_count, py_buffer_cache,                               \
    "Count the number of lines contained in a buffer cache.\n"  \
    "\n"                                                        \
    "An read access lock has to be held for the cache; see the" \
    " pychrysalide.glibext.BufferCache.lock() function."        \
)

    cache = G_BUFFER_CACHE(pygobject_get(self));

    count = g_buffer_cache_count_lines(cache);

    result = PyLong_FromSize_t(count);

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

PyTypeObject *get_python_buffer_cache_type(void)
{
    static PyMethodDef py_buffer_cache_methods[] = {
        BUFFER_CACHE_LOCK_METHOD,
        BUFFER_CACHE_UNLOCK_METHOD,
        BUFFER_CACHE_INSERT_AT_METHOD,
        BUFFER_CACHE_DELETE_AT_METHOD,
        BUFFER_CACHE_DELETE_TYPE_AT_METHOD,
        BUFFER_CACHE_APPEND_METHOD,
        BUFFER_CACHE_EXTEND_WITH_METHOD,
        BUFFER_CACHE_TRUNCATE_METHOD,
        BUFFER_CACHE_ADD_LINE_FLAG_METHOD,
        BUFFER_CACHE_GET_LINE_FLAGS_METHOD,
        BUFFER_CACHE_REMOVE_LINE_FLAG_METHOD,
#ifdef INCLUDE_GTK_SUPPORT
        BUFFER_CACHE_FIND_LINE_BY_INDEX_METHOD,
#endif
        BUFFER_CACHE_LOOK_FOR_FLAG_METHOD,
        { NULL }
    };

    static PyGetSetDef py_buffer_cache_getseters[] = {
        BUFFER_CACHE_CONTENT_ATTRIB,
        BUFFER_CACHE_LINE_HEIGHT_ATTRIB,
        BUFFER_CACHE_LEFT_MARGIN_ATTRIB,
        BUFFER_CACHE_TEXT_POSITION_ATTRIB,
        BUFFER_CACHE_LINES_COUNT_ATTRIB,
        { NULL }
    };

    static PyTypeObject py_buffer_cache_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.glibext.BufferCache",
        .tp_basicsize   = sizeof(PyGObject),

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = BUFFER_CACHE_DOC,

        .tp_methods     = py_buffer_cache_methods,
        .tp_getset      = py_buffer_cache_getseters,

        .tp_init        = py_buffer_cache_init,
        .tp_new         = py_buffer_cache_new

    };

    return &py_buffer_cache_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.glibext.BufferCache'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_buffer_cache_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python 'BufferCache'   */
    PyObject *module;                       /* Module à recompléter        */
    PyObject *dict;                         /* Dictionnaire du module      */

    type = get_python_buffer_cache_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        module = get_access_to_python_module("pychrysalide.glibext");

        dict = PyModule_GetDict(module);

        if (!register_class_for_pygobject(dict, G_TYPE_BUFFER_CACHE, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en tampon de lignes.                      *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_to_buffer_cache(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */

    result = PyObject_IsInstance(arg, (PyObject *)get_python_buffer_cache_type());

    switch (result)
    {
        case -1:
            /* L'exception est déjà fixée par Python */
            result = 0;
            break;

        case 0:
            PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to buffer cache");
            break;

        case 1:
            *((GBufferCache **)dst) = G_BUFFER_CACHE(pygobject_get(arg));
            break;

        default:
            assert(false);
            break;

    }

    return result;

}
