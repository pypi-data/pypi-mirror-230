
/* Chrysalide - Outil d'analyse de fichiers binaires
 * modifier.c - modification d'une séquence d'octets pour un motif recherché
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


#include "modifier.h"


#include "modifier-int.h"



/* Initialise la classe des transformations d'octets. */
static void g_scan_token_modifier_class_init(GScanTokenModifierClass *);

/* Initialise une instance de transformation d'octets. */
static void g_scan_token_modifier_init(GScanTokenModifier *);

/* Supprime toutes les références externes. */
static void g_scan_token_modifier_dispose(GScanTokenModifier *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_token_modifier_finalize(GScanTokenModifier *);



/* Indique le type défini pour une transformation d'une séquence d'octets. */
G_DEFINE_TYPE(GScanTokenModifier, g_scan_token_modifier, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des transformations d'octets.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_modifier_class_init(GScanTokenModifierClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_token_modifier_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_token_modifier_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : modifier = instance à initialiser.                           *
*                                                                             *
*  Description : Initialise une instance de transformation d'octets.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_modifier_init(GScanTokenModifier *modifier)
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

static void g_scan_token_modifier_dispose(GScanTokenModifier *modifier)
{
    G_OBJECT_CLASS(g_scan_token_modifier_parent_class)->dispose(G_OBJECT(modifier));

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

static void g_scan_token_modifier_finalize(GScanTokenModifier *modifier)
{
    G_OBJECT_CLASS(g_scan_token_modifier_parent_class)->finalize(G_OBJECT(modifier));

}


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

char *g_scan_token_modifier_get_name(const GScanTokenModifier *modifier)
{
    char *result;                           /* Désignation à retourner     */
    GScanTokenModifierClass *class;         /* Classe à activer            */

    class = G_SCAN_TOKEN_MODIFIER_GET_CLASS(modifier);

    result = class->get_name(modifier);

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

bool g_scan_token_modifier_transform(const GScanTokenModifier *modifier, const sized_binary_t *src, sized_binary_t **dest, size_t *count)
{
    bool result;                            /* Bilan d'opération à renvoyer*/
    GScanTokenModifierClass *class;         /* Classe à activer            */

    class = G_SCAN_TOKEN_MODIFIER_GET_CLASS(modifier);

    result = class->transform(modifier, src, dest, count);

    return result;

}
