
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - enregistrement des fonctions principales
 *
 * Copyright (C) 2022 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "core.h"


#include <malloc.h>
#include <string.h>


#include "items/count.h"
#include "items/datasize.h"
#include "items/uint.h"
#include "items/console/log.h"
#ifdef INCLUDE_MAGIC_SUPPORT
#   include "items/magic/type.h"
#   include "items/magic/mime-encoding.h"
#   include "items/magic/mime-type.h"
#endif
#include "items/math/to_string.h"
#include "items/string/lower.h"
#include "items/string/to_int.h"
#include "items/string/upper.h"
#include "items/time/make.h"
#include "items/time/now.h"
#include "patterns/modifiers/hex.h"
#include "patterns/modifiers/plain.h"
#include "patterns/modifiers/rev.h"


/* Liste des modificateurs disponibles */

typedef struct _available_modifier_t
{
    char *name;                             /* Désignation humaine         */
    GScanTokenModifier *instance;           /* Mécanisme correspondant     */

} available_modifier_t;

static available_modifier_t *__modifiers = NULL;
static size_t __modifiers_count = 0;


/******************************************************************************
*                                                                             *
*  Paramètres  : modifier = modificateur à rendre disponible.                 *
*                                                                             *
*  Description : Inscrit un modificateur dans la liste des disponibles.       *
*                                                                             *
*  Retour      : Bilan des enregistrements effectués : true si nouveauté.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_scan_token_modifier(GScanTokenModifier *modifier)
{
    bool result;                            /* Bilan à retourner           */
    char *name;                             /* Nom donné au modificateur   */
    GScanTokenModifier *found;              /* Alternative présente        */
    available_modifier_t *last;             /* Emplacement disponible      */

    name = g_scan_token_modifier_get_name(modifier);

    found = find_scan_token_modifiers_for_name(name);

    result = (found == NULL);

    if (!result)
        free(name);

    else
    {
        __modifiers_count++;
        __modifiers = realloc(__modifiers, __modifiers_count * sizeof(available_modifier_t));

        last = &__modifiers[__modifiers_count - 1];

        last->name = name;
        last->instance = modifier;

        g_object_ref(G_OBJECT(modifier));

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Charge tous les modificateurs de base.                       *
*                                                                             *
*  Retour      : Bilan des opérations d'enregistrement.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_all_known_scan_token_modifiers(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

#define REGISTER_SCAN_MODIFIER(m)                   \
    ({                                              \
        bool __status;                              \
        __status = register_scan_token_modifier(m); \
        g_object_unref(G_OBJECT(m));                \
        __status;                                   \
    })

    if (result) result = REGISTER_SCAN_MODIFIER(g_scan_hex_modifier_new());
    if (result) result = REGISTER_SCAN_MODIFIER(g_scan_plain_modifier_new());
    if (result) result = REGISTER_SCAN_MODIFIER(g_scan_reverse_modifier_new());

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Décharge tous les modificateurs inscrits.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_all_scan_token_modifiers(void)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < __modifiers_count; i++)
        g_object_unref(G_OBJECT(__modifiers[i].instance));

    if (__modifiers != NULL)
        free(__modifiers);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : name = désignation du modificateur recherché.                *
*                                                                             *
*  Description : Fournit le modificateur correspondant à un nom.              *
*                                                                             *
*  Retour      : Instance du modificateur identifié ou NULL.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanTokenModifier *find_scan_token_modifiers_for_name(const char *name)
{
    GScanTokenModifier *result;             /* Instance à renvoyer         */
    size_t i;                               /* Boucle de parcours          */
    available_modifier_t *registered;       /* Infos d'enregistrement      */

    result = NULL;

    for (i = 0; i < __modifiers_count; i++)
    {
        registered = __modifiers + i;

        if (strcmp(registered->name, name) == 0)
        {
            result = registered->instance;
            g_object_ref(G_OBJECT(result));
            break;
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : space = espace de noms à composer.                           *
*                                                                             *
*  Description : Inscrit les principales fonctions dans l'espace racine.      *
*                                                                             *
*  Retour      : Bilan des enregistrements effectués.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_main_scan_namespace(GScanNamespace *space)
{
    bool result;                            /* Bilan à retourner           */
    GScanNamespace *ns;                     /* Nouvel espace de noms       */

    result = true;

#define REGISTER_FUNC(s, f)                                 \
    ({                                                      \
        bool __result;                                      \
        __result = g_scan_namespace_register_item(s, f);    \
        g_object_unref(G_OBJECT(f));                        \
        __result;                                           \
    })

    if (result) result = REGISTER_FUNC(space, g_scan_count_function_new());
    if (result) result = REGISTER_FUNC(space, g_scan_datasize_function_new());

    if (result) result = REGISTER_FUNC(space, g_scan_uint_function_new(MDS_8_BITS_SIGNED, SRE_LITTLE));
    if (result) result = REGISTER_FUNC(space, g_scan_uint_function_new(MDS_8_BITS_UNSIGNED, SRE_LITTLE));

    if (result) result = REGISTER_FUNC(space, g_scan_uint_function_new(MDS_16_BITS_SIGNED, SRE_LITTLE));
    if (result) result = REGISTER_FUNC(space, g_scan_uint_function_new(MDS_16_BITS_SIGNED, SRE_BIG));
    if (result) result = REGISTER_FUNC(space, g_scan_uint_function_new(MDS_16_BITS_UNSIGNED, SRE_LITTLE));
    if (result) result = REGISTER_FUNC(space, g_scan_uint_function_new(MDS_16_BITS_UNSIGNED, SRE_BIG));

    if (result) result = REGISTER_FUNC(space, g_scan_uint_function_new(MDS_32_BITS_SIGNED, SRE_LITTLE));
    if (result) result = REGISTER_FUNC(space, g_scan_uint_function_new(MDS_32_BITS_SIGNED, SRE_BIG));
    if (result) result = REGISTER_FUNC(space, g_scan_uint_function_new(MDS_32_BITS_UNSIGNED, SRE_LITTLE));
    if (result) result = REGISTER_FUNC(space, g_scan_uint_function_new(MDS_32_BITS_UNSIGNED, SRE_BIG));

    if (result) result = REGISTER_FUNC(space, g_scan_uint_function_new(MDS_64_BITS_SIGNED, SRE_LITTLE));
    if (result) result = REGISTER_FUNC(space, g_scan_uint_function_new(MDS_64_BITS_SIGNED, SRE_BIG));
    if (result) result = REGISTER_FUNC(space, g_scan_uint_function_new(MDS_64_BITS_UNSIGNED, SRE_LITTLE));
    if (result) result = REGISTER_FUNC(space, g_scan_uint_function_new(MDS_64_BITS_UNSIGNED, SRE_BIG));

    /* Console */

    if (result)
    {
        ns = g_scan_namespace_new("console");
        result = g_scan_namespace_register_item(space, G_REGISTERED_ITEM(ns));

        if (result) result = REGISTER_FUNC(ns, g_scan_console_log_function_new());

        g_object_unref(G_OBJECT(ns));

    }

    /* Magic */

#ifdef INCLUDE_MAGIC_SUPPORT
    if (result)
    {
        ns = g_scan_namespace_new("magic");
        result = g_scan_namespace_register_item(space, G_REGISTERED_ITEM(ns));

        if (result) result = REGISTER_FUNC(ns, g_scan_magic_type_function_new());
        if (result) result = REGISTER_FUNC(ns, g_scan_mime_encoding_function_new());
        if (result) result = REGISTER_FUNC(ns, g_scan_mime_type_function_new());

        g_object_unref(G_OBJECT(ns));

    }
#endif

    /* Math */

    if (result)
    {
        ns = g_scan_namespace_new("math");
        result = g_scan_namespace_register_item(space, G_REGISTERED_ITEM(ns));

        if (result) result = REGISTER_FUNC(ns, g_scan_math_to_string_function_new());

        g_object_unref(G_OBJECT(ns));

    }

    /* String */

    if (result)
    {
        ns = g_scan_namespace_new("string");
        result = g_scan_namespace_register_item(space, G_REGISTERED_ITEM(ns));

        if (result) result = REGISTER_FUNC(ns, g_scan_string_lower_function_new());
        if (result) result = REGISTER_FUNC(ns, g_scan_string_to_int_function_new());
        if (result) result = REGISTER_FUNC(ns, g_scan_string_upper_function_new());

        g_object_unref(G_OBJECT(ns));

    }

    /* Time */

    if (result)
    {
        ns = g_scan_namespace_new("time");
        result = g_scan_namespace_register_item(space, G_REGISTERED_ITEM(ns));

        if (result) result = REGISTER_FUNC(ns, g_scan_time_make_function_new());
        if (result) result = REGISTER_FUNC(ns, g_scan_time_now_function_new());

        g_object_unref(G_OBJECT(ns));

    }

    return result;

}
