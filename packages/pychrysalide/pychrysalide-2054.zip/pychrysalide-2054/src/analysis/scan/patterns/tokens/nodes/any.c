
/* Chrysalide - Outil d'analyse de fichiers binaires
 * any.c - suite d'octets quelconques
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


#include "any.h"


#include <assert.h>


#include "any-int.h"



/* ------------------------ DECOMPOSITION DE MOTIF RECHERCHE ------------------------ */


/* Initialise la classe des séries d'octets quelconques. */
static void g_scan_token_node_any_class_init(GScanTokenNodeAnyClass *);

/* Initialise une instance de série d'octets quelconques. */
static void g_scan_token_node_any_init(GScanTokenNodeAny *);

/* Supprime toutes les références externes. */
static void g_scan_token_node_any_dispose(GScanTokenNodeAny *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_token_node_any_finalize(GScanTokenNodeAny *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Inscrit la définition d'un motif dans un moteur de recherche. */
static bool g_scan_token_node_any_enroll(GScanTokenNodeAny *, GScanContext *, GEngineBackend *, size_t, size_t *);

/* Transforme les correspondances locales en trouvailles. */
static void g_scan_token_node_any_check_forward(const GScanTokenNodeAny *, GScanContext *, GBinContent *, pending_matches_t *, node_search_offset_t *, bool, bool *);

/* Transforme les correspondances locales en trouvailles. */
static void g_scan_token_node_any_check_backward(const GScanTokenNodeAny *, GScanContext *, GBinContent *, pending_matches_t *, node_search_offset_t *, bool, bool *);



/* ---------------------------------------------------------------------------------- */
/*                          DECOMPOSITION DE MOTIF RECHERCHE                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une série d'octets quelconque, vide ou non. */
G_DEFINE_TYPE(GScanTokenNodeAny, g_scan_token_node_any, G_TYPE_SCAN_TOKEN_NODE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des séries d'octets quelconques.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_any_class_init(GScanTokenNodeAnyClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanTokenNodeClass *node;              /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_token_node_any_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_token_node_any_finalize;

    node = G_SCAN_TOKEN_NODE_CLASS(klass);

    node->visit = (visit_scan_token_node_fc)NULL;
    node->enroll = (enroll_scan_token_node_fc)g_scan_token_node_any_enroll;
    node->check_forward = (check_scan_token_node_fc)g_scan_token_node_any_check_forward;
    node->check_backward = (check_scan_token_node_fc)g_scan_token_node_any_check_backward;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : any = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de série d'octets quelconques.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_any_init(GScanTokenNodeAny *any)
{
    g_scan_token_node_set_flags(G_SCAN_TOKEN_NODE(any), STNF_PROD);

    any->min = 0;
    any->has_max = false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : any = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_any_dispose(GScanTokenNodeAny *any)
{
    G_OBJECT_CLASS(g_scan_token_node_any_parent_class)->dispose(G_OBJECT(any));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : any = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_any_finalize(GScanTokenNodeAny *any)
{
    G_OBJECT_CLASS(g_scan_token_node_any_parent_class)->finalize(G_OBJECT(any));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : min = éventuelle quantité minimale à retrouver.              *
*                max = éventuelle quantité maximale à retrouver.              *
*                                                                             *
*  Description : Construit un noeud pointant une série d'octets quelconques.  *
*                                                                             *
*  Retour      : Mécanismes mis en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanTokenNode *g_scan_token_node_any_new(const phys_t *min, const phys_t *max)
{
    GScanTokenNode *result;                 /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_TOKEN_NODE_ANY, NULL);

    if (!g_scan_token_node_any_create(G_SCAN_TOKEN_NODE_ANY(result), min, max))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : any = séquence d'octets quelconques à initialiser pleinement.*
*                min = éventuelle quantité minimale à retrouver.              *
*                max = éventuelle quantité maximale à retrouver.              *
*                                                                             *
*  Description : Met en place un un noeud pointant une série d'octets.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_token_node_any_create(GScanTokenNodeAny *any, const phys_t *min, const phys_t *max)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (min != NULL)
        any->min = *min;
    else
        any->min = 0;

    if (max != NULL)
    {
        any->max = *max;

        result = (any->min <= any->max);

    }

    any->has_max = (max != NULL);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : node    = définition de la bribe à enregistrer.              *
*                context = contexte de l'analyse à mener.                     *
*                backend = moteur de recherche à préchauffer.                 *
*                maxsize = taille max. des atomes (mise en commun optimisée). *
*                slow    = niveau de ralentissement induit (0 = idéal). [OUT] *
*                                                                             *
*  Description : Inscrit la définition d'un motif dans un moteur de recherche.*
*                                                                             *
*  Retour      : Bilan de l'opération à renvoyer.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_scan_token_node_any_enroll(GScanTokenNodeAny *node, GScanContext *context, GEngineBackend *backend, size_t maxsize, size_t *slow)
{
    bool result;                            /* Statut à retourner          */
    bool forced;                            /* Inclusion dans un scan ?    */

    result = true;

    forced = (g_scan_token_node_get_flags(G_SCAN_TOKEN_NODE(node)) & STNF_MAIN);

    if (forced)
        *slow += (maxsize * 4);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node    = définition de la bribe à manipuler.                *
*                context = contexte de l'analyse à mener.                     *
*                content = accès au contenu brut pour vérifications (optim.)  *
*                matches = suivi des correspondances à consolider.            *
*                offset  = tolérance dans les positions à appliquer.          *
*                not     = indique si les résultats doivent être inversés.    *
*                skip    = détermine si l'analyse est différée. [OUT]         *
*                                                                             *
*  Description : Transforme les correspondances locales en trouvailles.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_any_check_forward(const GScanTokenNodeAny *node, GScanContext *context, GBinContent *content, pending_matches_t *matches, node_search_offset_t *offset, bool not, bool *skip)
{
    bool initialized;                       /* Initialisation du suivi ?   */
    bool forced;                            /* Inclusion dans un scan ?    */
    phys_t size;                            /* Quantité d'octets considérés*/
    const phys_t *datasize;                 /* Taille max. à communiquer   */

    if (*skip)
        return;


    //         $a = { [1-3] 6f }
    // pas d'initialisation, construction de résultats avec une taille nulle



    initialized = are_pending_matches_initialized(matches);

    forced = (g_scan_token_node_get_flags(G_SCAN_TOKEN_NODE(node)) & STNF_MAIN);

    size = matches->content_end - matches->content_start;

    datasize = (not ? &size : NULL);

    if (forced)
    {
        assert(!initialized);

        if (node->min > size)
            /* TODO set abort in matches */;

        else
            add_range_to_node_search_offset(offset,
                                            matches->content_start,
                                            matches->content_end - matches->content_start,
                                            datasize);

    }
    else
    {
        assert(initialized);


        // TODO : compléter les intervales éventuels déjà en place


        /*
        printf("[i] create hole: %llx <-> %llx\n",
               (unsigned long long)node->min,
               (unsigned long long)node->max);
        */


        if (node->has_max)
            add_range_to_node_search_offset(offset, node->min, node->max, datasize);
        else
            add_range_to_node_search_offset(offset, node->min, matches->content_end - node->min, datasize);

        // TODO : si dernier, virer les correspondances qui n'ont plus l'espace de fin requis
        // -> au niveau du noeud, en fonction du flag _LAST

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node    = définition de la bribe à manipuler.                *
*                context = contexte de l'analyse à mener.                     *
*                content = accès au contenu brut pour vérifications (optim.)  *
*                matches = suivi des correspondances à consolider.            *
*                offset  = tolérance dans les positions à appliquer.          *
*                not     = indique si les résultats doivent être inversés.    *
*                skip    = détermine si l'analyse est différée. [OUT]         *
*                                                                             *
*  Description : Transforme les correspondances locales en trouvailles.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_any_check_backward(const GScanTokenNodeAny *node, GScanContext *context, GBinContent *content, pending_matches_t *matches, node_search_offset_t *offset, bool not, bool *skip)
{
#ifndef NDEBUG
    bool forced;                            /* Inclusion dans un scan ?    */
#endif
    phys_t size;                            /* Quantité d'octets considérés*/
    const phys_t *datasize;                 /* Taille max. à communiquer   */

    if (*skip)
        return;

    /**
     * En lecture à rebourd, au moins un noeud a été solicité pour analyse (lors
     * du sens de lecteur normal). Donc l'initialisation a déjà dû avoir lieu.
     */
    assert(are_pending_matches_initialized(matches));

    /**
     * Si les recherches associées au noeud ont été forcées, alors les traitements
     * liés ont déjà été effectués, et l'appel de cette fonction aurait dû être sauté.
     */
#ifndef NDEBUG
    forced = (g_scan_token_node_get_flags(G_SCAN_TOKEN_NODE(node)) & STNF_MAIN);
    assert(!forced);
#endif

    size = matches->content_end - matches->content_start;

    if (node->min > size)
        /* TODO set abort in matches */;

    else
    {
        datasize = (not ? &size : NULL);

        /**
         * Une tolérance basée sur des espaces (et non des positions) est déterminée
         * ici.
         *
         * Charge au prochain noeud de traitement de filtrer les résultats courants
         * avec, voire à la fonction _g_scan_token_node_check_backward() de
         * réaliser une synthèse finale si le noeud courant est le dernier d'une
         * lignée.
         */

        if (node->has_max)
            add_range_to_node_search_offset(offset, node->min, node->max, datasize);
        else
            add_range_to_node_search_offset(offset, node->min, matches->content_end - node->min, datasize);

    }

}
