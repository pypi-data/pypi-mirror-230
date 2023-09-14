
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rev.c - transormation via inversement d'une séquence d'octets
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


#include "rev.h"


#include <malloc.h>
#include <string.h>


#include "../modifier-int.h"



/* ----------------------- RECHERCHE D'UN MOTIF DE TEXTE BRUT ----------------------- */


/* Initialise la classe des transmissions via inversement. */
static void g_scan_reverse_modifier_class_init(GScanReverseModifierClass *klass);

/* Initialise une instance de transmission via inversement. */
static void g_scan_reverse_modifier_init(GScanReverseModifier *);

/* Supprime toutes les références externes. */
static void g_scan_reverse_modifier_dispose(GScanReverseModifier *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_reverse_modifier_finalize(GScanReverseModifier *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Fournit le nom d'appel d'un modificateur pour motif. */
static char *g_scan_reverse_modifier_get_name(const GScanReverseModifier *);

/* Transforme une séquence d'octets pour motif de recherche. */
static bool g_scan_reverse_modifier_transform(const GScanReverseModifier *, const sized_binary_t *, sized_binary_t **, size_t *);



/* ---------------------------------------------------------------------------------- */
/*                         RECHERCHE D'UN MOTIF DE TEXTE BRUT                         */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une transormation via inversement d'une séquence d'octets. */
G_DEFINE_TYPE(GScanReverseModifier, g_scan_reverse_modifier, G_TYPE_SCAN_TOKEN_MODIFIER);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des transmissions via inversement.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_reverse_modifier_class_init(GScanReverseModifierClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanTokenModifierClass *modifier;      /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_reverse_modifier_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_reverse_modifier_finalize;

    modifier = G_SCAN_TOKEN_MODIFIER_CLASS(klass);

    modifier->get_name = (get_scan_modifier_name_fc)g_scan_reverse_modifier_get_name;

    modifier->transform = (transform_scan_token_fc)g_scan_reverse_modifier_transform;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : modifier = instance à initialiser.                           *
*                                                                             *
*  Description : Initialise une instance de transmission via inversement.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_reverse_modifier_init(GScanReverseModifier *modifier)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : modifier = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_reverse_modifier_dispose(GScanReverseModifier *modifier)
{
    G_OBJECT_CLASS(g_scan_reverse_modifier_parent_class)->dispose(G_OBJECT(modifier));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : modifier = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_reverse_modifier_finalize(GScanReverseModifier *modifier)
{
    G_OBJECT_CLASS(g_scan_reverse_modifier_parent_class)->finalize(G_OBJECT(modifier));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Construit un modificateur livrant des octets inversés.       *
*                                                                             *
*  Retour      : Mécanisme mis en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanTokenModifier *g_scan_reverse_modifier_new(void)
{
    GScanTokenModifier *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_REVERSE_MODIFIER, NULL);

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

static char *g_scan_reverse_modifier_get_name(const GScanReverseModifier *modifier)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("rev");

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

static bool g_scan_reverse_modifier_transform(const GScanReverseModifier *modifier, const sized_binary_t *src, sized_binary_t **dest, size_t *count)
{
    bool result;                            /* Bilan d'opération à renvoyer*/
    sized_binary_t *binary;                 /* Raccourci vers le stockage  */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    *dest = malloc(1 * sizeof(sized_binary_t));
    *count = 1;

    binary = &(*dest)[0];

    binary->len = src->len;
    binary->data = malloc(binary->len);

    for (i = 0; i < src->len; i++)
        binary->data[src->len - i - 1] = src->data[i];

    return result;

}
