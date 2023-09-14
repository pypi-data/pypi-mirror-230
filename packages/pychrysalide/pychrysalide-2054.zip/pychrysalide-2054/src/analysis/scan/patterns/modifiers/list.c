
/* Chrysalide - Outil d'analyse de fichiers binaires
 * list.c - gestion d'une liste de transformateurs
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "list.h"


#include <assert.h>
#include <malloc.h>


#include "list-int.h"



/* ----------------------- RECHERCHE D'UN MOTIF DE TEXTE BRUT ----------------------- */


/* Initialise la classe des liste de transformations d'octets. */
static void g_scan_modifier_list_class_init(GScanModifierListClass *);

/* Initialise une instance de liste de transformations d'octets. */
static void g_scan_modifier_list_init(GScanModifierList *);

/* Supprime toutes les références externes. */
static void g_scan_modifier_list_dispose(GScanModifierList *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_modifier_list_finalize(GScanModifierList *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Fournit le nom d'appel d'un modificateur pour motif. */
static char *g_scan_modifier_list_get_name(const GScanModifierList *);

/* Transforme une séquence d'octets pour motif de recherche. */
static bool g_scan_modifier_list_transform(const GScanModifierList *, const sized_binary_t *, sized_binary_t **, size_t *);



/* ---------------------------------------------------------------------------------- */
/*                         RECHERCHE D'UN MOTIF DE TEXTE BRUT                         */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une série de transformations d'octets. */
G_DEFINE_TYPE(GScanModifierList, g_scan_modifier_list, G_TYPE_SCAN_TOKEN_MODIFIER);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des liste de transformations d'octets.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_modifier_list_class_init(GScanModifierListClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanTokenModifierClass *modifier;      /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_modifier_list_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_modifier_list_finalize;

    modifier = G_SCAN_TOKEN_MODIFIER_CLASS(klass);

    modifier->get_name = (get_scan_modifier_name_fc)g_scan_modifier_list_get_name;

    modifier->transform = (transform_scan_token_fc)g_scan_modifier_list_transform;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de liste de transformations d'octets.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_modifier_list_init(GScanModifierList *list)
{
    list->modifiers = NULL;
    list->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_modifier_list_dispose(GScanModifierList *list)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < list->count; i++)
        g_clear_object(&list->modifiers[i]);

    G_OBJECT_CLASS(g_scan_modifier_list_parent_class)->dispose(G_OBJECT(list));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_modifier_list_finalize(GScanModifierList *list)
{
    if (list->modifiers != NULL)
        free(list->modifiers);

    G_OBJECT_CLASS(g_scan_modifier_list_parent_class)->finalize(G_OBJECT(list));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Construit une liste de modificateurs d'octets.               *
*                                                                             *
*  Retour      : Mécanisme mis en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanTokenModifier *g_scan_modifier_list_new(void)
{
    GScanTokenModifier *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_MODIFIER_LIST, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list     = liste de modificateurs à étendre.                 *
*                modifier = modificateur à intégrer.                          *
*                                                                             *
*  Description : Intègre un nouveau transformateur dans une liste.            *
*                                                                             *
*  Retour      : Bilan de l'ajout : false si un élément similaire est déjà là.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_modifier_list_add(GScanModifierList *list, GScanTokenModifier *modifier)
{
    bool result;                            /* Bilan à retourner           */
    char *name;                             /* Désignation du modificateur */
    size_t i;                               /* Boucle de parcours          */
    char *other;                            /* Désignation de ses collègues*/

    /* Recherche d'une redondance */

    /**
     * Note : deux listes identiques passent sans soucis.
     * TODO : comparer les transformateurs ?
     */

    result = true;

    if (!G_IS_SCAN_MODIFIER_LIST(modifier))
    {
        name = g_scan_token_modifier_get_name(modifier);

        for (i = 0; i < list->count && result; i++)
        {
            if (G_IS_SCAN_MODIFIER_LIST(list->modifiers[i]))
                continue;

            other = g_scan_token_modifier_get_name(list->modifiers[i]);

            result = (strcmp(name, other) != 0);

            free(other);

        }

    }

    free(name);

    if (!result)
        goto done;

    /* Inclusion dans la liste */

    list->modifiers = realloc(list->modifiers, ++list->count * sizeof(GScanTokenModifier *));

    list->modifiers[list->count - 1] = modifier;
    g_object_ref(G_OBJECT(modifier));

 done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = série à consulter.                                    *
*                                                                             *
*  Description : Indique le nombre de transformateurs intégrés dans la liste. *
*                                                                             *
*  Retour      : Nombre de modificateurs représentés.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_scan_modifier_list_count(const GScanModifierList *list)
{
    size_t result;                          /* Quantité à retourner        */

    result = list->count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list  = série à consulter.                                   *
*                index = indice du paramètre à retourner.                     *
*                                                                             *
*  Description : Fournit un transformateur donné de la liste.                 *
*                                                                             *
*  Retour      : Modificateur inclus dans la liste ou NULL si mauvais indice. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanTokenModifier *g_scan_modifier_list_get(const GScanModifierList *list, size_t index)
{
    GScanTokenModifier *result;             /* Instance à retourner        */

    assert(index < list->count);

    if (index < list->count)
    {
        result = list->modifiers[index];
        g_object_ref(G_OBJECT(result));
    }

    else
        result = NULL;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : modifier = modificateur à consulter.                         *
*                                                                             *
*  Description : Fournit le nom d'appel d'un modificateur pour motif.         *
*                                                                             *
*  Retour      : Désignation humaine.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_scan_modifier_list_get_name(const GScanModifierList *modifier)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("(list)");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : modifier = modificateur à solliciter.                        *
*                src      = séquence d'octets à traiter.                      *
*                dest     = nouvelle(s) séquence(s) d'octets obtenue(s) [OUT] *
*                count    = quantité de ces séquences.                        *
*                                                                             *
*  Description : Transforme une séquence d'octets pour motif de recherche.    *
*                                                                             *
*  Retour      : Bilan de l'opération : succès ou échec.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_scan_modifier_list_transform(const GScanModifierList *modifier, const sized_binary_t *src, sized_binary_t **dest, size_t *count)
{
    bool result;                            /* Bilan d'opération à renvoyer*/
    size_t i;                               /* Boucle de parcours #1       */
    sized_binary_t *extra;                  /* Motifs supplémentaires      */
    size_t extra_count;                     /* Quantité de ces motifs      */
    sized_binary_t *new;                    /* Nouvel emplacement libre    */
    size_t k;                               /* Boucle de parcours #2       */

    *dest = NULL;
    *count = 0;

    for (i = 0; i < modifier->count; i++)
    {
        result = g_scan_token_modifier_transform(modifier->modifiers[i], src, &extra, &extra_count);
        if (!result) goto exit;

        new = (*dest) + *count;

        *count += extra_count;
        *dest = realloc(*dest, *count * sizeof(sized_binary_t)); 

        for (k = 0; k < extra_count; k++, new++)
            copy_szstr(*new, extra[k]);

        free(extra);

    }

 exit:

    if (!result)
    {
        for (i = 0; i < *count; i++)
            exit_szstr(dest[i]);

        if (*dest != NULL)
            free(*dest);

        *dest = NULL;
        *count = 0;

    }

    return result;

}
