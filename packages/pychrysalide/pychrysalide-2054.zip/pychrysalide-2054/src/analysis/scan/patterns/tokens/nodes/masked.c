
/* Chrysalide - Outil d'analyse de fichiers binaires
 * masked.c - gestion d'une recherche de motif partielle
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


#include "masked.h"


#include <assert.h>


#include "masked-int.h"
#include "../../backends/bitap.h"



/* ------------------------ DECOMPOSITION DE MOTIF RECHERCHE ------------------------ */


/* Initialise la classe des bribes de motif partielles. */
static void g_scan_token_node_masked_class_init(GScanTokenNodeMaskedClass *);

/* Initialise une instance de bribe de motif partielle. */
static void g_scan_token_node_masked_init(GScanTokenNodeMasked *);

/* Supprime toutes les références externes. */
static void g_scan_token_node_masked_dispose(GScanTokenNodeMasked *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_token_node_masked_finalize(GScanTokenNodeMasked *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Parcourt une arborescence de noeuds et y relève des éléments. */
static void g_scan_token_node_masked_visit(GScanTokenNodeMasked *, scan_tree_points_t *);

/* Inscrit la définition d'un motif dans un moteur de recherche. */
static bool g_scan_token_node_masked_enroll(GScanTokenNodeMasked *, GScanContext *, GEngineBackend *, size_t, size_t *);

/* Détermine si un contenu d'intérêt est présent à une position. */
static bool check_scan_token_node_masked_content(const masked_byte_t *, size_t, phys_t, GBinContent *);

/* Transforme les correspondances locales en trouvailles. */
static void g_scan_token_node_masked_check_forward(const GScanTokenNodeMasked *, GScanContext *, GBinContent *, pending_matches_t *, node_search_offset_t *, bool, bool *);

/* Transforme les correspondances locales en trouvailles. */
static void g_scan_token_node_masked_check_backward(const GScanTokenNodeMasked *, GScanContext *, GBinContent *, pending_matches_t *, node_search_offset_t *, bool, bool *);



/* ---------------------------------------------------------------------------------- */
/*                          DECOMPOSITION DE MOTIF RECHERCHE                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un noeud représentant une bribe partielle à retrouver. */
G_DEFINE_TYPE(GScanTokenNodeMasked, g_scan_token_node_masked, G_TYPE_SCAN_TOKEN_NODE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des bribes de motif partielles.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_masked_class_init(GScanTokenNodeMaskedClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanTokenNodeClass *node;              /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_token_node_masked_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_token_node_masked_finalize;

    node = G_SCAN_TOKEN_NODE_CLASS(klass);

    node->visit = (visit_scan_token_node_fc)g_scan_token_node_masked_visit;
    node->enroll = (enroll_scan_token_node_fc)g_scan_token_node_masked_enroll;
    node->check_forward = (check_scan_token_node_fc)g_scan_token_node_masked_check_forward;
    node->check_backward = (check_scan_token_node_fc)g_scan_token_node_masked_check_backward;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : masked = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de bribe de motif partielle.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_masked_init(GScanTokenNodeMasked *masked)
{
    g_scan_token_node_set_flags(G_SCAN_TOKEN_NODE(masked), STNF_PROD);

    masked->bytes = NULL;
    masked->len = 0;

    masked->raw = NULL;
    masked->atoms = NULL;
    masked->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : masked = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_masked_dispose(GScanTokenNodeMasked *masked)
{
    G_OBJECT_CLASS(g_scan_token_node_masked_parent_class)->dispose(G_OBJECT(masked));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : masked = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_masked_finalize(GScanTokenNodeMasked *masked)
{
    size_t i;                               /* Boucle de parcours          */

    if (masked->bytes != NULL)
        free(masked->bytes);

    for (i = 0; i < masked->count; i++)
        exit_szstr(&masked->raw[i]);

    if (masked->raw != NULL)
        free(masked->raw);

    if (masked->atoms != NULL)
        free(masked->atoms);

    G_OBJECT_CLASS(g_scan_token_node_masked_parent_class)->finalize(G_OBJECT(masked));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : byte = valeur masquée à intégrer.                            *
*                                                                             *
*  Description : Construit une bribe de motif partielle.                      *
*                                                                             *
*  Retour      : Mécanismes mis en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanTokenNode *g_scan_token_node_masked_new(const masked_byte_t *byte)
{
    GScanTokenNode *result;                 /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_TOKEN_NODE_MASKED, NULL);

    if (!g_scan_token_node_masked_create(G_SCAN_TOKEN_NODE_MASKED(result), byte))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : masked = bribe partielle à initialiser pleinement.           *
*                byte   = valeur masquée à intégrer.                          *
*                                                                             *
*  Description : Met en place une bribe de motif partielle.                   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_token_node_masked_create(GScanTokenNodeMasked *masked, const masked_byte_t *byte)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    g_scan_token_node_masked_add(masked, byte);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : masked = ensemble de noeuds à compléter.                     *
*                byte = valeur masquée à intégrer.                            *
*                                                                             *
*  Description : Enregistre la valeur d'octet à rechercher avec son masque.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_token_node_masked_add(GScanTokenNodeMasked *masked, const masked_byte_t *byte)
{
    assert((byte->value & 0x0f) == 0 || (byte->value & 0xf0) == 0);

    masked->bytes = realloc(masked->bytes, ++masked->len * sizeof(masked_byte_t));

    masked->bytes[masked->len - 1] = *byte;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : node   = point de départ du parcours à effectuer.            *
*                points = points capitaux de l'arborescence. [OUT]            *
*                                                                             *
*  Description : Parcourt une arborescence de noeuds et y relève des éléments.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_masked_visit(GScanTokenNodeMasked *node, scan_tree_points_t *points)
{
    GScanTokenNodeMasked *other;            /* Concurrence à mesurer       */

    if (points->best_masked == NULL)
        points->best_masked = G_SCAN_TOKEN_NODE(node);

    else
    {
        other = G_SCAN_TOKEN_NODE_MASKED(points->best_masked);

        if (node->len > other->len)
            points->best_masked = G_SCAN_TOKEN_NODE(node);

    }

}


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

static bool g_scan_token_node_masked_enroll(GScanTokenNodeMasked *node, GScanContext *context, GEngineBackend *backend, size_t maxsize, size_t *slow)
{
    bool result;                            /* Statut à retourner          */
    bool forced;                            /* Inclusion dans un scan ?    */
    //size_t len_to_enroll;                   /* Taille à considérer         */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    forced = (g_scan_token_node_get_flags(G_SCAN_TOKEN_NODE(node)) & STNF_MAIN);

    if (forced)
    {
        *slow += (maxsize * 2);

        /**
         * Dans le cas bien précis de l'usage de l'algorithme Bitap pour les recherches
         * dans le contenu binaire à analyser, on tire parti du coût nul des recherches
         * multiples pour une même position.
         */

        if (G_IS_BITAP_BACKEND(backend))
        {
            //len_to_enroll = (node->len < maxsize ? node->len : maxsize);

            /* TODO */
            assert(false);


            node->enrolled_count = 1;

        }

        else
        {
            node->raw = make_atoms_from_masked_byte(node->bytes[0].value, node->bytes[0].mask, &node->count);

            node->atoms = malloc(node->count * sizeof(tracked_scan_atom_t));

            for (i = 0; i < node->count && result; i++)
            {
                find_best_atom(&node->raw[i], maxsize, &node->atoms[i], NULL);

                result = enroll_prepared_atom(&node->raw[i], context, backend, &node->atoms[i]);

            }

            node->enrolled_count = node->count;

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bytes   = octets partiels avec leur masque à interpréter.    *
*                len     = quantité d'octets à interpréter.                   *
*                start   = point d'analyse à respecter.                       *
*                content = accès au contenu brut pour vérifications (optim.)  *
*                                                                             *
*  Description : Détermine si un contenu d'intérêt est présent à une position.*
*                                                                             *
*  Retour      : Bilan de l'analyse : true pour une correspondance.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool check_scan_token_node_masked_content(const masked_byte_t *bytes, size_t len, phys_t start, GBinContent *content)
{
    bool result;                            /* Bilan à retourner           */
    vmpa2t pos;                             /* Position dans les données   */
    const bin_t *ptr;                       /* Accès aux données brutes    */
    size_t i;                               /* Boucle de parcours          */

    result = false;

    init_vmpa(&pos, start, VMPA_NO_VIRTUAL);

    ptr = g_binary_content_get_raw_access(content, &pos, len);

    for (i = 0; i < len; i++)
    {
        if ((ptr[i] & bytes[i].mask) != bytes[i].value)
            break;
    }

    result = (i == len);

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

static void g_scan_token_node_masked_check_forward(const GScanTokenNodeMasked *node, GScanContext *context, GBinContent *content, pending_matches_t *matches, node_search_offset_t *offset, bool not, bool *skip)
{
    bool initialized;                       /* Initialisation du suivi ?   */
#ifndef NDEBUG
    bool forced;                            /* Inclusion dans un scan ?    */
#endif
    size_t ocount;                          /* Quantité de bornes présentes*/
    node_offset_range_t * const *ranges_ptr;/* Bornes d'espace à parcourir */
    size_t i;                               /* Boucle de parcours #1       */
    const tracked_scan_atom_t *atom;        /* Atome correspondant         */
    size_t count;                           /* Quantité de bribes trouvées */
    const phys_t *found;                    /* Localisations des bribes    */
    size_t k;                               /* Boucle de parcours #2       */
    phys_t new_begin;                       /* Nouveau départ à tester     */
    size_t o;                               /* Boucle de parcours #3       */
    const node_offset_range_t *range;       /* Bornes d'espace à parcourir */
    bool status;                            /* Bilan d'une correspondance  */
    size_t pcount;                          /* Nombre de correspondances   */
    match_area_t * const *pending_ptr;      /* Correspondances actuelles   */
    size_t p;                               /* Boucle de parcours #4       */
    match_area_t *pending;                  /* Correspondance à traiter    */
    phys_t after;                           /* Espace disposible après     */
    phys_t min;                             /* Borne minimale déterminée   */
    phys_t max;                             /* Borne maximale déterminée   */
    phys_t j;                               /* Boucle de parcours #5       */

    if (*skip)
        return;

    initialized = are_pending_matches_initialized(matches);

    /**
     * Si l'analyse arrive à un ou plusieurs octets masqués, soit il s'agit du
     * premier noeud, et la génération d'atomes a été forcée pour obtenir des
     * points de départ, soit des correspondances ont été établies au préalable,
     * et il ne doit alors pas y avoir d'atome mis en place (si l'initialisation
     * ne provient pas d'une mise en place artificielle par une inversion NOT).
     */
#ifndef NDEBUG
    forced = (g_scan_token_node_get_flags(G_SCAN_TOKEN_NODE(node)) & STNF_MAIN);
    assert((!initialized && forced) || (initialized && (!forced || not)));
#endif

    ranges_ptr = get_node_search_offset_ranges(offset, &ocount);

    /* Si aucune correspondance n'a été établie */
    if (!initialized)
    {
        for (i = 0; i < node->enrolled_count; i++)
        {
            atom = &node->atoms[i];

            found = g_scan_context_get_atom_matches(context, atom->pid, &count);

            for (k = 0; k < count; k++)
            {
                assert(atom->pos == 0);

                new_begin = found[k];

                /**
                 * Si des bornes sont spécifiées, la position de l'atome est testée.
                 *
                 * Dans la pratique, cette situation (non initialisée) ne peut provenir
                 * que d'un espace situé dans le vide, donc couvrant un large périmètre.
                 * La validation a ainsi de grandes chances de passer...
                 *
                 * Le motif pouvant amener à cette situation (pas d'initialisation,
                 * mais à décalage à considérer) est par exemple :
                 *
                 *    ~( ?? ?1 )
                 *
                 */
                if (ocount > 0)
                {
                    if (!does_node_search_offset_include_pos_forward(offset, 0, new_begin))
                        continue;
                }

                /**
                 * Existe-t-il assez de place pour faire tenir le motif masqué ?
                 */
                if ((new_begin + node->len) > matches->content_end)
                    continue;

                status = check_scan_token_node_masked_content(node->bytes, node->len, new_begin, content);

                if ((status && !not) || (!status && not))
                {
                    /**
                     * Il ne peut y avoir qu'une seule séquence d'octets à un même
                     * emplacement, donc le couple (start, len) enregistré est
                     * unique.
                     */
                    add_pending_match(matches, new_begin, node->len);

                }

            }

        }

    }

    /* Si les correspondances en place sont à confirmer et compléter */
    else
    {
        reset_pending_matches_ttl(matches);

        pending_ptr = get_all_pending_matches(matches, &pcount);

        for (p = 0; p < pcount; p++)
        {
            pending = (*pending_ptr) + p;

            assert(pending->end <= matches->content_end);

            after = matches->content_end - pending->end;

            new_begin = pending->end;

            if (ocount > 0)
            {
                for (o = 0; o < ocount; o++)
                {
                    range = (*ranges_ptr) + o;

                    /**
                     * Si bornes de tolérance il y a, l'espace restant est validé en
                     * tenant compte de ces bornes.
                     */
                    if (!get_node_offset_range(range, node->len, after, &min, &max))
                        continue;

                    /**
                     * Une recherche des différentes correspondances amont est lancée.
                     */
                    for (j = min; j <= max; j++)
                    {
                        status = check_scan_token_node_masked_content(node->bytes, node->len,
                                                                      new_begin + j, content);

                        if ((status && !not) || (!status && not))
                        {
                            /**
                             * S'il s'avère qu'il existe de multiples correspondances dans l'espace
                             * analysé, c'est la fonction extend_pending_match_ending() qui
                             * duplique cette correspondance, en s'appuyant sur le TTL pour
                             * repérer ce cas de figure.
                             *
                             * Par exemple, deux correspondances '?1 ?1 [1-3] ?2 ?2'
                             * sont valides pour un même contenu :
                             *
                             *    aa.bbb -> correspondance 'aa.bb'
                             *      ^
                             *
                             *    aa.bbb -> correspondance 'aa..bb'
                             *      ^
                             */
                            extend_pending_match_ending(matches, p, new_begin + j + node->len);

                            /**
                             * Comme l'extension a pu conduire à un ajout et donc à une
                             * réallocation de la liste, on recharge l'élément pour les
                             * itérations suivantes.
                             */
                            pending = (*pending_ptr) + p;

                        }

                    }

                }

            }

            else
            {
                /**
                 * Si la fin d'une correspondance potentielle est trop près de
                 * la fin du contenu binaire et ne peut contenir le motif
                 * représenté, alors la corresponance est écartée.
                 */
                if (node->len > after)
                    continue;

                new_begin = pending->end;

                status = check_scan_token_node_masked_content(node->bytes, node->len, new_begin, content);

                if ((status && !not) || (!status && not))
                {
                    extend_pending_match_ending(matches, p, new_begin + node->len);

                    /**
                     * Comme il n'y a qu'une seule itération par correspondance,
                     * nul besoin de recharcher l'élément.
                     */

                }

            }

        }

        purge_pending_matches(matches);

    }

    set_pending_matches_initialized(matches);

    disable_all_ranges_in_node_search_offset(offset);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node    = définition de la bribe à manipuler.                *
*                context = contexte de l'analyse à mener.                     *
*                content = accès au contenu brut pour vérifications (optim.)  *
*                matches = suivi des correspondances à consolider.            *
*                offsets = tolérance dans les positions à appliquer.          *
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

static void g_scan_token_node_masked_check_backward(const GScanTokenNodeMasked *node, GScanContext *context, GBinContent *content, pending_matches_t *matches, node_search_offset_t *offset, bool not, bool *skip)
{
#ifndef NDEBUG
    bool forced;                            /* Inclusion dans un scan ?    */
#endif
    size_t pcount;                          /* Nombre de correspondances   */
    match_area_t * const *pending_ptr;      /* Correspondances actuelles   */
    size_t ocount;                          /* Quantité de bornes présentes*/
    node_offset_range_t * const *ranges_ptr;/* Bornes d'espace à parcourir */
    size_t p;                               /* Boucle de parcours #1       */
    const match_area_t *pending;            /* Correspondance à traiter    */
    phys_t before;                          /* Espace disposible avant     */
    phys_t new_begin;                       /* Nouveau départ à tester     */
    size_t o;                               /* Boucle de parcours #2       */
    const node_offset_range_t *range;       /* Bornes d'espace à parcourir */
    phys_t min;                             /* Borne minimale déterminée   */
    phys_t max;                             /* Borne maximale déterminée   */
    phys_t j;                               /* Boucle de parcours #3       */
    bool status;                            /* Bilan d'une correspondance  */

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

    reset_pending_matches_ttl(matches);

    pending_ptr = get_all_pending_matches(matches, &pcount);

    ranges_ptr = get_node_search_offset_ranges(offset, &ocount);

    for (p = 0; p < pcount; p++)
    {
        pending = (*pending_ptr) + p;

        assert(matches->content_start <= pending->start);

        before = pending->start - matches->content_start;

        new_begin = pending->start - node->len;

        if (ocount > 0)
        {
            for (o = 0; o < ocount; o++)
            {
                range = (*ranges_ptr) + o;

                /**
                 * Si bornes de tolérance il y a, l'espace restant est validé en
                 * tenant compte de ces bornes.
                 */
                if (!get_node_offset_range(range, node->len, before, &min, &max))
                {
                    if (not)
                        extend_pending_match_beginning(matches, p, pending->start - node->len);

                    continue;

                }

                /**
                 * Une recherche des différentes correspondances amont est lancée.
                 */
                for (j = min; j <= max; j++)
                {
                    status = check_scan_token_node_masked_content(node->bytes, node->len,
                                                                  new_begin - j, content);

                    if ((status && !not) || (!status && not))
                    {
                        /**
                         * S'il s'avère qu'il existe de multiples correspondances dans l'espace
                         * analysé, c'est la fonction extend_pending_match_beginning() qui
                         * duplique cette correspondance, en s'appuyant sur le TTL pour
                         * repérer ce cas de figure.
                         */
                        extend_pending_match_beginning(matches, p, new_begin);

                        /**
                         * Comme l'extension a pu conduire à un ajout et donc à une
                         * réallocation de la liste, on recharge l'élément pour les
                         * itérations suivantes.
                         */
                        pending = (*pending_ptr) + p;

                    }

                }

            }

        }

        else
        {
            /**
             * Si le début d'une correspondance potentielle est trop près du début
             * du contenu binaire et ne peut contenir le motif représenté, alors
             * la corresponance est écartée.
             */
            if (node->len > before)
            {
                if (not)
                    extend_pending_match_beginning(matches, p, new_begin);

                continue;

            }

            status = check_scan_token_node_masked_content(node->bytes, node->len, new_begin, content);

            if ((status && !not) || (!status && not))
                extend_pending_match_beginning(matches, p, new_begin);

        }

    }

    purge_pending_matches(matches);

    disable_all_ranges_in_node_search_offset(offset);

}
