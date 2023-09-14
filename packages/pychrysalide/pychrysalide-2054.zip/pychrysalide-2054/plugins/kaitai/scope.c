
/* Chrysalide - Outil d'analyse de fichiers binaires
 * scope.c - recherches d'éléments de lecture
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#include "scope.h"


#include "parsers/struct.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : locals = contexte de variables locales à initialiser.        *
*                meta   = informations générales à disposition.               *
*                                                                             *
*  Description : Initialise un contexte pour correspondances Kaitai établies. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void init_record_scope(kaitai_scope_t *locals, GKaitaiMeta *meta)
{
    locals->meta = meta;

    if (meta != NULL)
        g_object_ref(G_OBJECT(meta));

    locals->root = NULL;
    locals->parent = NULL;
    locals->last = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : locals = contexte de variables locales à réinitialiser.      *
*                                                                             *
*  Description : Vide un contexte de correspondances Kaitai établies.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void reset_record_scope(kaitai_scope_t *locals)
{
    g_clear_object(&locals->meta);

    g_clear_object(&locals->root);
    g_clear_object(&locals->parent);
    g_clear_object(&locals->last);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = contexte de variables locales à initialiser.          *
*                src  = contexte de variables locales à copier.               *
*                                                                             *
*  Description : Copie un contexte de correspondances Kaitai établies.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void copy_record_scope(kaitai_scope_t *dest, const kaitai_scope_t *src)
{
    reset_record_scope(dest);

#define COPY_SCOPE_ITEM(itm)                    \
    dest->itm = src->itm;                       \
    if (dest->itm != NULL)                      \
        g_object_ref(G_OBJECT(dest->itm));

    COPY_SCOPE_ITEM(meta);

    COPY_SCOPE_ITEM(root);
    COPY_SCOPE_ITEM(parent);
    COPY_SCOPE_ITEM(last);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : locals = variables locales pour les résolutions de types.    *
*                                                                             *
*  Description : Retourne le souvenir d'une correspondance racine.            *
*                                                                             *
*  Retour      : Dernière correspondance établie ou NULL.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GMatchRecord *get_root_record(const kaitai_scope_t *locals)
{
    GMatchRecord *result;                   /* Instance à retourner        */

    result = locals->root;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : locals = variables locales pour les résolutions de types.    *
*                                                                             *
*  Description : Retourne le souvenir de la correspondance parente effectuée. *
*                                                                             *
*  Retour      : Dernière correspondance établie ou NULL.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GMatchRecord *get_parent_record(const kaitai_scope_t *locals)
{
    GMatchRecord *result;                   /* Instance à retourner        */

    result = locals->parent;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : locals = variables locales pour les résolutions de types.    *
*                record = dernière correspondance établie.                    *
*                                                                             *
*  Description : Conserve le souvenir de la dernière correspondance effectuée.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void remember_last_record(kaitai_scope_t *locals, GMatchRecord *record)
{
    g_clear_object(&locals->last);

    locals->last = record;

    if (record != NULL)
        g_object_ref(G_OBJECT(record));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : locals = variables locales pour les résolutions de types.    *
*                                                                             *
*  Description : Retourne le souvenir de la dernière correspondance effectuée.*
*                                                                             *
*  Retour      : Dernière correspondance établie ou NULL.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GMatchRecord *get_last_record(const kaitai_scope_t *locals)
{
    GMatchRecord *result;                   /* Instance à retourner        */

    result = locals->last;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : locals = variables locales pour les résolutions de types.    *
*                name   = désignation du type particulier ciblé.              *
*                                                                             *
*  Description : Recherche la définition d'un type nouveau pour Kaitai.       *
*                                                                             *
*  Retour      : Type prêt à emploi ou NULL si non trouvé.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiType *find_sub_type(const kaitai_scope_t *locals, const char *name)
{
    GKaitaiType *result;                    /* Instance à retourner        */
    size_t i;                               /* Boucle de parcours          */
    GKaitaiParser *parser;                  /* Lecteur d'origine           */

    GMatchRecord *list[] = { locals->root, locals->parent, locals->last };

    result = NULL;

    for (i = 0; i < 3; i++)
    {
        if (list[i] == NULL)
            continue;

        parser = g_match_record_get_creator(list[i]);

        if (G_IS_KAITAI_STRUCT(parser))
            result = g_kaitai_structure_find_sub_type(G_KAITAI_STRUCT(parser), name);

        g_object_unref(G_OBJECT(parser));

        if (result != NULL)
            break;

    }

    return result;

}
