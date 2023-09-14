
/* Chrysalide - Outil d'analyse de fichiers binaires
 * objhole.h - prototypes pour l'utilisation d'un espace inutilisé dans la structure GObject
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _GLIBEXT_OBJHOLE_H
#define _GLIBEXT_OBJHOLE_H


#include <glib.h>
#include <glib-object.h>


#include "../common/cpp.h"



/**
 * Une structure GObject a la définition suivante :
 *
 *    struct  _GObject
 *    {
 *        GTypeInstance  g_type_instance;
 *        volatile guint ref_count;
 *        GData          *qdata;
 *    };
 *
 * En revanche, le fichier "glib/gobject/gobject.c" précise la définition
 * réelle de la structure selon l'environnement :
 *
 *    #if SIZEOF_INT == 4 && GLIB_SIZEOF_VOID_P == 8
 *    #define HAVE_OPTIONAL_FLAGS
 *    #endif
 *
 *    typedef struct
 *    {
 *      GTypeInstance  g_type_instance;
 *      guint          ref_count;
 *    #ifdef HAVE_OPTIONAL_FLAGS
 *      guint          optional_flags;
 *    #endif
 *      GData         *qdata;
 *    } GObjectReal;
 *
 *    G_STATIC_ASSERT(sizeof(GObject) == sizeof(GObjectReal));
 *    G_STATIC_ASSERT(G_STRUCT_OFFSET(GObject, ref_count) == G_STRUCT_OFFSET(GObjectReal, ref_count));
 *    G_STATIC_ASSERT(G_STRUCT_OFFSET(GObject, qdata) == G_STRUCT_OFFSET(GObjectReal, qdata));
 *
 * L'espace entre les deux derniers champs ne peut donc être pleinement exploité deux fois.
 */

#if 0

#   define GET_GOBJECT_EXTRA(obj, tp)                           \
    ({                                                          \
        BUILD_BUG_ON(sizeof(tp) > sizeof(guint));               \
        tp *___result;                                          \
        ___result = (tp *)(((guint *)&obj->ref_count) + 1);     \
        BUILD_BUG_ON((___result + 1) == (tp *)&obj->qdata);     \
        ___result;                                              \
    })

#endif


/**
 * Choix du bit de verrou pour le champ "lock".
 *
 * Dans la structure exploitant le mot utilisé ici, ce verrou est généralement
 * placé dans le bit de poids fort pour les objets qui l'utilisent.
 */

#if __BYTE_ORDER == __LITTLE_ENDIAN

#   define HOLE_LOCK_BIT 31

#elif __BYTE_ORDER == __BIG_ENDIAN

#   define HOLE_LOCK_BIT 0

#else

#   error "Unknown byte order"

#endif


/* Verrou d'accès pour une encapsulation */
typedef struct _lockable_obj_extra_t
{
    gint lock;                              /* Gestion d'accès aux fanions */

} lockable_obj_extra_t;


#define INIT_GOBJECT_EXTRA_LOCK(xtr)                    \
    do                                                  \
    {                                                   \
        lockable_obj_extra_t *__lockable;               \
        __lockable = (lockable_obj_extra_t *)xtr;       \
        __lockable->lock = 0;                           \
    }                                                   \
    while (0)

#define LOCK_GOBJECT_EXTRA(xtr)                         \
    do                                                  \
    {                                                   \
        lockable_obj_extra_t *__lockable;               \
        __lockable = (lockable_obj_extra_t *)xtr;       \
        g_bit_lock(&__lockable->lock, HOLE_LOCK_BIT);   \
    }                                                   \
    while (0)

#define UNLOCK_GOBJECT_EXTRA(xtr)                       \
    do                                                  \
    {                                                   \
        lockable_obj_extra_t *__lockable;               \
        __lockable = (lockable_obj_extra_t *)xtr;       \
        g_bit_unlock(&__lockable->lock, HOLE_LOCK_BIT); \
    }                                                   \
    while (0)



#endif  /* _GLIBEXT_OBJHOLE_H */
