
/* Chrysalide - Outil d'analyse de fichiers binaires
 * token.c - bribes de recherche textuelle
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


#include "token.h"


#include <assert.h>
#include <ctype.h>
#include <stdio.h>


#include "token-int.h"
#include "../../../common/cpp.h"
#include "../../../core/logs.h"



/* ------------------------- CIBLAGE DES SEQUENCES D'OCTETS ------------------------- */


/* Initialise la classe des bribes de recherche textuelle. */
static void g_string_token_class_init(GStringTokenClass *);

/* Initialise une instance de bribe de recherche textuelle. */
static void g_string_token_init(GStringToken *);

/* Supprime toutes les références externes. */
static void g_string_token_dispose(GStringToken *);

/* Procède à la libération totale de la mémoire. */
static void g_string_token_finalize(GStringToken *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Affiche un motif de recherche au format texte. */
static void g_string_token_output_to_text(const GStringToken *, GScanContext *, int);

/* Affiche un motif de recherche au format JSON. */
static void g_string_token_output_to_json(const GStringToken *, GScanContext *, const sized_string_t *, unsigned int, int);



/* ---------------------------------------------------------------------------------- */
/*                           CIBLAGE DES SEQUENCES D'OCTETS                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une bribe de recherche textuelle. */
G_DEFINE_TYPE(GStringToken, g_string_token, G_TYPE_SEARCH_PATTERN);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des bribes de recherche textuelle.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_string_token_class_init(GStringTokenClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GSearchPatternClass *pattern;           /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_string_token_dispose;
    object->finalize = (GObjectFinalizeFunc)g_string_token_finalize;

    pattern = G_SEARCH_PATTERN_CLASS(klass);

    pattern->to_text = (output_pattern_to_text_fc)g_string_token_output_to_text;
    pattern->to_json = (output_pattern_to_json_fc)g_string_token_output_to_json;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : token = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de bribe de recherche textuelle.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_string_token_init(GStringToken *token)
{
    token->root = NULL;
    token->slow = 0;
    token->need_backward = false;

    token->fullword = false;
    token->private = false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : token = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_string_token_dispose(GStringToken *token)
{
    G_OBJECT_CLASS(g_string_token_parent_class)->dispose(G_OBJECT(token));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : token = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_string_token_finalize(GStringToken *token)
{
    G_OBJECT_CLASS(g_string_token_parent_class)->finalize(G_OBJECT(token));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : token    = encadrement de motif à initialiser pleinement.    *
*                root     = représentation du motif à recherche.              *
*                fullword = limite les correspondances à des mots entiers.    *
*                private  = donne une vocation privée au motif de recherche.  *
*                                                                             *
*  Description : Met en place un gestionnaire de recherche de binaire.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_string_token_create(GStringToken *token, GScanTokenNode *root, bool fullword, bool private)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    token->root = root;
    g_object_ref(G_OBJECT(root));

    token->fullword = fullword;
    token->private = private;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : token = encadrement de motif à consulter.                    *
*                                                                             *
*  Description : Indique si seuls des mots entiers sont retenus des analyses. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_string_token_target_fullword(const GStringToken *token)
{
    bool result;                            /* Statut à renvoyer           */

    result = token->fullword;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : token = encadrement de motif à consulter.                    *
*                                                                             *
*  Description : Détermine si le gestionnaire est à vocation privée.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_string_token_is_private(const GStringToken *token)
{
    bool result;                            /* Statut à renvoyer           */

    result = token->private;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : token   = définition de la bribe à enregistrer.              *
*                context = contexte de l'analyse à mener.                     *
*                backend = moteur de recherche à préchauffer.                 *
*                maxsize = taille max. des atomes (mise en commun optimisée). *
*                                                                             *
*  Description : Inscrit la définition d'un motif dans un moteur de recherche.*
*                                                                             *
*  Retour      : Bilan de l'opération à renvoyer.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_string_token_enroll(GStringToken *token, GScanContext *context, GEngineBackend *backend, size_t maxsize)
{
    bool result;                            /* Statut à retourner          */

    token->need_backward = g_scan_token_node_setup_tree(token->root);

    result = g_scan_token_node_enroll(token->root, context, backend, maxsize, &token->slow);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : token   = définition de la bribe à manipuler.                *
*                context = contexte de l'analyse à mener.                     *
*                content = accès au contenu brut pour vérifications (optim.)  *
*                matches = suivi des correspondances à consolider.            *
*                                                                             *
*  Description : Transforme les correspondances locales en trouvailles.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_string_token_check(const GStringToken *token, GScanContext *context, GBinContent *content, pending_matches_t *matches)
{
    size_t p;                               /* Boucle de parcours #3       */
    match_area_t *pending;                  /* Correspondance à traiter    */
    vmpa2t pos;                             /* Tête de lecture             */
    const bin_t *byte;                      /* Octet à valider             */

    g_scan_token_node_check_forward(token->root, context, content, matches);

    if (token->need_backward)
        g_scan_token_node_check_backward(token->root, context, content, matches);

    sort_and_filter_pending_matches(matches);

    if (token->fullword)
    {
        reset_pending_matches_ttl(matches);

        for (p = 0; p < matches->used; p++)
        {
            pending = &matches->areas[p];

            /* Validation de l'octet précédent, s'il existe */
            if (pending->start > matches->content_start)
            {
                init_vmpa(&pos, pending->start - 1, VMPA_NO_VIRTUAL);

                byte = g_binary_content_get_raw_access(content, &pos, 1);

                if (isalnum(*byte))
                    continue;

            }

            /* Validation de l'octet suivant, s'il existe */
            if (pending->end < matches->content_end)
            {
                init_vmpa(&pos, pending->end, VMPA_NO_VIRTUAL);

                byte = g_binary_content_get_raw_access(content, &pos, 1);

                if (isalnum(*byte))
                    continue;

            }

            keep_pending_match(pending);

        }

        purge_pending_matches(matches);

    }

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = définition de motif à considérer.                  *
*                context = contexte de l'analyse à mener.                     *
*                fd      = canal d'écriture.                                  *
*                                                                             *
*  Description : Affiche un motif de recherche au format texte.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_string_token_output_to_text(const GStringToken *pattern, GScanContext *context, int fd)
{
    const GScanMatch **matches;             /* Correspondances établies    */
    size_t count;                           /* Quantité de cette liste     */
    size_t i;                               /* Boucle de parcours          */

    if (g_string_token_is_private(pattern))
        return;

    matches = g_scan_context_get_full_matches(context, G_SEARCH_PATTERN(pattern), &count);

    for (i = 0; i < count; i++)
        g_scan_match_output_to_text(matches[i], fd);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = définition de motif à considérer.                  *
*                context  = contexte de l'analyse à mener.                    *
*                padding  = éventuel bourrage initial à placer ou NULL.       *
*                level    = profondeur actuelle.                              *
*                fd       = canal d'écriture.                                 *
*                                                                             *
*  Description : Affiche un motif de recherche au format JSON.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_string_token_output_to_json(const GStringToken *pattern, GScanContext *context, const sized_string_t *padding, unsigned int level, int fd)
{
    unsigned int i;                         /* Boucle de parcours #1       */
    const GScanMatch **matches;             /* Correspondances établies    */
    size_t count;                           /* Quantité de cette liste     */
    char value[ULLONG_MAXLEN];              /* Impression de la position   */
    int ret;                                /* Bilan d'une conversion      */
    size_t k;                               /* Boucle de parcours #2       */
    bool trailing;                          /* Virgule finale              */

    if (g_string_token_is_private(pattern))
        return;

    matches = g_scan_context_get_full_matches(context, G_SEARCH_PATTERN(pattern), &count);

    /* Nombre de correspondances */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    write(fd, "\"match_count\": ", 15);

    ret = snprintf(value, ULLONG_MAXLEN, "%zu", count);

    if (ret > 0)
        write(fd, value, ret);

    else
    {
        log_simple_message(LMT_EXT_ERROR, "Error while converting value!");
        write(fd, "null", 4);
    }

    write(fd, ",\n", 2);

    /* Détail des correspondances */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    write(fd, "\"matches\": [\n", 13);

    for (k = 0; k < count; k++)
    {
        trailing = ((k + 1) < count);

        g_scan_match_output_to_json(matches[k], padding, level + 1, fd, trailing);

    }

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    write(fd, "]\n", 2);

}
