
/* Chrysalide - Outil d'analyse de fichiers binaires
 * type.c - reconnaissance du type d'un contenu
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


#include "type.h"


#include "cookie.h"
#include "../../item-int.h"
#include "../../exprs/literal.h"



/* ---------------------- INTRODUCTION D'UNE NOUVELLE FONCTION ---------------------- */


/* Initialise la classe des reconnaissances de contenus. */
static void g_scan_magic_type_function_class_init(GScanMagicTypeFunctionClass *);

/* Initialise une instance de reconnaissance de contenus. */
static void g_scan_magic_type_function_init(GScanMagicTypeFunction *);

/* Supprime toutes les références externes. */
static void g_scan_magic_type_function_dispose(GScanMagicTypeFunction *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_magic_type_function_finalize(GScanMagicTypeFunction *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Indique le nom associé à une expression d'évaluation. */
static char *g_scan_magic_type_function_get_name(const GScanMagicTypeFunction *);

/* Réduit une expression à une forme plus simple. */
static bool g_scan_magic_type_function_run_call(GScanMagicTypeFunction *, GScanExpression **, size_t, GScanContext *, GScanScope *, GObject **);



/* ---------------------------------------------------------------------------------- */
/*                        INTRODUCTION D'UNE NOUVELLE FONCTION                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une reconnaissance de types de contenus. */
G_DEFINE_TYPE(GScanMagicTypeFunction, g_scan_magic_type_function, G_TYPE_REGISTERED_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des reconnaissances de contenus.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_magic_type_function_class_init(GScanMagicTypeFunctionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GRegisteredItemClass *registered;       /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_magic_type_function_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_magic_type_function_finalize;

    registered = G_REGISTERED_ITEM_CLASS(klass);

    registered->get_name = (get_registered_item_name_fc)g_scan_magic_type_function_get_name;
    registered->run_call = (run_registered_item_call_fc)g_scan_magic_type_function_run_call;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de reconnaissance de contenus.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_magic_type_function_init(GScanMagicTypeFunction *func)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_magic_type_function_dispose(GScanMagicTypeFunction *func)
{
    G_OBJECT_CLASS(g_scan_magic_type_function_parent_class)->dispose(G_OBJECT(func));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : func = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_magic_type_function_finalize(GScanMagicTypeFunction *func)
{
    G_OBJECT_CLASS(g_scan_magic_type_function_parent_class)->finalize(G_OBJECT(func));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Constitue une fonction d'identification de types de contenus.*
*                                                                             *
*  Retour      : Fonction mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRegisteredItem *g_scan_magic_type_function_new(void)
{
    GRegisteredItem *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_MAGIC_TYPE_FUNCTION, NULL);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : item = élément d'appel à consulter.                          *
*                                                                             *
*  Description : Indique le nom associé à une expression d'évaluation.        *
*                                                                             *
*  Retour      : Désignation humaine de l'expression d'évaluation.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_scan_magic_type_function_get_name(const GScanMagicTypeFunction *item)
{
    char *result;                           /* Désignation à retourner     */

    result = strdup("type");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item  = élément d'appel à consulter.                         *
*                args  = liste d'éventuels arguments fournis.                 *
*                count = taille de cette liste.                               *
*                ctx   = contexte de suivi de l'analyse courante.             *
*                scope = portée courante des variables locales.               *
*                out   = zone d'enregistrement de la résolution opérée. [OUT] *
*                                                                             *
*  Description : Réduit une expression à une forme plus simple.               *
*                                                                             *
*  Retour      : Réduction correspondante, expression déjà réduite, ou NULL.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_scan_magic_type_function_run_call(GScanMagicTypeFunction *item, GScanExpression **args, size_t count, GScanContext *ctx, GScanScope *scope, GObject **out)
{
    bool result;                            /* Bilan à retourner           */
    magic_t cookie;                         /* Référence des bibliothèques */
    GBinContent *content;                   /* Contenu à manipuler         */
    vmpa2t pos;                             /* Tête de lecture             */
    phys_t size;                            /* Quantité de données dispos. */
    const bin_t *data;                      /* Accès à des données         */
    const char *desc;                       /* Description du contenu      */
    sized_string_t string;                  /* Description à diffuser      */

    result = (count == 0);
    if (!result) goto exit;

    cookie = get_magic_cookie(MAGIC_NONE);

    content = g_scan_context_get_content(ctx);

    g_binary_content_compute_start_pos(content, &pos);

    size = g_binary_content_compute_size(content);

    data = g_binary_content_get_raw_access(content, &pos, size);

    desc = magic_buffer(cookie, data, size);

    if (desc != NULL)
    {
        string.data = (char *)desc;
        string.len = strlen(desc);
    }
    else
    {
        string.data = "";
        string.len = 0;
    }

    *out = G_OBJECT(g_scan_literal_expression_new(LVT_STRING, &string));

    g_object_unref(G_OBJECT(content));

 exit:

    return result;

}
