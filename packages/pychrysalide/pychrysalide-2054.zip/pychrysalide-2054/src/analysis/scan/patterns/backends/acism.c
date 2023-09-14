
/* Chrysalide - Outil d'analyse de fichiers binaires
 * acism.c - méthode de recherche basée sur l'algorithme Aho-Corasick Interleaved State-transition Matrix
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#include "acism.h"


#include <assert.h>
#include <stdlib.h>
#include <string.h>


#include "acism-int.h"
#include "../../../../common/sort.h"



/* ---------------------- IMPLANTATION D'UNE NOUVELLE APPROCHE ---------------------- */


/* Initialise la classe des méthodes basée sur Bitmap. */
static void g_acism_backend_class_init(GAcismBackendClass *);

/* Initialise une instance de méthodes basée sur Bitmap. */
static void g_acism_backend_init(GAcismBackend *);

/* Supprime toutes les références externes. */
static void g_acism_backend_dispose(GAcismBackend *);

/* Procède à la libération totale de la mémoire. */
static void g_acism_backend_finalize(GAcismBackend *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Indique la taille maximale des suites d'octets recherchées. */
size_t g_acism_backend_get_atom_max_size(const GAcismBackend *);

/* Intègre un motif limité de contenu à rechercher. */
static patid_t g_acism_backend_setup_for(GAcismBackend *, GScanContext *, const uint8_t *, size_t);

/* Inscrit dans le moteur une chaîne de caractères à rechercher. */
static patid_t g_acism_backend_enroll_plain_pattern(GAcismBackend *, GScanContext *, const uint8_t *, size_t);

#ifdef __USE_BYTE_FREQ

/* Compare un niveau de fréquence avec un autre. */
static int compare_byte_frequencies(const acism_freq_rank_t *, const acism_freq_rank_t *);

/* Détermine les identifiants de chaque valeur 8 bits utile. */
static void g_acism_backend_define_codes(GAcismBackend *);

#endif

/* Construit l'arborescence de noeuds de lecture. */
static void g_acism_backend_build_trie(GAcismBackend *);

/* Construit l'arborescence de noeuds de lecture. */
static void g_acism_backend_build_suffix_links(GAcismBackend *);

#ifdef __SORT_BEFORE_BITMASK

/* Compare des noeuds selon l'espace de codes couvert. */
static int compare_node_according_to_code_range(const acism_trie_node_t **, const acism_trie_node_t **);

#endif

/* Organise la convertion de l'arborescence en tableau. */
static void g_acism_backend_prepare_interleave_array(GAcismBackend *);

/* Compresse l'arborescence dans un tableau de position. */
static void g_acism_backend_build_interleave_array(GAcismBackend *);

/* Met en ordre les derniers détails avant un premier scan. */
static void g_acism_backend_warm_up(GAcismBackend *);

/* Parcours un contenu binaire à la recherche de motifs. */
static void g_acism_backend_run_scan(const GAcismBackend *, GScanContext *);

/* Affiche les caractéristques d'un noeud et de ses enfants. */
static void visit_and_output_node(const acism_trie_node_t *, unsigned int);

/* Imprime quelques faits quant aux éléments mis en place. */
static void g_acism_backend_output_stats(const GAcismBackend *);



/* ---------------------------------------------------------------------------------- */
/*                        IMPLANTATION D'UNE NOUVELLE APPROCHE                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un moteur de recherche pour données. */
G_DEFINE_TYPE(GAcismBackend, g_acism_backend, G_TYPE_ENGINE_BACKEND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des méthodes basée sur Bitmap.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_acism_backend_class_init(GAcismBackendClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEngineBackendClass *backend;           /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_acism_backend_dispose;
    object->finalize = (GObjectFinalizeFunc)g_acism_backend_finalize;

    backend = G_ENGINE_BACKEND_CLASS(klass);

    backend->get_max_size = (get_backend_atom_max_size_fc)g_acism_backend_get_atom_max_size;
    backend->enroll_plain = (enroll_plain_into_backend_fc)g_acism_backend_enroll_plain_pattern;
    backend->warm_up = (warm_up_backend_fc)g_acism_backend_warm_up;
    backend->run_scan = (run_backend_scan_fc)g_acism_backend_run_scan;
    backend->output = (output_backend_stats_fc)g_acism_backend_output_stats;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de méthodes basée sur Bitmap.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_acism_backend_init(GAcismBackend *backend)
{
#ifdef __USE_BYTE_FREQ
    size_t i;                               /* Boucle de parcours #1       */
    acism_freq_rank_t *iter;                /* Boucle de parcours #2       */
#endif

#ifdef __USE_BYTE_FREQ
    memset(backend->codes_for_bytes, 0, 256 * sizeof(acism_code_t));
#endif

    backend->nchars = 0;

#ifdef __USE_BYTE_FREQ
    for (i = 0, iter = backend->frequencies; i < 256; i++, iter++)
    {
        iter->frequency = 0;
        iter->rank = i;
    }
#endif

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_acism_backend_dispose(GAcismBackend *backend)
{
    G_OBJECT_CLASS(g_acism_backend_parent_class)->dispose(G_OBJECT(backend));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_acism_backend_finalize(GAcismBackend *backend)
{
    G_OBJECT_CLASS(g_acism_backend_parent_class)->finalize(G_OBJECT(backend));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une méthode de recherche basée sur l'algorithme Acism.  *
*                                                                             *
*  Retour      : Méthode mise en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GEngineBackend *g_acism_backend_new(void)
{
    GAcismBackend *result;                  /* Structure à retourner       */

    result = g_object_new(G_TYPE_ACISM_BACKEND, NULL);

    return G_ENGINE_BACKEND(result);

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à consulter.                   *
*                                                                             *
*  Description : Indique la taille maximale des suites d'octets recherchées.  *
*                                                                             *
*  Retour      : Valeur strictement positive.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_acism_backend_get_atom_max_size(const GAcismBackend *backend)
{
    size_t result;                          /* Taille à faire connaître    */

    result = ACSIM_ATOM_SIZE;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à préparer.                    *
*                context = contexte de l'analyse à mener.                     *
*                plain   = chaîne de caractères classique à intégrer.         *
*                len     = taille de cette chaîne.                            *
*                                                                             *
*  Description : Intègre un motif limité de contenu à rechercher.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static patid_t g_acism_backend_setup_for(GAcismBackend *backend, GScanContext *context, const uint8_t *pattern, size_t len)
{
    patid_t result;                         /* Identifiant à retourner     */
    size_t i;                               /* Boucle de parcours          */
    int ret;                                /* Bilan d'une comparaison     */
    acism_source_t *source;                 /* Définition à mémoriser      */

    result = INVALID_PATTERN_ID;

    /*Recherche d'un motif déjà sollicité */

    /**
     * '\x00\x00\x00\x00abcd1234' '\x01\x01\x01\x01abcd1234' peuvent en effet
     * constituer deux cibles différentes, mais elles comportent normalement
     * la même séquence atomique à rechercher : 'abcd1234'.
     */

    for (i = 0; i < backend->sources_count; i++)
    {
        source = backend->sources + i;

        if (source->len != len)
            continue;

        ret = memcmp(source->atoms, pattern, len);

        if (ret == 0)
        {
            result = source->pid;
            break;
        }

    }

    /* Introduction d'un nouveau motif au besoin */

    if (result == INVALID_PATTERN_ID)
    {
        backend->sources = realloc(backend->sources, ++backend->sources_count * sizeof(acism_source_t));

        source = &backend->sources[backend->sources_count - 1];

        source->atoms = pattern;
        source->len = len;

        result = g_scan_context_get_new_pattern_id(context);
        source->pid = result;

        backend->nchars += len;

#ifdef __USE_BYTE_FREQ
        for (i = 0; i < len; i++)
            backend->frequencies[pattern[i]].frequency++;
#endif

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à manipuler.                   *
*                context = contexte de l'analyse à mener.                     *
*                plain   = chaîne de caractères classique à intégrer.         *
*                len     = taille de cette chaîne.                            *
*                                                                             *
*  Description : Inscrit dans le moteur une chaîne de caractères à rechercher.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static patid_t g_acism_backend_enroll_plain_pattern(GAcismBackend *backend, GScanContext *context, const uint8_t *plain, size_t len)
{
    patid_t result;                         /* Identifiant à retourner     */

    assert(len <= ACSIM_ATOM_SIZE);

    /**
     * Le traitement différé des chaînes à rechercher permet deux choses :
     *   - la construction d'une table de permutation ;
     *   - le décompte des noeuds à allouer (en une seule fois).
     *
     * Si l'intention du premier point est louable (densifier les champs de bits
     * pour allouer moins et tenir plus facilement dans le cache du CPU), la
     * permetutation est extrèmement coûteuse pendant la phase de scan
     * (une lecture supplémentaire par octet de données scannées).
     *
     * Le second point reste valable (à priori).
     *
     * L'appel à la fonction g_acism_backend_setup_for() demeure donc, et l'arbre
     * est construit dans un second temps. La distinction de cette fonction avec
     * la procédure d'enrôlement permet potentiellement d'étuer une bascule à
     * moindre coût un jour.
     */

    result = g_acism_backend_setup_for(backend, context, plain, len);

    return result;

}


#ifdef __USE_BYTE_FREQ


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier élément à comparer.                              *
*                b = second élément à comparer.                               *
*                                                                             *
*  Description : Compare un niveau de fréquence avec un autre.                *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int compare_byte_frequencies(const acism_freq_rank_t *a, const acism_freq_rank_t *b)
{
    int result;                             /* Bilan à retourner           */

    /**
     * Afin d'obtenir les plus grosses fréquences en premier,
     * l'ordre de comparaison est inversé : b < a ?
     */

    result = sort_unsigned_long(b->frequency, a->frequency);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à préparer.                    *
*                                                                             *
*  Description : Détermine les identifiants de chaque valeur 8 bits utile.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_acism_backend_define_codes(GAcismBackend *backend)
{
    size_t i;                               /* Boucle de parcours #1       */
    acism_freq_rank_t *iter;                /* Boucle de parcours #2       */

    /**
     * La redistribution des valeurs d'octet va permettre de compacter
     * par la suite les masques de cellules utilisées pour construire
     * le plus petit tableau des états.
     *
     * L'idée est de grouper le plus possible les états (représentés
     * par un indice) autour de l'état 0.
     */

    qsort(backend->frequencies, 256, sizeof(acism_freq_rank_t), (__compar_fn_t)compare_byte_frequencies);

    /* 0 == racine */
    backend->codes_count++;

#if 0
    for (i = 0, iter = backend->frequencies; i < 256; i++, iter++)
    {
        if (iter->frequency == 0)
            break;

        backend->codes_for_bytes[iter->rank] = backend->codes_count++;

    }
#else
    for (i = 0; i < 256; i++)
        backend->codes_for_bytes[i] = backend->codes_count++;
#endif

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à préparer.                    *
*                                                                             *
*  Description : Construit l'arborescence de noeuds de lecture.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_acism_backend_build_trie(GAcismBackend *backend)
{
    size_t i;                               /* Boucle de parcours #1       */
    acism_trie_node_t *next;                /* Prochain noeud disponible   */
    acism_trie_node_t *node;                /* Tête de parcours            */
    acism_source_t *source;                 /* Définition à mémoriser      */
    size_t k;                               /* Boucle de parcours #2       */
    acism_code_t code;                      /* Identifiant de symbole      */
    acism_trie_node_t *parent;              /* Sauvegarde d'un accès       */

    backend->nodes = calloc(backend->nchars + 1, sizeof(acism_trie_node_t));

    for (i = 0; i < (backend->nchars + 1); i++)
    {
        backend->nodes[i].min_child_code = MAX_ACISM_CODE;
        backend->nodes[i].max_child_code = MIN_ACISM_CODE;
    }

    next = backend->nodes + 1;

    for (i = 0; i < backend->sources_count; i++)
    {
        node = backend->nodes;

        source = &backend->sources[i];

        for (k = 0; k < source->len && node->child != NULL; k++)
        {
#ifdef __USE_BYTE_FREQ
            code = backend->codes_for_bytes[source->atoms[k]];
#else
            code = 1 + source->atoms[k];
#endif

            /* Insertion d'un nouveau noeud au début des enfants */
            if (code < node->child->code)
            {
                next->parent = node;
                next->suffix_link = node;
                next->data = source->atoms[k];
                next->code = code;

                next->sibling = node->child;
                node->child = next++;

                if (code < node->min_child_code) node->min_child_code = code;
                if (code > node->max_child_code) node->max_child_code = code;
                node->children_count++;

                node = node->child;

                k++;
                break;

            }

            parent = node;

            /* Recherche du point d'insertion idéal */
            for (node = node->child;
                 node->sibling != NULL && code >= node->sibling->code;
                 node = node->sibling);

            /* Si le noeud idéal n'existe pas, insertion ordonnée */
            if (code > node->code)
            {
                next->parent = parent;
                next->suffix_link = parent;
                next->data = source->atoms[k];
                next->code = code;

                next->sibling = node->sibling;
                node->sibling = next++;

                if (code < parent->min_child_code) parent->min_child_code = code;
                if (code > parent->max_child_code) parent->max_child_code = code;
                parent->children_count++;

                node = node->sibling;

                k++;
                break;

            }

        }

        /* Creéation d'une nouvelle branche avec le reliquat */
        for (; k < source->len; k++)
        {
#ifdef __USE_BYTE_FREQ
            code = backend->codes_for_bytes[source->atoms[k]];
#else
            code = 1 + source->atoms[k];
#endif

            next->parent = node;
            next->suffix_link = node;
            next->data = source->atoms[k];
            next->code = code;

            node->child = next++;

            if (code < node->min_child_code) node->min_child_code = code;
            if (code > node->max_child_code) node->max_child_code = code;
            node->children_count++;

            node = node->child;

        }

        node->matched_atom = i + 1;

    }

    backend->nodes_used = next - backend->nodes;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à préparer.                    *
*                                                                             *
*  Description : Construit l'arborescence de noeuds de lecture.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_acism_backend_build_suffix_links(GAcismBackend *backend)
{
    size_t max_pos;                         /* Tête de lecture finale      */
    acism_trie_node_t **stack;              /* Pile des noeuds à traiter   */
    size_t rd_pos;                          /* Tête de lecture             */
    size_t wr_pos;                          /* Tête d'écriture             */
    acism_trie_node_t *node;                /* Noeud à traiter             */
    acism_trie_node_t *parent;              /* Noeud parent de la chaîne   */
    acism_trie_node_t *iter;                /* Boucle de parcours          */

    max_pos = backend->nodes_used;

    stack = calloc(max_pos, sizeof(acism_trie_node_t *));

    /* Initialisation du parcours */

    rd_pos = 0;
    wr_pos = 0;

    stack[wr_pos++] = &backend->nodes[0];

    assert(backend->nodes->sibling == NULL);

    /* Traitement manuel de démarrage pour éviter une condition en [0] */

    for (iter = backend->nodes->child; iter != NULL; iter = iter->sibling)
        stack[wr_pos++] = iter;

    rd_pos++;

    /* Suivi des liens déjà en place */

    while (rd_pos < max_pos)
    {
        assert(rd_pos < wr_pos);

        node = stack[rd_pos++];

        /* Remontée jusqu'à la découverte d'un lien d'intérêt */

        for (parent = node->suffix_link; parent != NULL; parent = parent->suffix_link)
        {
            for (iter = parent->child; iter != NULL; iter = iter->sibling)
                if (iter->code == node->code && iter != node)
                {
                    node->suffix_link = iter;
                    break;
                }

            if (iter != NULL)
                break;

        }

        if (parent == NULL /* && node != &backend->nodes [0] */)
            node->suffix_link = backend->nodes;

        /* Inscription des noeuds suivants */

        for (iter = node->child; iter != NULL; iter = iter->sibling)
            stack[wr_pos++] = iter;

    }

    /* Sortie propre */

    free(stack);

}


#ifdef __SORT_BEFORE_BITMASK


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier élément à comparer.                              *
*                b = second élément à comparer.                               *
*                                                                             *
*  Description : Compare des noeuds selon l'espace de codes couvert.          *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int compare_node_according_to_code_range(const acism_trie_node_t **a, const acism_trie_node_t **b)
{
    int result;                             /* Bilan à retourner           */
    const acism_trie_node_t *_a;            /* Autre vision de l'élément #1*/
    const acism_trie_node_t *_b;            /* Autre vision de l'élément #1*/
    acism_code_t range_a;                   /* Espacement des codes #1     */
    acism_code_t range_b;                   /* Espacement des codes #2     */

    result = 0;

    _a = *a;
    _b = *b;

    if (_a->child == NULL)
        result = (_b->child == NULL ? 0 : 1);

    else if (_b->child == NULL)
        result = (_a->child == NULL ? 0 : -1);

    else
    {
        assert(_a->min_child_code <= _a->max_child_code);
        range_a = _a->max_child_code - _a->min_child_code;

        assert(_b->min_child_code <= _b->max_child_code);
        range_b = _b->max_child_code - _b->min_child_code;

        result = sort_unsigned_long(range_b, range_a);

        if (result == 0)
            result = sort_unsigned_long(_b->children_count, _a->children_count);




    }

    return result;

}


#endif


#if 1


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à préparer.                    *
*                                                                             *
*  Description : Organise la convertion de l'arborescence en tableau.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_acism_backend_prepare_interleave_array(GAcismBackend *backend)
{
#ifdef __SORT_BEFORE_BITMASK
    acism_trie_node_t **list;               /* Liste de noeuds alloués     */
#endif
    size_t i;                               /* Boucle de parcours #1       */
    size_t last_free_state;                 /* Dernier emplacement dispo.  */
    size_t full_size;                       /* Cartographie entière        */
    bitfield_t *global_usage;               /* Cartographie des usages     */
    bitfield_t *usage;                      /* Cartographie locale         */
    acism_trie_node_t *node;                /* Noeud en cours de traitement*/
    acism_trie_node_t *iter;                /* Boucle de parcours #2       */
    size_t free_state;                      /* Emplacement libre trouvé    */
    bool found;                             /* Bilan de recherche          */

    size_t bsum;

    /* Préparation de la liste de noeuds à inscrire */

#ifdef __SORT_BEFORE_BITMASK

    list = calloc(backend->nodes_used, sizeof(acism_trie_node_t *));

    for (i = 0; i < backend->nodes_used; i++)
        list[i] = backend->nodes + i;

    qsort(list + 1, backend->nodes_used - 1, sizeof(acism_trie_node_t *),
          (__compar_fn_t)compare_node_according_to_code_range);

#endif

    /* Insertion des noeuds dans l'ordre prévu */

    last_free_state = 257;
    full_size = last_free_state + 257;
    global_usage = create_bit_field(full_size, false);

    bsum = 0;

    usage = create_bit_field(257, false);

    for (i = 0; i < backend->nodes_used; i++)
    {
#ifdef __SORT_BEFORE_BITMASK
        node = list[i];
#else
        node = backend->nodes + i;
#endif

        /* Préparation du masque du noeud */

        reset_all_in_bit_field(usage);

        set_in_bit_field(usage, 0, 1);

        for (iter = node->child; iter != NULL; iter = iter->sibling)
            set_in_bit_field(usage, iter->code, 1);

        assert(popcount_for_bit_field(usage) == (node->children_count + 1));

        /* Recherche d'une position idéale */

        if (i == 0)
            free_state = 0;

        else
            for (free_state = 1; free_state < last_free_state; free_state++)
            {
                found = test_zeros_within_bit_field(global_usage, free_state, usage);
                if (found) break;
            }

        /* Suivi global */

        assert(!test_in_bit_field(global_usage, free_state));

        or_bit_field_at(global_usage, usage, free_state);

        bsum += node->children_count + 1;
        assert(popcount_for_bit_field(global_usage) == bsum);

        node->state_index = free_state;

        if ((free_state + 257) > last_free_state)
        {
            last_free_state += 257;
            full_size += 257;
            resize_bit_field(&global_usage, full_size);
        }

    }

    /* Sotie encadrée */

    backend->bitmap_usage = global_usage;

    delete_bit_field(usage);

#ifdef __SORT_BEFORE_BITMASK
    free(list);
#endif

}


#else


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à préparer.                    *
*                                                                             *
*  Description : Organise la convertion de l'arborescence en tableau.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_acism_backend_prepare_interleave_array(GAcismBackend *backend)
{
    size_t max_pos;                         /* Tête de lecture finale      */
    acism_trie_node_t **stack;              /* Pile des noeuds à traiter   */
    size_t last_free_state;                 /* Dernier emplacement dispo.  */
    size_t full_size;                       /* Cartographie entière        */
    bitfield_t *global_usage;               /* Cartographie des usages     */
    bitfield_t *usage;                      /* Cartographie locale         */
    size_t rd_pos;                          /* Tête de lecture             */
    size_t wr_pos;                          /* Tête d'écriture             */
    acism_trie_node_t *node;                /* Noeud à traiter             */
    acism_trie_node_t *iter;                /* Boucle de parcours          */
    size_t free_state;                      /* Emplacement libre trouvé    */
    bool found;                             /* Bilan de recherche          */

    max_pos = backend->nodes_used;

    stack = calloc(max_pos, sizeof(acism_trie_node_t *));

    last_free_state = 257;
    full_size = last_free_state + 257;
    global_usage = create_bit_field(full_size, false);

    usage = create_bit_field(257, false);

    /* Initialisation du parcours */

    rd_pos = 0;
    wr_pos = 0;

    stack[wr_pos++] = &backend->nodes[0];

    assert(backend->nodes->sibling == NULL);

    /* Traitement manuel de démarrage pour éviter une condition en [0] */

    set_in_bit_field(global_usage, 0, 1);

    for (iter = backend->nodes->child; iter != NULL; iter = iter->sibling)
    {
        set_in_bit_field(global_usage, iter->code, 1);
        stack[wr_pos++] = iter;
    }

    rd_pos++;

    /* Suivi des liens déjà en place */

    while (rd_pos < max_pos)
    {
        assert(rd_pos < wr_pos);

        node = stack[rd_pos++];

        /* Préparation du masque du noeud et inscription des noeuds suivants */

        reset_all_in_bit_field(usage);

        set_in_bit_field(usage, 0, 1);

        for (iter = node->child; iter != NULL; iter = iter->sibling)
        {
            set_in_bit_field(usage, iter->code, 1);
            stack[wr_pos++] = iter;
        }

        assert(popcount_for_bit_field(usage) == (node->children_count + 1));

        /* Recherche d'une position idéale */

        for (free_state = 1; free_state < last_free_state; free_state++)
        {
            found = test_zeros_within_bit_field(global_usage, free_state, usage);
            if (found) break;
        }

        /* Suivi global */

        assert(!test_in_bit_field(global_usage, free_state));

        or_bit_field_at(global_usage, usage, free_state);

        node->state_index = free_state;

        if ((free_state + 257) > last_free_state)
        {
            last_free_state += 257;
            full_size += 257;
            resize_bit_field(&global_usage, full_size);
        }

    }

    /* Sotie encadrée */

    backend->bitmap_usage = global_usage;

    delete_bit_field(usage);

    free(stack);

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à préparer.                    *
*                                                                             *
*  Description : Compresse l'arborescence dans un tableau de position.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_acism_backend_build_interleave_array(GAcismBackend *backend)
{
    size_t maxsize;                         /* Taille maximale du tableau  */
    size_t i;                               /* Boucle de parcours #1       */
    acism_trie_node_t *node;                /* Noeud à transcrire          */
    acism_state_t *base;                    /* Base d'une série de cellules*/
    acism_trie_node_t *iter;                /* Sous-noeud à inscrire #2    */
    acism_trie_node_t *child;               /* Sous-noeud à inscrire #3    */
    uint16_t offset;                        /* Décalage local              */

    maxsize = get_bit_field_size(backend->bitmap_usage);

    backend->states = calloc(maxsize, sizeof(acism_state_t));
    backend->pids = calloc(maxsize, sizeof(patid_t));

    for (i = 0; i < backend->nodes_used; i++)
    {
        node = &backend->nodes[i];
        base = backend->states + node->state_index;

        assert(base[0].code == 0);
        assert(base[0].index == 0);

        if (node->matched_atom > 0)
        {
            base[0].match = 1;
            base[0].atom_size = backend->sources[node->matched_atom - 1].len;

            backend->pids[node->state_index] = backend->sources[node->matched_atom - 1].pid;

            for (iter = node->parent->suffix_link; iter != NULL; iter = iter->suffix_link)
            {
                for (child = iter->child; child != NULL; child = child->sibling)
                    if (child->code == node->code && child->matched_atom > 0)
                        break;

                if (child != NULL)
                {
                    base[0].suffix = 1;
                    break;
                }

            }

        }
        base[0].index = i == 0 ? 0 : node->suffix_link->state_index;

        for (child = node->child; child != NULL; child = child->sibling)
        {
            offset = child->code;

            assert(base[offset].code == 0);
            assert(base[offset].index == 0);

            base[offset].code = child->code;
            base[offset].index = child->state_index;

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à préparer.                    *
*                                                                             *
*  Description : Met en ordre les derniers détails avant un premier scan.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_acism_backend_warm_up(GAcismBackend *backend)
{
#ifdef __USE_BYTE_FREQ

    /**
     * Attribue un identifiant unique pour chaque octet présent dans les
     * motifs recherchés.
     */
    g_acism_backend_define_codes(backend);

#endif

    /**
     * Construit une arborescence de lecture à partir des différents
     * octets présents dans les motifs.
     */
    g_acism_backend_build_trie(backend);

    /**
     * Met en place les liens suivis en cas d'échec de correspondance
     * lors de la lecture d'un octet supplémentaire.
     */
    g_acism_backend_build_suffix_links(backend);

    /**
     * Conversion de l'arborescence en tableau plat et compressé.
     */

    g_acism_backend_prepare_interleave_array(backend);

    g_acism_backend_build_interleave_array(backend);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à manipuler.                   *
*                context = lieu d'enregistrement des résultats.               *
*                                                                             *
*  Description : Parcours un contenu binaire à la recherche de motifs.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_acism_backend_run_scan(const GAcismBackend *backend, GScanContext *context)
{
    GBinContent *content;                   /* Contenu binaire manipulé    */
    phys_t dlen;                            /* Quantité de données         */
    vmpa2t pos;                             /* Point de départ ciblé       */
    const bin_t *data;                      /* Données à analyser          */
#ifdef __USE_BYTE_FREQ
    acism_code_t *codes_for_bytes;
#endif
    acism_state_t *root;                    /* Racine de l'arborescence    */
    acism_state_t *state;                   /* Tête de lecture courante    */
    phys_t i;                               /* Boucle de parcours #1       */
    acism_code_t code;                      /* Code du caractère courant   */
    acism_state_t *next;                    /* Prochaine tête à valider    */
    acism_state_t *iter;                    /* Boucle de parcours #2       */
    acism_state_t *test;                    /* Test de validité alternative*/

    content = g_scan_context_get_content(context);

    dlen = g_binary_content_compute_size(content);

    g_binary_content_compute_start_pos(content, &pos);
    data = g_binary_content_get_raw_access(content, &pos, dlen);

    /* Suivi via l'arborescence aplatie */

#ifdef __USE_BYTE_FREQ
    codes_for_bytes = backend->codes_for_bytes;
#endif

    root = backend->states;
    if (root == NULL) goto done;

    state = root;

    for (i = 0; i < dlen; i++)
    {
#ifdef __USE_BYTE_FREQ
        code = 1 + codes_for_bytes[data[i]];
#else
        code = 1 + data[i];
#endif

        /* Déplacement de la tête de lecture dans l'arborescence */

 retry:

        next = state + code;

        if (next->code == code)
            next = root + next->index;

        else if (state != root)
        {
            state = root + state->index;
            goto retry;
        }

        else
            continue;

        /* Remontée d'éventuels résultats */

        if (next->match)
        {
            g_scan_context_register_atom_match(context,
                                               backend->pids[next - root],
                                               i + 1 - next->atom_size);

            if (next->suffix)
            {
                for (iter = root + state->index; ; iter = root + iter->index)
                {
                    test = iter + code;

                    if (test->code == code)
                    {
                        test = root + test->index;

                        if (test->match)
                        {
                            assert(test->atom_size < next->atom_size);

                            g_scan_context_register_atom_match(context,
                                                               backend->pids[test - root],
                                                               i + 1 - test->atom_size);

                        }

                    }

                    if (iter == root)
                        break;

                }

            }


        }

        /* Bascule au caractère suivant */

        state = next;

    }

 done:

    g_object_unref(G_OBJECT(content));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node  = noeud d'arborescence à traiter.                      *
*                level = profondeur courante.                                 *
*                                                                             *
*  Description : Affiche les caractéristques d'un noeud et de ses enfants.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void visit_and_output_node(const acism_trie_node_t *node, unsigned int level)
{
    unsigned int i;                         /* Boucle de parcours #1       */
    acism_trie_node_t *iter;                /* Boucle de parcours #2       */

    for (i = 0; i < level; i++)
        printf("  ");

    printf(" '%c' (code=%hhu)\n", node->data, node->code);

    for (iter = node->child; iter != NULL; iter = iter->sibling)
        visit_and_output_node(iter, level + 1);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à consulter.                   *
*                                                                             *
*  Description : Imprime quelques faits quant aux éléments mis en place.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_acism_backend_output_stats(const GAcismBackend *backend)
{
    printf("nodes used: %zu\n", backend->nodes_used);

    printf("full_size: %zu (real: %zu)\n",
           get_bit_field_size(backend->bitmap_usage),
           popcount_for_bit_field(backend->bitmap_usage));

    visit_and_output_node(backend->nodes, 0);

}
