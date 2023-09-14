
/* Chrysalide - Outil d'analyse de fichiers binaires
 * preload.c - préchargement d'instructions à partir d'un format
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "preload.h"


#include <assert.h>


#include "preload-int.h"



/* Initialise la classe des préchargements à partir d'un format. */
static void g_preload_info_class_init(GPreloadInfoClass *);

/* Initialise une instance de préchargement à partir de format. */
static void g_preload_info_init(GPreloadInfo *);

/* Supprime toutes les références externes. */
static void g_preload_info_dispose(GPreloadInfo *);

/* Procède à la libération totale de la mémoire. */
static void g_preload_info_finalize(GPreloadInfo *);



/* Indique le type défini pour un préchargement à partir d'un format. */
G_DEFINE_TYPE(GPreloadInfo, g_preload_info, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des préchargements à partir d'un format.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_preload_info_class_init(GPreloadInfoClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_preload_info_dispose;
    object->finalize = (GObjectFinalizeFunc)g_preload_info_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de préchargement à partir de format. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_preload_info_init(GPreloadInfo *info)
{
    info->instructions = NULL;

    info->comments = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_preload_info_dispose(GPreloadInfo *info)
{
    size_t count;                           /* Borne de parcours           */
    size_t i;                               /* Boucle de parcours          */
    GArchInstruction *instr;                /* Instruction à libérer       */
    GDbComment *comment;                    /* Commentaire à libérer       */

    g_preload_info_lock_instructions(info);

    count = _g_preload_info_count_instructions(info);

    for (i = 0; i < count; i++)
    {
        instr = _g_preload_info_grab_instruction(info, i);
        g_object_unref(G_OBJECT(instr));
    }

    _g_preload_info_drain_instructions(info);

    g_preload_info_unlock_instructions(info);

    g_preload_info_lock_comments(info);

    count = _g_preload_info_count_comments(info);

    for (i = 0; i < count; i++)
    {
        comment = _g_preload_info_grab_comment(info, i);
        g_object_unref(G_OBJECT(comment));
    }

    _g_preload_info_drain_comments(info);

    g_preload_info_unlock_comments(info);

    G_OBJECT_CLASS(g_preload_info_parent_class)->dispose(G_OBJECT(info));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_preload_info_finalize(GPreloadInfo *info)
{
    G_OBJECT_CLASS(g_preload_info_parent_class)->finalize(G_OBJECT(info));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une nouvelle collecte d'informations préchargées.       *
*                                                                             *
*  Retour      : Adresse de l'instance mise en place ou NULL en cas d'échec.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPreloadInfo *g_preload_info_new(void)
{
    GPreloadInfo *result;                   /* Nouveau preloade à renvoyer */

    result = g_object_new(G_TYPE_PRELOAD_INFO, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : src  = collecte à consulter.                                 *
*                dest = collecte à constituer. [OUT]                          *
*                                                                             *
*  Description : Copie le contenu d'une collecte d'informations préchargées.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_preload_info_copy(GPreloadInfo *src, GPreloadInfo *dest)
{
    void inc_preloaded_item_ref(GObject **item)
    {
        g_object_ref(*item);
    }

    copy_flat_array_items(&src->instructions, &dest->instructions,
                          sizeof(GArchInstruction *), (item_notify_cb)inc_preloaded_item_ref);

    copy_flat_array_items(&src->comments, &dest->comments,
                          sizeof(GDbComment *), (item_notify_cb)inc_preloaded_item_ref);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = préchargements à mettre à jour.                       *
*                                                                             *
*  Description : Verrouille les accès à la liste des instructions.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_preload_info_lock_instructions(GPreloadInfo *info)
{
    lock_flat_array(&info->instructions);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = préchargements à mettre à jour.                       *
*                                                                             *
*  Description : Déverrouille les accès à la liste des instructions.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_preload_info_unlock_instructions(GPreloadInfo *info)
{
    unlock_flat_array(&info->instructions);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info  = instance à mettre à jour.                            *
*                instr = instruction à venir associer.                        *
*                                                                             *
*  Description : Ajoute une instruction supplémentaire aux préchargements.    *
*                                                                             *
*  Retour      : true si l'instruction a bien été insérée, false sinon.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_preload_info_add_instruction(GPreloadInfo *info, GArchInstruction *instr)
{
    bool result;                            /* Bilan à retourner           */

    g_preload_info_lock_instructions(info);

    result = _g_preload_info_add_instruction(info, instr);

    g_preload_info_unlock_instructions(info);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info  = instance à mettre à jour.                            *
*                instr = instruction à venir associer.                        *
*                                                                             *
*  Description : Ajoute une instruction supplémentaire aux préchargements.    *
*                                                                             *
*  Retour      : true si l'instruction a bien été insérée, false sinon.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _g_preload_info_add_instruction(GPreloadInfo *info, GArchInstruction *instr)
{
    bool result;                            /* Bilan à retourner           */

    int cmp_instr_by_addr(const GArchInstruction **a, const GArchInstruction **b)
    {
        const mrange_t *range_a;            /* Emplacement pour l'instr. A */
        const mrange_t *range_b;            /* Emplacement pour l'instr. B */

        range_a = g_arch_instruction_get_range(*a);
        range_b = g_arch_instruction_get_range(*b);

        return cmp_vmpa(get_mrange_addr(range_a), get_mrange_addr(range_b));

    }

    result = !_g_preload_info_has_instruction_for(info, g_arch_instruction_get_range(instr));

    if (result)
        insert_item_into_flat_array(&info->instructions, &instr, sizeof(GArchInstruction *),
                                    (__compar_fn_t)cmp_instr_by_addr);

    else
        g_object_unref(G_OBJECT(instr));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info  = instance à mettre à jour.                            *
*                range = emplacement de l'instruction recherchés.             *
*                                                                             *
*  Description : Détermine si une instruction existe sur un espace donné.     *
*                                                                             *
*  Retour      : true si une instruction existe à l'emplacement indiqué.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _g_preload_info_has_instruction_for(GPreloadInfo *info, const mrange_t *range)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstruction **ptr;                 /* Adresse dans le tableau     */

    int check_for_overlap(const mrange_t *key, const GArchInstruction **i)
    {
        const mrange_t *irange;             /* Emplacement pour l'instr.   */
        int status;                         /* Bilan de la recherche       */

        irange = g_arch_instruction_get_range(*i);

        if (mrange_intersects_mrange(irange, key))
            status = 0;

        else
            status = cmp_vmpa(get_mrange_addr(key), get_mrange_addr(irange));

        return status;

    }

    ptr = find_item_in_flat_array(info->instructions, sizeof(GArchInstruction *),
                                  (__compar_fn_t)check_for_overlap, range);

    result = (ptr != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info  = instance à mettre à jour.                            *
*                addr = localisation de l'instruction recherchée.             *
*                                                                             *
*  Description : Détermine si une instruction est présente à un point donné.  *
*                                                                             *
*  Retour      : true si une instruction existe à l'emplacement indiqué.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _g_preload_info_has_instruction_at(GPreloadInfo *info, const vmpa2t *addr)
{
    bool result;                            /* Bilan à retourner           */
    GArchInstruction **ptr;                 /* Adresse dans le tableau     */

    int cmp_instr_by_addr(const vmpa2t *key, const GArchInstruction **i)
    {
        const mrange_t *range;              /* Emplacement pour l'instr.   */

        range = g_arch_instruction_get_range(*i);

        return cmp_vmpa(key, get_mrange_addr(range));

    }

    ptr = find_item_in_flat_array(info->instructions, sizeof(GArchInstruction *),
                                  (__compar_fn_t)cmp_instr_by_addr, addr);

    result = (ptr != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = instance à consulter.                                 *
*                                                                             *
*  Description : Indique la quantité d'instructions préchargées disponibles.  *
*                                                                             *
*  Retour      : Nombre d'instructions attachées.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t _g_preload_info_count_instructions(const GPreloadInfo *info)
{
    size_t result;                          /* Décompte à retourner        */

    result = count_flat_array_items(info->instructions);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info  = instance à consulter.                                *
*                index = indice de l'instruction concernée.                   *
*                                                                             *
*  Description : Fournit une instruction préchargée donnée.                   *
*                                                                             *
*  Retour      : Instruction trouvée.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *_g_preload_info_grab_instruction(const GPreloadInfo *info, size_t index)
{
    GArchInstruction *result;               /* Opérande à retourner        */
    GArchInstruction **ptr;                 /* Adresse dans le tableau     */

    ptr = get_flat_array_item(info->instructions, index, sizeof(GArchInstruction *));

    result = *ptr;

    /**
     * La propriétée de l'élément est transmise à l'appelant.
     *
     * Ainsi, pour vider une liste via _g_preload_info_drain_instructions(),
     * il suffit juste de libérer la mémoire occupée pour le stockage sans
     * se préoccuper des références contenues ; le gain de temps est important
     * puisqu'on évite là un parcours et des déplacements.
     */

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = instance à manipuler.                                 *
*                                                                             *
*  Description : Dépile une instruction présente dans les préchargements.     *
*                                                                             *
*  Retour      : Instruction retirée ou NULL si aucune.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_preload_info_pop_instruction(GPreloadInfo *info)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    GArchInstruction **ptr;                 /* Adresse dans le tableau     */

    g_preload_info_lock_instructions(info);

    if (_g_preload_info_count_instructions(info) == 0)
        result = NULL;

    else
    {
        ptr = get_flat_array_item(info->instructions, 0, sizeof(GArchInstruction *));
        result = *ptr;

        rem_item_from_flat_array(&info->instructions, 0, sizeof(GArchInstruction *));

    }

    g_preload_info_unlock_instructions(info);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = instance à manipuler.                                 *
*                                                                             *
*  Description : Retire des préchargements toutes les instructions.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void _g_preload_info_drain_instructions(GPreloadInfo *info)
{
    /**
     * A utiliser en conjonction avec _g_preload_info_grab_instruction()
     * uniquement.
     */

    reset_flat_array(&info->instructions);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = préchargements à mettre à jour.                       *
*                                                                             *
*  Description : Verrouille les accès à la liste des commentaires.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_preload_info_lock_comments(GPreloadInfo *info)
{
    lock_flat_array(&info->comments);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = préchargements à mettre à jour.                       *
*                                                                             *
*  Description : Déverrouille les accès à la liste des commentaires.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_preload_info_unlock_comments(GPreloadInfo *info)
{
    unlock_flat_array(&info->comments);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info    = instance à mettre à jour.                          *
*                comment = commentaire à venir associer.                      *
*                                                                             *
*  Description : Ajoute un commentaire supplémentaire aux préchargements.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_preload_info_add_comment(GPreloadInfo *info, GDbComment *comment)
{
    g_preload_info_lock_comments(info);

    _g_preload_info_add_comment(info, comment);

    g_preload_info_unlock_comments(info);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info    = instance à mettre à jour.                          *
*                comment = commentaire à venir associer.                      *
*                                                                             *
*  Description : Ajoute un commentaire supplémentaire aux préchargements.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void _g_preload_info_add_comment(GPreloadInfo *info, GDbComment *comment)
{
    int cmp_comment_by_addr(const GDbComment * const *a, const GDbComment * const *b)
    {
        const vmpa2t *addr_a;               /* Position du commentaire A   */
        const vmpa2t *addr_b;               /* Position du commentaire B   */

        addr_a = g_db_comment_get_address(*a);
        addr_b = g_db_comment_get_address(*b);

        return cmp_vmpa(addr_a, addr_b);

    }

    insert_item_into_flat_array(&info->comments, &comment, sizeof(GDbComment *),
                                (__compar_fn_t)cmp_comment_by_addr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = instance à mettre à consulter.                        *
*                addr = localisation du commentaire recherché.                *
*                                                                             *
*  Description : Recherche un commentaire dans des préchargements.            *
*                                                                             *
*  Retour      : Eventuel commentaire retrouvé ou NULL.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbComment *_g_preload_info_find_comment_at(GPreloadInfo *info, const vmpa2t *addr)
{
    GDbComment *result;                     /* Trouvaille à retourner      */
    GDbComment **ptr;                       /* Adresse dans le tableau     */

    ptr = find_item_in_flat_array(info->comments, sizeof(GDbComment *),
                                     (__compar_fn_t)compare_comment_by_addr, addr);

    if (ptr != NULL)
    {
        result = *ptr;
        g_object_ref(G_OBJECT(result));
    }
    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info  = instance à mettre à consulter.                       *
*                addr  = localisation du commentaire recherché.               *
*                index = indice du commentaire retrouvé ou NULL. [OUT]        *
*                                                                             *
*  Description : Recherche un commentaire dans des préchargements.            *
*                                                                             *
*  Retour      : Eventuel commentaire retrouvé ou NULL.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbComment *g_preload_info_find_comment_at(GPreloadInfo *info, const vmpa2t *addr, size_t *index)
{
    GDbComment *result;                     /* Trouvaille à retourner      */
    GDbComment **ptr;                       /* Adresse dans le tableau     */

    ptr = find_item_in_flat_array(info->comments, sizeof(GDbComment *),
                                     (__compar_fn_t)compare_comment_by_addr, addr);

    if (ptr != NULL)
    {
        result = *ptr;
        g_object_ref(G_OBJECT(result));

        if (index != NULL)
            *index = ((void **)ptr - info->comments);

    }
    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info    = instance à mettre à jour.                          *
*                index   = indice du commentaire à remplacer.                 *
*                comment = commentaire à venir associer.                      *
*                                                                             *
*  Description : Remplace un commentaire par un autre à un emplacement donné. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_preload_info_replace_comment_at(GPreloadInfo *info, size_t index, GDbComment *comment)
{
#ifndef NDEBUG
    GDbComment **current;                   /* Commentaire à remplacer     */
#endif

#ifndef NDEBUG
    current = get_flat_array_item(info->comments, index, sizeof(GDbComment *));

    assert(cmp_vmpa(g_db_comment_get_address(*current), g_db_comment_get_address(comment)));
#endif

    rpl_item_in_flat_array(info->comments, index, &comment, sizeof(GDbComment *));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = instance à consulter.                                 *
*                                                                             *
*  Description : Indique la quantité de commentaires préchargés disponibles.  *
*                                                                             *
*  Retour      : Nombre de commentaires attachés.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t _g_preload_info_count_comments(const GPreloadInfo *info)
{
    size_t result;                          /* Décompte à retourner        */

    result = count_flat_array_items(info->comments);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info  = instance à consulter.                                *
*                index = indice de l'instruction concernée.                   *
*                                                                             *
*  Description : Fournit un commentaire préchargé donné.                      *
*                                                                             *
*  Retour      : Commentaire trouvé.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbComment *_g_preload_info_grab_comment(const GPreloadInfo *info, size_t index)
{
    GDbComment *result;                     /* Opérande à retourner        */
    GDbComment **ptr;                       /* Adresse dans le tableau     */

    ptr = get_flat_array_item(info->comments, index, sizeof(GDbComment *));

    result = *ptr;

    /**
     * La propriétée de l'élément est transmise à l'appelant.
     *
     * Ainsi, pour vider une liste via _g_preload_info_drain_comments(),
     * il suffit juste de libérer la mémoire occupée pour le stockage sans
     * se préoccuper des références contenues ; le gain de temps est important
     * puisqu'on évite là un parcours et des déplacements.
     */

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = instance à manipuler.                                 *
*                                                                             *
*  Description : Retire des préchargements tous les commentaires.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void _g_preload_info_drain_comments(GPreloadInfo *info)
{
    /**
     * A utiliser en conjonction avec _g_preload_info_grab_comment()
     * uniquement.
     */

    reset_flat_array(&info->comments);

}
