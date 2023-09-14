
/* Chrysalide - Outil d'analyse de fichiers binaires
 * plain.c - gestion d'une recherche de motif textuel
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


#include "plain.h"


#include <assert.h>


#include "plain-int.h"
#include "../../../../../common/extstr.h"



/* ------------------------ DECOMPOSITION DE MOTIF RECHERCHE ------------------------ */


/* Initialise la classe des noeuds pour motif textuel. */
static void g_scan_token_node_plain_class_init(GScanTokenNodePlainClass *);

/* Initialise une instance de noeud pour motif textuel. */
static void g_scan_token_node_plain_init(GScanTokenNodePlain *);

/* Supprime toutes les références externes. */
static void g_scan_token_node_plain_dispose(GScanTokenNodePlain *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_token_node_plain_finalize(GScanTokenNodePlain *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Parcourt une arborescence de noeuds et y relève des éléments. */
static void g_scan_token_node_plain_visit(GScanTokenNodePlain *, scan_tree_points_t *);

/* Inscrit la définition d'un motif dans un moteur de recherche. */
static bool g_scan_token_node_plain_enroll(GScanTokenNodePlain *, GScanContext *, GEngineBackend *, size_t, size_t *);

/* Détermine si un contenu d'intérêt est présent à une position. */
static bool check_scan_token_node_plain_content(const sized_binary_t *, const tracked_scan_atom_t *, bool, phys_t, GBinContent *);

/* Transforme les correspondances locales en trouvailles. */
static void g_scan_token_node_plain_check_forward(const GScanTokenNodePlain *, GScanContext *, GBinContent *, pending_matches_t *, node_search_offset_t *, bool, bool *);

/* Transforme les correspondances locales en trouvailles. */
static void g_scan_token_node_plain_check_backward(const GScanTokenNodePlain *, GScanContext *, GBinContent *, pending_matches_t *, node_search_offset_t *, bool, bool *);



/* ---------------------------------------------------------------------------------- */
/*                          DECOMPOSITION DE MOTIF RECHERCHE                          */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un noeud représentant une bribe de texte à retrouver. */
G_DEFINE_TYPE(GScanTokenNodePlain, g_scan_token_node_plain, G_TYPE_SCAN_TOKEN_NODE);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des noeuds pour motif textuel.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_plain_class_init(GScanTokenNodePlainClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanTokenNodeClass *node;              /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_token_node_plain_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_token_node_plain_finalize;

    node = G_SCAN_TOKEN_NODE_CLASS(klass);

    node->visit = (visit_scan_token_node_fc)g_scan_token_node_plain_visit;
    node->enroll = (enroll_scan_token_node_fc)g_scan_token_node_plain_enroll;
    node->check_forward = (check_scan_token_node_fc)g_scan_token_node_plain_check_forward;
    node->check_backward = (check_scan_token_node_fc)g_scan_token_node_plain_check_backward;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plain = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de noeud pour motif textuel.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_plain_init(GScanTokenNodePlain *plain)
{
    g_scan_token_node_set_flags(G_SCAN_TOKEN_NODE(plain), STNF_PROD);

    init_szstr(&plain->orig);
    plain->modifier = NULL;
    plain->flags = SPNF_NONE;

    plain->raw = NULL;
    plain->atoms = NULL;
    plain->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plain = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_plain_dispose(GScanTokenNodePlain *plain)
{
    g_clear_object(&plain->modifier);

    G_OBJECT_CLASS(g_scan_token_node_plain_parent_class)->dispose(G_OBJECT(plain));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plain = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_token_node_plain_finalize(GScanTokenNodePlain *plain)
{
    size_t i;                               /* Boucle de parcours          */

    exit_szstr(&plain->orig);

    for (i = 0; i < plain->count; i++)
        exit_szstr(&plain->raw[i]);

    if (plain->raw != NULL)
        free(plain->raw);

    if (plain->atoms != NULL)
        free(plain->atoms);

    G_OBJECT_CLASS(g_scan_token_node_plain_parent_class)->finalize(G_OBJECT(plain));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : text     = texte brut à rechercher.                          *
*                modifier = transformateur éventuel à solliciter.             *
*                flags    = particularités à prendre en considération.        *
*                                                                             *
*  Description : Construit un noeud représentant un motif textuel.            *
*                                                                             *
*  Retour      : Mécanismes mis en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanTokenNode *g_scan_token_node_plain_new(const sized_binary_t *text, GScanTokenModifier *modifier, ScanPlainNodeFlags flags)
{
    GScanTokenNode *result;                 /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_TOKEN_NODE_PLAIN, NULL);

    if (!g_scan_token_node_plain_create(G_SCAN_TOKEN_NODE_PLAIN(result), text, modifier, flags))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plain    = encadrement de motif à initialiser pleinement.    *
*                text     = texte brut à rechercher.                          *
*                modifier = transformateur éventuel à solliciter.             *
*                flags    = particularités à prendre en considération.        *
*                                                                             *
*  Description : Met en place un noeud représentant un motif textuel.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_token_node_plain_create(GScanTokenNodePlain *plain, const sized_binary_t *text, GScanTokenModifier *modifier, ScanPlainNodeFlags flags)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    szstrdup(&plain->orig, text);

    if (modifier != NULL)
    {
        plain->modifier = modifier;
        g_object_ref(G_OBJECT(modifier));
    }

    plain->flags = flags;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plain = noeud de motif textuel à consulter.                  *
*                                                                             *
*  Description : Indique les propriétés particulières d'un noeud de texte.    *
*                                                                             *
*  Retour      : Propriétés particulières associées au noeud.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ScanPlainNodeFlags g_scan_token_node_plain_get_flags(const GScanTokenNodePlain *plain)
{
    ScanPlainNodeFlags result;              /* Statut à retourner          */

    result = plain->flags;

    return result;

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

static void g_scan_token_node_plain_visit(GScanTokenNodePlain *node, scan_tree_points_t *points)
{
    if (points->first_plain == NULL)
        points->first_plain = G_SCAN_TOKEN_NODE(node);

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

static bool g_scan_token_node_plain_enroll(GScanTokenNodePlain *node, GScanContext *context, GEngineBackend *backend, size_t maxsize, size_t *slow)
{
    bool result;                            /* Statut à retourner          */
    size_t i;                               /* Boucle de parcours #1       */
    tracked_scan_atom_t atom;               /* Atome identifié             */
    size_t letters;                         /* Nombre de lettres présentes */
    size_t k;                               /* Boucle de parcours #2       */
    size_t extra_count;                     /* Quantité pour l'exhaustivité*/
    sized_binary_t *extra;                  /* Couverture supplémntaire    */
    size_t remaining;                       /* Quantité restant à traiter  */

    /* Génération d'une base de chaînes à couvrir */

    if (node->modifier == NULL)
    {
        node->raw = malloc(sizeof(sized_binary_t));
        node->count = 1;

        szstrdup(&node->raw[0], &node->orig);

        result = true;

    }
    else
        result = g_scan_token_modifier_transform(node->modifier, &node->orig, &node->raw, &node->count);

    if (!result)
        goto exit;

    /* Préparation pour la mémorisation des atomes */

    node->atoms = malloc(node->count * sizeof(tracked_scan_atom_t));

    /* Validation du besoin effectif dans les cas extrèmes */



    // TODO : if (orig.len < ...)



    /* Recherche des atomes */

    for (i = 0; i < node->count; i++)
    {
        if (node->flags & SPNF_CASE_INSENSITIVE)
        {
            find_best_atom(&node->raw[i], maxsize, &atom, &letters);

            if (letters == 0)
                node->atoms[i] = atom;

            /* Insertion des nouvelles combinaisons pour couvrir toutes les casses */
            else
            {
                /* extra_count = 2^letters */
                for (k = 1, extra_count = 2; k < letters; k++, extra_count *= 2)
                    ;

                extra = make_atoms_case_insensitive(&node->raw[i], &atom, extra_count);

                remaining = node->count - i - 1;

                node->count += (extra_count - 1);

                node->raw = realloc(node->raw, node->count * sizeof(sized_binary_t));

                memmove(&node->raw[i + extra_count], &node->raw[i + 1], remaining * sizeof(sized_binary_t));

                for (k = 0; k < extra_count; k++)
                    node->raw[i + k] = extra[k];

                free(extra);

                node->atoms = realloc(node->atoms, node->count * sizeof(tracked_scan_atom_t));

                for (k = 0; k < extra_count; k++)
                    node->atoms[i + k] = atom;

                i += extra_count - 1;

            }

        }

        else
            find_best_atom(&node->raw[i], maxsize, &node->atoms[i], &letters);

    }

    /* Enregistrements en masse */

    for (i = 0; i < node->count && result; i++)
        result = enroll_prepared_atom(&node->raw[i], context, backend, &node->atoms[i]);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw     = contneu brut à retrouver idéalement.               *
*                atom    = contenu brut représentatif ciblé.                  *
*                nocase  = marque un éventuel désintérêt pour la casse.       *
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

static bool check_scan_token_node_plain_content(const sized_binary_t *raw, const tracked_scan_atom_t *atom, bool nocase, phys_t start, GBinContent *content)
{
    bool result;                            /* Bilan à retourner           */
    vmpa2t pos;                             /* Position dans les données   */
    const bin_t *ptr;                       /* Accès aux données brutes    */
    int ret;                                /* Bilan d'une comparaison     */

    result = false;

    init_vmpa(&pos, start, VMPA_NO_VIRTUAL);

    /* Validation du contenu avant l'atome */

    if (atom->pos > 0)
    {
        ptr = g_binary_content_get_raw_access(content, &pos, atom->pos);

        if (nocase)
            ret = memcasecmp(raw->data, ptr, atom->pos);
        else
            ret = memcmp(raw->data, ptr, atom->pos);

        if (ret != 0) goto done;

    }

    /* Validation du contenu après l'atome */

    if (atom->rem > 0)
    {
        advance_vmpa(&pos, atom->len);

        ptr = g_binary_content_get_raw_access(content, &pos, atom->rem);

        if (nocase)
            ret = memcasecmp(raw->data + atom->pos + atom->len, ptr, atom->rem);
        else
            ret = memcmp(raw->data + atom->pos + atom->len, ptr, atom->rem);

        if (ret != 0) goto done;

    }

    result = true;

 done:

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

static void g_scan_token_node_plain_check_forward(const GScanTokenNodePlain *node, GScanContext *context, GBinContent *content, pending_matches_t *matches, node_search_offset_t *offset, bool not, bool *skip)
{
    bool initialized;                       /* Initialisation du suivi ?   */
    bool nocase;                            /* Pas d'intérêt pour la casse */
    size_t ocount;                          /* Quantité de bornes présentes*/
    size_t i;                               /* Boucle de parcours #1       */
    const sized_binary_t *raw;              /* Données brutes d'origine    */
    const tracked_scan_atom_t *atom;        /* Atome correspondant         */
    size_t count;                           /* Quantité de bribes trouvées */
    const phys_t *found;                    /* Localisations des bribes    */
    size_t k;                               /* Boucle de parcours #2       */
    phys_t new_begin;                       /* Nouveau départ à tester     */
    bool status;                            /* Bilan d'une correspondance  */
    size_t pcount;                          /* Nombre de correspondances   */
    match_area_t * const *pending_ptr;      /* Correspondances actuelles   */
    size_t p;                               /* Boucle de parcours #3       */
    const match_area_t *pending;            /* Correspondance à traiter    */

    if (*skip)
        return;

    initialized = are_pending_matches_initialized(matches);

    nocase = (node->flags & SPNF_CASE_INSENSITIVE);

    get_node_search_offset_ranges(offset, &ocount);

    for (i = 0; i < node->count; i++)
    {
        raw = &node->raw[i];
        atom = &node->atoms[i];

        found = g_scan_context_get_atom_matches(context, atom->pid, &count);

        if (!initialized)
        {
            for (k = 0; k < count; k++)
            {
                new_begin = found[k] - atom->pos;

                /**
                 * Si personne n'a manipulé les pré-résultats, mais qu'un décallage
                 * est spécifié par un noeud précédent, une validation sur la base
                 * d'une position 0 est menée.
                 */
                if (ocount > 0)
                {
                    if (!does_node_search_offset_include_pos_forward(offset, 0, new_begin))
                    {
                        if (not)
                            add_pending_match(matches, new_begin, raw->len);

                        continue;

                    }
                }

                status = check_scan_token_node_plain_content(raw, atom, nocase, new_begin, content);

                if ((status && !not) || (!status && not))
                    /**
                     * Il ne peut y avoir qu'une seule séquence d'octets à un même
                     * emplacement, donc le couple (new_begin, len) enregistré est
                     * unique.
                     */
                    add_pending_match(matches, new_begin, raw->len);

            }

        }

        else
        {
            reset_pending_matches_ttl(matches);

            pending_ptr = get_all_pending_matches(matches, &pcount);

            for (p = 0; p < pcount; p++)
            {
                pending = (*pending_ptr) + p;

                assert(matches->content_start <= pending->start);

                for (k = 0; k < count; k++)
                {
                    new_begin = found[k] - atom->pos;

                    /**
                     * Si bornes de tolérance il y a, on valide la position.
                     *
                     * Sinon les correspondances passées et actuelle doivent
                     * être jointes.
                     */
                    if (ocount > 0)
                    {
                        if (!does_node_search_offset_include_pos_forward(offset, pending->end, new_begin))
                        {
                            if (not)
                            {
                                extend_pending_match_ending(matches, p, pending->end + raw->len);

                                /**
                                 * Comme l'extension a pu conduire à un ajout et donc à une
                                 * réallocation de la liste, on recharge l'élément pour les
                                 * itérations suivantes.
                                 */
                                pending = (*pending_ptr) + p;

                            }

                            continue;

                        }
                    }
                    else
                    {
                        if (pending->end != new_begin)
                        {
                            if (not)
                            {
                                extend_pending_match_ending(matches, p, pending->end + raw->len);

                                /**
                                 * Comme l'extension a pu conduire à un ajout et donc à une
                                 * réallocation de la liste, on recharge l'élément pour les
                                 * itérations suivantes.
                                 */
                                pending = (*pending_ptr) + p;

                            }

                            continue;

                        }
                    }

                    status = check_scan_token_node_plain_content(raw, atom, nocase, new_begin, content);

                    if ((status && !not) || (!status && not))
                    {
                        /**
                         * Même si une base de couples uniques est assurée,
                         * la constitution d'un ensemble de noeuds peut amener une
                         * redondance dans les emplacements de correspondances.
                         *
                         * Par exemple, pour la séquence d'octets analysés suivante :
                         *
                         *    aaa....bbb
                         *
                         * La définition { (61 61 | 61 61 61) [4-5] 62 62 62 } peut établir
                         * les correspondances suivantes :
                         *
                         *    aa.....bbb -> couple pending[x] (0;2) puis (0;10)
                         *           ^
                         *     aa....bbb -> couple pending[y] (1;3) puis (1;10)
                         *           ^
                         *    aaa....bbb -> couple pending[z] (0;3) puis (0;10)
                         *           ^
                         *
                         * Par ailleurs, une même base de départ peut conduire
                         * à plusieurs zone de correspondances.
                         *
                         * Par exemple, pour la séquence d'octets analysés suivante :
                         *
                         *    aa..bb..bb
                         *
                         * La définition { 61 61 [2-6] 62 62 } peut établir
                         * les correspondances suivantes :
                         *
                         *    aa..bb..bb -> couple pending[x] (0;2) puis (0;6)
                         *        ^
                         *    aa..bb..bb -> couple pending[x] (0;2) puis (0;10)
                         *            ^
                         */

                        /**
                         * La seconde situation est prise en compte par la fonction
                         * extend_pending_match_ending() qui s'appuie sur le TTL pour
                         * dupliquer la correspondance pending[x] initiale. Le nouvel
                         * élément est placé en fin de liste, ce qui ne boulverse pas
                         * le parcours de liste courant, la valeur de pcount n'étant
                         * pas actualisée.
                         */

                        extend_pending_match_ending(matches, p, new_begin + raw->len);

                        /**
                         * Comme l'extension a pu conduire à un ajout et donc à une
                         * réallocation de la liste, on recharge l'élément pour les
                         * itérations suivantes.
                         */
                        pending = (*pending_ptr) + p;

                    }

                }

            }

            purge_pending_matches(matches);

        }

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

static void g_scan_token_node_plain_check_backward(const GScanTokenNodePlain *node, GScanContext *context, GBinContent *content, pending_matches_t *matches, node_search_offset_t *offset, bool not, bool *skip)
{



    if (*skip)
        return;



    printf("TODO\n");
    assert(0);



}
