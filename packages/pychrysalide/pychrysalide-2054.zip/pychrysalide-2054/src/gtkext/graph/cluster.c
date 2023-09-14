
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cluster.c - mise en place de graphiques
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#include "cluster.h"


#include <assert.h>
#include <malloc.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>


#include "cluster-int.h"
#include "hspace.h"
#include "incoming.h"
#include "leaving.h"
#include "rank.h"
#include "vspace.h"
#include "../gtkblockdisplay.h"
#include "../gtkbufferdisplay.h"
#include "../gtkdisplaypanel.h"
#include "../../common/sort.h"
#include "../../glibext/gloadedpanel.h"



/* -------------------------- DEFINITION D'UN CHEF DE FILE -------------------------- */


/* Mise en disposition de blocs en graphique (instance) */
struct _GGraphCluster
{
    GObject parent;                         /* A laisser en premier        */

    GGraphCluster *owner;                   /* Ensemble lié parent         */
    size_t *parent_index;                   /* Indice du lien au départ    */

    GGraphCluster *container;               /* Conteneur de l'ensemble     */

    incoming_link_t **top_anchors;          /* Accroches supérieures       */
    size_t ta_count;                        /* Quantité de ces accroches   */

    GCodeBlock *block;                      /* Bloc d'origine représenté   */
    GtkWidget *display;                     /* Vue graphique associée      */
    GtkAllocation alloc;                    /* Emplacement final du bloc   */

    gint left_offset;                       /* Besoin d'espace à gauche    */
    gint right_offset;                      /* Besoin d'espace à droite    */

    leaving_link_t **bottom_anchors;        /* Accroches inférieures       */
    size_t ba_count;                        /* Quantité de ces accroches   */

    bool has_straight;                      /* Présence d'une ligne droite */
    size_t straight_level;                  /* Rang atteint en ligne droite*/
    size_t straight_index;                  /* Indice du lien vertical     */

    graph_rank_t *ranks;                    /* Répartition verticale       */
    size_t ranks_count;                     /* Nombre de divisions         */

    vspace_manager_t self;                  /* Gestion d'un retour direct  */

};

/* Mise en disposition de blocs en graphique (classe) */
struct _GGraphClusterClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};



/* Initialise la classe des mises en disposition graphique. */
static void g_graph_cluster_class_init(GGraphClusterClass *);

/* Initialise une mise en disposition de blocs en graphique. */
static void g_graph_cluster_init(GGraphCluster *);

/* Supprime toutes les références externes. */
static void g_graph_cluster_dispose(GGraphCluster *);

/* Procède à la libération totale de la mémoire. */
static void g_graph_cluster_finalize(GGraphCluster *);

/* Complète un graphique avec un sous-ensemble de blocs. */
static void g_graph_cluster_add_sub(GGraphCluster *, GGraphCluster *);

/* Etablit les connexions entre blocs selon les rangs. */
static void g_graph_cluster_setup_link_for_target(GGraphCluster *, GGraphCluster *, leaving_link_t *);

/* Inscrit à l'endroit idéal une réservation d'espace latéral. */
static void g_graph_cluster_extend_vspace_manager(GGraphCluster *, leaving_link_t *, incoming_link_t *, GdkPoint *);

/* Ajoute une marge à gauche pour les liens remontants. */
static void g_graph_cluster_insert_left_margin(GGraphCluster *, gint);

/* Détermine les abscisses de tous les liens en place. */
static void g_graph_cluster_compute_link_x_positions(GGraphCluster *);

/* Réserve de l'espace vertical pour les lignes horizontales. */
static void g_graph_cluster_book_hspace_for_links(GGraphCluster *);

/* Applique les positions calculées pour chaque lien graphique. */
static void g_graph_cluster_resolve_links(const GGraphCluster *);



/* ------------------------- CALCUL DE REPARTITION DE BLOCS ------------------------- */


/* Liste de blocs restants à traiter */
typedef struct _pending_blocks
{
    size_t count;                           /* Taille de la liste          */
    GCodeBlock *list[0];                    /* Liste de blocs à traiter    */

} pending_blocks;


/* Met en place un ensemble de blocs sous forme graphique. */
static GGraphCluster *setup_graph_clusters(GLoadedBinary *, const GBlockList *, size_t , segcnt_list *, pending_blocks *, GHashTable *);



/* ---------------------------------------------------------------------------------- */
/*                            DEFINITION D'UN CHEF DE FILE                            */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour les mises en disposition graphique. */
G_DEFINE_TYPE(GGraphCluster, g_graph_cluster, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des mises en disposition graphique.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_cluster_class_init(GGraphClusterClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_graph_cluster_dispose;
    object->finalize = (GObjectFinalizeFunc)g_graph_cluster_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une mise en disposition de blocs en graphique.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_cluster_init(GGraphCluster *cluster)
{
    cluster->container = cluster;

    cluster->left_offset = 0;
    cluster->right_offset = 0;

    init_vspace_manager(&cluster->self);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_cluster_dispose(GGraphCluster *cluster)
{
    g_clear_object(&cluster->block);
    g_clear_object(&cluster->display);

    G_OBJECT_CLASS(g_graph_cluster_parent_class)->dispose(G_OBJECT(cluster));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_cluster_finalize(GGraphCluster *cluster)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < cluster->ta_count; i++)
        delete_incoming_link(cluster->top_anchors[i]);

    if (cluster->top_anchors != NULL)
        free(cluster->top_anchors);

    for (i = 0; i < cluster->ba_count; i++)
        delete_leaving_link(cluster->bottom_anchors[i]);

    if (cluster->bottom_anchors != NULL)
        free(cluster->bottom_anchors);

    for (i = 0; i < cluster->ranks_count; i++)
        exit_graph_rank(&cluster->ranks[i]);

    if (cluster->ranks != NULL)
        free(cluster->ranks);

    exit_vspace_manager(&cluster->self);

    G_OBJECT_CLASS(g_graph_cluster_parent_class)->finalize(G_OBJECT(cluster));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block       = premier bloc du groupe.                        *
*                highlighted = gestionnaire de surbrillance pour segments.    *
*                binary      = binaire charger dont le code est à représenter.*
*                                                                             *
*  Description :             *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGraphCluster *g_graph_cluster_new(GCodeBlock *block, segcnt_list *highlighted, GLoadedBinary *binary)
{
    GGraphCluster *result;                  /* Structure à retourner       */
    GBufferView *view;                      /* Partie affichée du tampon   */

    result = g_object_new(G_TYPE_GRAPH_CLUSTER, NULL);

    /* Encapsulation du bloc d'entrée */

    result->block = block;
    g_object_ref(G_OBJECT(block));

    view = g_code_block_get_view(result->block, highlighted);

    result->display = gtk_block_display_new(view);
    gtk_widget_show(result->display);

    g_loaded_panel_set_content(G_LOADED_PANEL(result->display), G_LOADED_CONTENT(binary));

    gtk_block_display_override_view_index(GTK_BLOCK_DISPLAY(result->display), BVW_GRAPH);

    gtk_display_panel_show_border(GTK_DISPLAY_PANEL(result->display), true);

    g_graph_cluster_reset_allocation(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à traiter.                      *
*                                                                             *
*  Description : Assigne à un bloc et son ensemble un emplacement initial.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_reset_allocation(GGraphCluster *cluster)
{
    GtkRequisition requisition;             /* Taille à l'écran actuelle   */
    size_t i;                               /* Boucle de parcours          */

    /* Détermination d'une position initiale centrée */

    gtk_widget_get_preferred_size(cluster->display, NULL, &requisition);

    cluster->alloc.x = -requisition.width / 2;
    cluster->alloc.y = 0;

    cluster->alloc.width = requisition.width;
    cluster->alloc.height = requisition.height;

    /* Propagation aux sous-blocs */

    for (i = 0; i < cluster->ranks_count; i++)
        visit_graph_rank(&cluster->ranks[i], g_graph_cluster_reset_allocation);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à compléter.                    *
*                sub     = sous-ensemble à intégrer.                          *
*                                                                             *
*  Description : Complète un graphique avec un sous-ensemble de blocs.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_cluster_add_sub(GGraphCluster *cluster, GGraphCluster *sub)
{
    size_t level;                           /* Niveau du nouvel ensemble   */
    size_t i;                               /* Boucle de parcours          */
    graph_rank_t new;                       /* Nouvel étage à insérer      */

    level = g_code_block_get_rank(sub->block);

    for (i = 0; i < cluster->ranks_count; i++)
        if (get_graph_rank(&cluster->ranks[i]) == level)
            break;

    if (i == cluster->ranks_count)
    {
        init_graph_rank(&new, sub);

        cluster->ranks = qinsert(cluster->ranks, &cluster->ranks_count,
                                 sizeof(graph_rank_t), (__compar_fn_t)cmp_graph_rank, &new);

    }

    else
        extend_graph_rank(&cluster->ranks[i], sub);

    sub->owner = cluster;

    if (sub->ranks_count == 0)
        sub->container = cluster;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grank   = ensemble de descendants d'un même rang.            *
*                source  = bloc courant ou NULL pour limiter les calculs.     *
*                target  = bloc ciblé pour l'arrivée d'un lien.               *
*                leaving = représentation d'un lien sortant.                  *
*                                                                             *
*  Description : Etablit les connexions entre blocs selon les rangs.          *
*                                                                             *
*  Retour      : true si la cible a été rencontrée.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_cluster_setup_link_for_target(GGraphCluster *source, GGraphCluster *target, leaving_link_t *leaving)
{
    size_t level;                           /* Niveau du nouvel ensemble   */
    size_t target_level;                    /* Rang du bloc ciblé          */

    target->parent_index = &leaving->index;

    if (source != NULL)
    {
        level = g_code_block_get_rank(source->block);
        target_level = g_code_block_get_rank(target->block);

        /* Est-ce un lien qui doit être vertical ? */

        if (target_level > (level + 1) && target_level > source->straight_level)
        {
            source->has_straight = true;
            source->straight_level = target_level;
            source->straight_index = source->ba_count - 1;
        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = ensemble de descendants d'un même rang.             *
*                from   = point de départ du lien concerné.                   *
*                to     = point d'arrivée du lien concerné.                   *
*                pts    = points intermédiaires du tracé complet final.       *
*                                                                             *
*  Description : Inscrit à l'endroit idéal une réservation d'espace latéral.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_cluster_extend_vspace_manager(GGraphCluster *target, leaving_link_t *from, incoming_link_t *to, GdkPoint *pts)
{
    bool done;                              /* Bilan des traitements       */
    GGraphCluster *container;               /* Arrivée de boucle extérieure*/
    size_t i;                               /* Boucle de parcours          */

    assert(target == to->owner);

    done = false;

    if (from->owner == target)
        extend_vspace_manager(&target->self, from, to, pts, false);

    else
    {
        for (i = 0; i < target->ranks_count && !done; i++)
            done = extend_graph_rank_vspace_manager(&target->ranks[i], from, to, pts, false);

        container = from->owner->owner;
        assert(container != NULL);

        for (i = 0; i < container->ranks_count && !done; i++)
            done = extend_graph_rank_vspace_manager(&container->ranks[i], from, to, pts, true);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à actualiser.                   *
*                all     = table regroupant tous les groupes créés.           *
*                                                                             *
*  Description : Met en place les embryons de liens nécessaires.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_define_links(GGraphCluster *cluster, GHashTable *all)
{
    size_t dcount;                          /* Nombre de liens de dest.    */
    block_link_t *links;                    /* Liens associés au bloc      */
    size_t i;                               /* Boucle de parcours          */
    block_link_t *dest;                     /* Bloc visé par un autre      */
    GGraphCluster *target;                  /* Bloc ciblé par un lien      */
    leaving_link_t *leaving;                /* Point de départ d'un lien   */
    incoming_link_t *incoming;              /* Définitions d'arrivée       */
    GdkPoint *midpts;                       /* Points intermédiaires       */

    /* Au niveau du bloc courant */

    links = g_code_block_get_destinations(cluster->block, &dcount);

    for (i = 0; i < dcount; i++)
    {
        dest = &links[i];

        switch (dest->type)
        {
            case ILT_EXEC_FLOW:
            case ILT_JUMP:
            case ILT_CASE_JUMP:
            case ILT_JUMP_IF_TRUE:
            case ILT_JUMP_IF_FALSE:

                target = G_GRAPH_CLUSTER(g_hash_table_lookup(all, dest->linked));
                assert(target != NULL);

                /* Point de départ */

                leaving = create_leaving_link(cluster, cluster->ba_count);

                cluster->bottom_anchors = realloc(cluster->bottom_anchors,
                                                  ++cluster->ba_count * sizeof(leaving_link_t *));

                cluster->bottom_anchors[cluster->ba_count - 1] = leaving;

                /* Point d'arrivée */

                incoming = create_incoming_link(target, dest->type, leaving);

                target->top_anchors = realloc(target->top_anchors,
                                              ++target->ta_count * sizeof(incoming_link_t *));

                target->top_anchors[target->ta_count - 1] = incoming;

                /* Etablissement d'un embryon de lien */

                leaving->other = incoming;

                g_graph_cluster_setup_link_for_target(cluster, target, leaving);

                break;

            case ILT_LOOP:

                target = G_GRAPH_CLUSTER(g_hash_table_lookup(all, dest->linked));
                assert(target != NULL);

                /* Point de départ */

                leaving = create_leaving_link(cluster, cluster->ba_count);

                cluster->bottom_anchors = realloc(cluster->bottom_anchors,
                                                  ++cluster->ba_count * sizeof(leaving_link_t *));

                cluster->bottom_anchors[cluster->ba_count - 1] = leaving;

                /* Point d'arrivée */

                midpts = malloc(2 * sizeof(GdkPoint));

                incoming = create_incoming_loop_link(target, midpts, leaving);

                target->top_anchors = realloc(target->top_anchors,
                                              ++target->ta_count * sizeof(incoming_link_t *));

                target->top_anchors[target->ta_count - 1] = incoming;

                /* Réservation d'un espace latéral */

                g_graph_cluster_extend_vspace_manager(target, leaving, incoming, midpts);

                /* Etablissement d'un embryon de lien */

                leaving->other = incoming;

                g_graph_cluster_setup_link_for_target(NULL, target, leaving);

                break;

            default:
                break;

        }

        unref_block_link(dest);

    }

    if (links != NULL)
        free(links);

    /* Doit-on forcer un lien strictement vertical ? */

    if (cluster->ba_count == 1 && !cluster->has_straight)
    {
        /**
         * Attention : les boucles aussi ont un seul lien sortant !
         *
         * S'il n'y a qu'un seul lien, on peut s'appuyer sur la variable 'incoming'
         * manipulée dans la boucle : c'est forcément elle qui a été mise en place.
         *
         * Même chose pour 'target'.
         */
        if (incoming->type != ILT_LOOP)
        {
            cluster->has_straight = true;
            cluster->straight_level = g_code_block_get_rank(target->block);
            cluster->straight_index = 0;
        }

    }

    /* Déplacement d'un éventuel lien central en position centrale */

    if (0 && cluster->has_straight)
    {
        size_t center;
        leaving_link_t *tmp;

        if (cluster->ba_count % 2 == 0)
            center = cluster->ba_count / 2 - 1;
        else
            center = cluster->ba_count / 2;

        if (cluster->straight_index < center)
        {
            tmp = cluster->bottom_anchors[cluster->straight_index];

            memmove(cluster->bottom_anchors + cluster->straight_index,
                    cluster->bottom_anchors + cluster->straight_index + 1,
                    (center - cluster->straight_index) * sizeof(leaving_link_t *));

            cluster->bottom_anchors[center] = tmp;

            for (i = cluster->straight_index; i <= center; i++)
                cluster->bottom_anchors[i]->index = i;

            cluster->straight_index = center;

        }

        else if (cluster->straight_index > center)
        {
            tmp = cluster->bottom_anchors[cluster->straight_index];

            memmove(cluster->bottom_anchors + center + 1,
                    cluster->bottom_anchors + center,
                    (cluster->straight_index - center) * sizeof(leaving_link_t *));

            cluster->bottom_anchors[center] = tmp;

            for (i = center; i <= cluster->straight_index ; i++)
                cluster->bottom_anchors[i]->index = i;

            cluster->straight_index = center;

        }

    }

    /* Propagation de la mise en place */

    for (i = 0; i < cluster->ranks_count; i++)
        define_graph_rank_links(&cluster->ranks[i], all);

}



/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à actualiser.                   *
*                                                                             *
*  Description : Repère les liens marquants à destination d'autres blocs.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_setup_links(GGraphCluster *cluster)
{
    size_t i;                               /* Boucle de parcours #1       */
    leaving_link_t *leaving;                /* Départ de lien              */
    incoming_link_t *incoming;              /* Arrivée de lien             */
    size_t level;                           /* Niveau du bloc courant      */
    size_t target_level;                    /* Rang du bloc ciblé          */
    GGraphCluster *container;               /* Conteneur parent à parcourir*/
    size_t k;                               /* Boucle de parcours #2       */

    for (i = 0; i < cluster->ba_count; i++)
    {
        leaving = cluster->bottom_anchors[i];
        incoming = leaving->other;

        if (incoming->type == ILT_LOOP)
            continue;

        /* Est-ce un lien qui doit être vertical ? */

        level = g_code_block_get_rank(leaving->owner->block);
        target_level = g_code_block_get_rank(incoming->owner->block);

        if (target_level > (level + 1))
        {
            leaving->straight = true;
            leaving->straight_level = target_level;
        }

        /* Est-ce une sortie de cluster ? */

        if (leaving->owner->container != incoming->owner->container)
        {
            container = leaving->owner->container;

            for (k = 0; k < container->ranks_count; k++)
                if (has_graph_rank_cluster(&container->ranks[k], incoming->owner))
                    break;

            if (k == container->ranks_count)
                leaving->cluster_exit = true;

        }

        /* Doit-on forcer un lien strictement vertical ? */

        if (cluster->ba_count == 1)
        {
            if (incoming->type == ILT_EXEC_FLOW)
                leaving->forced_straight = true;

            else if (incoming->type == ILT_JUMP)
            {
                for (k = 0; k < incoming->owner->ta_count; k++)
                    if (incoming->owner->top_anchors[k] != incoming
                        && incoming->owner->top_anchors[k]->type != ILT_LOOP)
                    {
                        break;
                    }

                leaving->forced_straight = (k == incoming->owner->ta_count);

            }

            if (leaving->forced_straight)
                leaving->straight_level = target_level;

        }

    }

    /* Propagation de la mise en place */

    for (i = 0; i < cluster->ranks_count; i++)
        visit_graph_rank(&cluster->ranks[i], g_graph_cluster_setup_links);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à manipuler.                    *
*                idx     = indice du lien éventuellement identifié. [OUT]     *
*                                                                             *
*  Description : Détermine un éventuel lien entrant réellement vertical.      *
*                                                                             *
*  Retour      : Lien entrant véritablement vertical.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

incoming_link_t *g_graph_cluster_find_real_straight_incoming(GGraphCluster *cluster, size_t *idx)
{
    incoming_link_t *result;                /* Lien entrant à retourner    */
    size_t straight_idx;                    /* Lien vertical le plus adapté*/
    size_t forced_idx;                      /* Lien vertical forcé         */
    bool drop_forced;                       /* Invalidation de cet indice  */
    size_t i;                               /* Boucle de parcours #1       */
    leaving_link_t *leaving;                /* Départ de lien              */
    GCodeBlock *block[2];                   /* Accès rapide aux blocs      */

    straight_idx = cluster->ta_count;
    forced_idx = cluster->ta_count;

    drop_forced = false;

    /* Recherche des candidats potentiels */

    for (i = 0; i < cluster->ta_count; i++)
    {
        leaving = cluster->top_anchors[i]->other;

        if (leaving->straight)
        {
            if (straight_idx < cluster->ta_count)
            {
                block[0] = leaving->owner->block;
                block[1] = cluster->top_anchors[straight_idx]->other->owner->block;

                if (g_code_block_get_rank(block[0]) <= g_code_block_get_rank(block[1]))
                    straight_idx = i;

            }

            else
                straight_idx = i;

        }

        if (leaving->forced_straight)
        {
            /**
             * Il ne peut y avoir qu'un lien forcé pour une entrée de bloc donnée !
             */
            assert(forced_idx == cluster->ta_count);

            forced_idx = i;

        }

        if (cluster->top_anchors[i]->type != ILT_LOOP)
            drop_forced |= (!leaving->straight && !leaving->forced_straight && !leaving->cluster_exit);

    }

    /* Détermination du résultat final */

    if (drop_forced)
        forced_idx = cluster->ta_count;

    if (straight_idx < cluster->ta_count || forced_idx < cluster->ta_count)
    {
        *idx = (forced_idx < cluster->ta_count ? forced_idx : straight_idx);

        result = cluster->top_anchors[*idx];

    }

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à manipuler.                    *
*                                                                             *
*  Description : Organise la disposition d'un ensemble de blocs basiques.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_dispatch_x(GGraphCluster *cluster)
{
    size_t idx;                             /* Indice de lien d'arrivée    */
    incoming_link_t *incoming;              /* Arrivée de lien             */
    leaving_link_t *leaving;                /* Départ de lien              */
    gint start;                             /* Position initiale de départ */
    gint end;                               /* Position initiale d'arrivée */
    size_t i;                               /* Boucle de parcours #1       */
    leaving_link_t *straight_leaving;       /* Lien à présenter vertical   */
    size_t straight_index;                  /* Indice du lien vertical     */
    gint straight_start;                    /* Position initiale de départ */
    size_t straight_level;                  /* Rang atteint en ligne droite*/
    const graph_rank_t *rank;               /* Accès confortable au rang   */
    size_t j;                               /* Boucle de parcours #2       */
    GGraphCluster *target;                  /* Unique sous-bloc visé       */

    /**
     * Traitement amont : alignement sur une éventuelle origine.
     */

    incoming = g_graph_cluster_find_real_straight_incoming(cluster, &idx);

    if (incoming != NULL)
    {
        leaving = incoming->other;

        start = g_graph_cluster_compute_leaving_link_position(leaving->owner, leaving->index);

        end = g_graph_cluster_compute_incoming_link_position(cluster, idx);

        g_graph_cluster_offset_x(cluster, start - end);

    }

    /**
     * Traitement aval : alignement selon une éventuelle bordure verticale.
     */

    /* Recherche d'une limite verticale */

    straight_leaving = NULL;

    for (i = 0; i < cluster->ba_count; i++)
        if (SHOULD_BE_VERTICAL(cluster->bottom_anchors[i]))
        {
            straight_leaving = cluster->bottom_anchors[i];
            straight_index = i;

            straight_start = g_graph_cluster_compute_leaving_link_position(cluster, i);
            straight_level = straight_leaving->straight_level;

            break;

        }

    /* Il est désormais temps de placer tous les blocs de code inférieurs. */

    for (i = 0; i < cluster->ranks_count; i++)
    {
        rank = &cluster->ranks[i];

        /* Répartition autour d'une ligne verticale */
        if (straight_leaving != NULL)
        {
            if (get_graph_rank(rank) < straight_level)
            {
                /* Répartition à gauche du lien */

                for (j = rank->count; j > 0; j--)
                    if (*rank->clusters[j - 1]->parent_index < straight_index)
                        break;

                start = straight_start - LINK_MARGIN;

                _place_graph_rank_clusters(rank->clusters, j, start, -1);

                /* Répartition à droite du lien */

                for (j = 0; j < rank->count; j++)
                    if (*rank->clusters[j]->parent_index > straight_index)
                        break;

                start = straight_start + LINK_MARGIN + cluster->right_offset;

                _place_graph_rank_clusters(rank->clusters + j, rank->count - j, start, 1);

            }

            else if (get_graph_rank(rank) == straight_level)
            {
                dispatch_x_graph_rank(rank);

                straight_leaving = NULL;

                goto look_for_forced;

            }

            else
                assert(false);

        }

        /* Répartition homogène */
        else
        {
            dispatch_x_graph_rank(rank);

 look_for_forced:

            /* Lien vertical interne ? */

            if (rank->count != 1)
                continue;

            target = rank->clusters[0];

            if (target->ba_count != 1)
                continue;

            leaving = target->bottom_anchors[0];

            if (leaving->forced_straight)
            {
                straight_leaving = leaving;
                straight_index = 0;

                straight_start = g_graph_cluster_compute_leaving_link_position(target, 0);
                straight_level = leaving->straight_level;

            }

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à consulter.                    *
*                root    = ensemble dont s'extraire.                          *
*                max     = ordonnée maximale de la zone de travail.           *
*                pos     = abscisses minimale et maximale en bout. [OUT]      *
*                                                                             *
*  Description : Calcule les abscisses extrèmes atteintes via liens de sortie.*
*                                                                             *
*  Retour      : false si une incapacité de détermination a été rencontrée.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_graph_cluster_compute_min_max_x_exit(const GGraphCluster *cluster, const GGraphCluster *root, gint pos[2])
{
    bool result;                            /* Bilan à renvoyer            */
    size_t i;                               /* Boucle de parcours #1       */
    const leaving_link_t *leaving;          /* Lien sortant à traiter      */
    bool stop;                              /* Prépare la fin de parcours  */
    GGraphCluster *iter;                    /* Boucle de parcours #2       */
    gint x;                                 /* Abscisse rencontrée         */

    result = false;

    for (i = 0; i < cluster->ba_count; i++)
    {
        leaving = cluster->bottom_anchors[i];

        if (leaving->other->type == ILT_LOOP)
            continue;

        stop = leaving->cluster_exit;

        /* Validation d'une sortie du cluster d'origine */

        if (stop)
        {
            for (iter = leaving->other->owner; iter != NULL; iter = iter->owner)
                if (iter == root)
                    break;

            stop = (iter == NULL);

        }

        /* Poursuite du lien */

        if (stop)
        {
            x = compute_leaving_link_position(leaving);

            if (x < pos[0])
            {
                pos[0] = x;
                result = true;
            }

            if (x > pos[1])
            {
                pos[1] = x;
                result = true;
            }

        }

        else
            result |= g_graph_cluster_compute_min_max_x_exit(leaving->other->owner, root, pos);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à consulter.                    *
*                max     = profondeur maximale des traitements en ordonnée.   *
*                pos     = ordonnées minimale et maximale en bout. [OUT]      *
*                                                                             *
*  Description : Calcule les abscisses extrèmes atteintes horizontalement.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_compute_min_max_horizontal(const GGraphCluster *cluster, gint max, gint pos[2])
{
    size_t i;                               /* Boucle de parcours          */
    const leaving_link_t *leaving;          /* Lien sortant du bloc        */

    if (cluster->alloc.y < max)
    {
        if (cluster->alloc.x < pos[0])
            pos[0] = cluster->alloc.x;

        if ((cluster->alloc.x + cluster->alloc.width) > pos[1])
            pos[1] = cluster->alloc.x + cluster->alloc.width;

        for (i = 0; i < cluster->ba_count; i++)
        {
            leaving = cluster->bottom_anchors[i];

            if (leaving->other->type == ILT_LOOP)
                continue;

            g_graph_cluster_compute_min_max_horizontal(leaving->other->owner, max, pos);

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à manipuler.                    *
*                                                                             *
*  Description : Définit d'éventuels décalages pour les lignes verticales.    *
*                                                                             *
*  Retour      : true si un changement est survenu, false sinon.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_graph_cluster_dispatch_define_extra_offset(GGraphCluster *cluster)
{
    bool result;                            /* Evolution à retourner       */
    size_t i;                               /* Boucle de parcours #1       */
    leaving_link_t *straight_leaving;       /* Lien à présenter vertical   */
    size_t straight_index;                  /* Indice du lien vertical     */
    gint straight_start;                    /* Position initiale de départ */
    size_t straight_level;                  /* Rang atteint en ligne droite*/
    const graph_rank_t *rank;               /* Accès confortable au rang   */
    size_t j;                               /* Boucle de parcours #2       */
    gint straight_depth;                    /* Profondeur du lien vertical */
    gint depth;                             /* Profondeur du lien voisin   */
    gint x_exit[2];                         /* Bornes des liens de sortie  */
#ifndef NDEBUG
    bool status;                            /* Validation des obtentions   */
#endif
    gint x_used[2];                         /* Bornes d'utilisations       */
    bool changed;                           /* Note un changement d'état   */
    gint offset;                            /* Décalage à appliquer        */
    GGraphCluster *parent;                  /* Racine pour les mises à jour*/
    GGraphCluster *target;                  /* Unique sous-bloc visé       */
    leaving_link_t *leaving;                /* Départ de lien              */

    result = false;

    /**
     * Le corps de cette fonction est calqué sur celui de g_graph_cluster_dispatch_x(),
     * à partir du traitement amon.
     *
     * Toute modification dans ces parties doit donc être synchronisée.
     */

    /* Recherche d'une limite verticale */

    straight_leaving = NULL;

    for (i = 0; i < cluster->ba_count; i++)
        if (SHOULD_BE_VERTICAL(cluster->bottom_anchors[i]))
        {
            straight_leaving = cluster->bottom_anchors[i];
            straight_index = i;

            straight_start = g_graph_cluster_compute_leaving_link_position(cluster, i);
            straight_level = straight_leaving->straight_level;

            break;

        }

    /* Il est désormais temps de placer tous les blocs de code inférieurs. */

    for (i = 0; i < cluster->ranks_count; i++)
    {
        rank = &cluster->ranks[i];

        /* Répartition autour d'une ligne verticale */
        if (straight_leaving != NULL)
        {
            if (get_graph_rank(rank) < straight_level)
            {
                /* Répartition à gauche du lien */

                for (j = rank->count; j > 0; j--)
                    if (*rank->clusters[j - 1]->parent_index < straight_index)
                        break;

                /* Répartition à droite du lien */

                for (j = 0; j < rank->count; j++)
                    if (*rank->clusters[j]->parent_index > straight_index)
                        break;

                if (j < rank->count)
                {
                    if (straight_leaving->cluster_exit)
                    {
                        straight_depth = straight_leaving->other->owner->alloc.y;

                        depth = G_MAXINT;

                        if (g_graph_cluster_compute_min_y_target(rank->clusters[j], cluster, &depth))
                        {
                            x_exit[0] = G_MAXINT;
                            x_exit[1] = G_MININT;

#ifndef NDEBUG
                            status = g_graph_cluster_compute_min_max_x_exit(rank->clusters[j], cluster, x_exit);
                            assert(status);
#else
                            g_graph_cluster_compute_min_max_x_exit(rank->clusters[j], cluster, x_exit);
#endif

                            x_used[0] = G_MAXINT;
                            x_used[1] = G_MININT;

                            changed = false;

                            if (straight_depth > depth)
                            {
                                g_graph_cluster_compute_min_max_horizontal(rank->clusters[j],
                                                                           straight_depth, x_used);

                                if (straight_start > x_used[0])
                                {
                                    offset = straight_start - x_used[0] + LINK_MARGIN;

                                    if (offset != 0)
                                    {
                                        cluster->right_offset += offset;
                                        changed = true;
                                    }

                                }

                            }

                            else
                            {
                                g_graph_cluster_compute_min_max_horizontal(straight_leaving->other->owner,
                                                                           depth, x_used);

                                if (x_used[1] > x_exit[0])
                                {
                                    offset = x_used[1] - x_exit[0] + LINK_MARGIN;

                                    if (offset != 0)
                                    {
                                        cluster->right_offset += offset;
                                        changed = true;
                                    }

                                }

                            }

                            /* Réorganisation suite à changement ? */
                            if (changed)
                            {
                                result = true;

                                parent = cluster->owner;

                                if (parent != NULL)
                                {
                                    g_graph_cluster_sort_leaving_links(parent);

                                    for (i = 0; i < parent->ranks_count; i++)
                                        visit_graph_rank(&parent->ranks[i], g_graph_cluster_reset_allocation);

                                    g_graph_cluster_dispatch_x(parent);

                                    g_graph_cluster_set_y(parent, parent->alloc.y);

                                    g_graph_cluster_sort_leaving_links(parent);

                                }

                            }

                        }

                    }

                }

                result |= visit_and_accumulate_graph_rank(rank, g_graph_cluster_dispatch_define_extra_offset);

            }

            else if (get_graph_rank(rank) == straight_level)
            {
                result |= visit_and_accumulate_graph_rank(rank, g_graph_cluster_dispatch_define_extra_offset);

                straight_leaving = NULL;

                goto look_for_forced;

            }

            else
                assert(false);

        }

        /* Répartition homogène */
        else
        {
            result |= visit_and_accumulate_graph_rank(rank, g_graph_cluster_dispatch_define_extra_offset);

 look_for_forced:

            /* Lien vertical interne ? */

            if (rank->count != 1)
                continue;

            target = rank->clusters[0];

            if (target->ba_count != 1)
                continue;

            leaving = target->bottom_anchors[0];

            if (leaving->forced_straight)
            {
                straight_leaving = leaving;
                straight_index = 0;

                straight_start = g_graph_cluster_compute_leaving_link_position(target, 0);
                straight_level = leaving->straight_level;

            }

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à analyser.                     *
*                x1      = abscisse de départ du lien d'origine.              *
*                max     = ordonnée la plus profonde à ne pas dépasser.       *
*                                                                             *
*  Description : Détermine une direction préférée pour la suite du bloc.      *
*                                                                             *
*  Retour      : false si une incapacité de détermination a été rencontrée.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

LeavingLinkDir g_graph_cluster_get_link_direction(const GGraphCluster *cluster, gint x1, gint max)
{
    LeavingLinkDir result;                  /* Préférence à retourner      */
    size_t left_points;                     /* Nombre de voix à gauche     */
    size_t left_straight;                   /* Nombre de voix à gauche bis */
    size_t right_points;                    /* Nombre de voix à droite     */
    size_t right_straight;                  /* Nombre de voix à droite bis */
    size_t i;                               /* Boucle de parcours #1       */
    const leaving_link_t *leaving;          /* Lien sortant à traiter      */
    LeavingLinkDir pref;                    /* Préférence du lien courant  */

    /* Analyse des différents liens */

    left_points = 0;
    left_straight = 0;
    right_points = 0;
    right_straight = 0;

    for (i = 0; i < cluster->ba_count; i++)
    {
        leaving = cluster->bottom_anchors[i];

        if (leaving->other->type == ILT_LOOP)
            continue;

        pref = get_leaving_link_direction(leaving, x1, max);

        if (pref == LLD_TO_LEFT)
        {
            left_points++;
            if (SHOULD_BE_VERTICAL(leaving))
                left_straight++;
        }
        else
        {
            right_points++;
            if (SHOULD_BE_VERTICAL(leaving))
                right_straight++;
        }

    }

    /* Décompte des points et élection du gagnant ! */

    if (left_points > right_points)
        result = LLD_TO_LEFT;

    else if (left_points < right_points)
        result = LLD_TO_RIGHT;

    else
    {
        if (left_straight > right_straight)
            result = LLD_TO_LEFT;

        else if (left_straight < right_straight)
            result = LLD_TO_RIGHT;

        else
            result = LLD_NO_PREF;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à manipuler.                    *
*                                                                             *
*  Description : Réorganise au besoin les liens sortants d'un bloc.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_sort_leaving_links(GGraphCluster *cluster)
{
    gint max;                               /* Borne pour la profondeur    */
    size_t lr_sep;                          /* Séparation gauche / droite  */
    leaving_link_t *leaving;                /* Lien sortant à traiter      */
    incoming_link_t *straight;              /* Lien entrant vertical ?     */
    size_t i;                               /* Boucle de parcours          */
    leaving_link_t **left;                  /* Liens à placer à gauche     */
    leaving_link_t **center;                /* Liens à placer au milieu    */
    leaving_link_t **right;                 /* Liens à placer à droite     */
    size_t left_count;                      /* Quantité de liens à gauche  */
    size_t center_count;                    /* Quantité de liens au milieu */
    size_t right_count;                     /* Quantité de liens à droite  */
    LeavingLinkDir pref;                    /* Préférence du lien courant  */
    gint x1;                                /* Abscisse de départ de lien  */

    /**
     * On n'intervient que s'il y a lieu de le faire...
     */

    if (cluster->ba_count < 2)
        goto done;

    /**
     * Détermination de la profondeur maximale, à partir des liens verticaux.
     *
     * Ces liens seront centraux, donc inutile de déterminer la direction
     * des autres liens passée une certaine profondeur verticale.
     */

    max = 0;
    lr_sep = cluster->ba_count;

    for (i = 0; i < cluster->ba_count; i++)
    {
        leaving = cluster->bottom_anchors[i];

        straight = g_graph_cluster_find_real_straight_incoming(leaving->other->owner, (size_t []){ 0 });

        if (straight == leaving->other)
        {
            /**
             * Il ne peut y avoir à priori qu'un seul lien vertical au départ
             * d'un bloc donné.
             */
            assert(max == 0);

            max = leaving->other->owner->alloc.y;
            lr_sep = i;

        }

    }

    if (max == 0)
        max = G_MAXINT;

    /**
     * Phase de réorganisation effective.
     */

    left = NULL;
    center = NULL;
    right = NULL;

    left_count = 0;
    center_count = 0;
    right_count = 0;

    /* Réorganisation des liens */

    for (i = 0; i < cluster->ba_count; i++)
    {
        leaving = cluster->bottom_anchors[i];


        if (i == lr_sep)
            pref = LLD_NO_PREF;

        else
        {
            x1 = compute_leaving_link_position(leaving);

            pref = get_leaving_link_direction(leaving, x1, max);

        }

        switch (pref)
        {
            case LLD_TO_LEFT:
                left = realloc(left, ++left_count * sizeof(leaving_link_t *));
                left[left_count - 1] = leaving;
                break;

            case LLD_NO_PREF:
                center = realloc(center, ++center_count * sizeof(leaving_link_t *));
                center[center_count - 1] = leaving;
                break;

            case LLD_TO_RIGHT:
                right = realloc(right, ++right_count * sizeof(leaving_link_t *));
                right[right_count - 1] = leaving;
                break;

        }

    }

    /* Sauvegarde du nouvel arrangement */

    assert((left_count + center_count + right_count) == cluster->ba_count);

    cluster->ba_count = 0;

    if (left != NULL)
    {
        qsort_r(left, left_count, sizeof(leaving_link_t *),
                (__compar_d_fn_t)cmp_leaving_links,
                (leaving_cmp_info_t []) { { .root = cluster, .dir = LLD_TO_LEFT } });

        for (i = 0; i < left_count; i++)
            cluster->bottom_anchors[cluster->ba_count++] = left[i];

        free(left);

    }

    if (center != NULL)
    {
        for (i = 0; i < center_count; i++)
            cluster->bottom_anchors[cluster->ba_count++] = center[i];

        free(center);

    }

    if (right != NULL)
    {
        qsort_r(right, right_count, sizeof(leaving_link_t *),
                (__compar_d_fn_t)cmp_leaving_links,
                (leaving_cmp_info_t []) { { .root = cluster, .dir = LLD_TO_RIGHT } });

        for (i = 0; i < right_count; i++)
            cluster->bottom_anchors[cluster->ba_count++] = right[i];

        free(right);

    }

    assert((left_count + center_count + right_count) == cluster->ba_count);

    for (i = 0; i < cluster->ba_count; i++)
        cluster->bottom_anchors[i]->index = i;

    /* Application de la nouvelle disposition */

    for (i = 0; i < cluster->ranks_count; i++)
        reorder_graph_rank_clusters(&cluster->ranks[i], cluster);

    for (i = 0; i < cluster->ranks_count; i++)
        visit_graph_rank(&cluster->ranks[i], g_graph_cluster_reset_allocation);

    for (i = 0; i < cluster->ranks_count; i++)
        offset_x_graph_rank(&cluster->ranks[i], cluster->alloc.x);

    g_graph_cluster_dispatch_x(cluster);

    g_graph_cluster_set_y(cluster, cluster->alloc.y);

 done:

    for (i = 0; i < cluster->ranks_count; i++)
        visit_graph_rank(&cluster->ranks[i], g_graph_cluster_sort_leaving_links);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à consulter.                    *
*                root    = ensemble dont s'extraire.                          *
*                pos     = ordonnée minimale en bout. [OUT]                   *
*                                                                             *
*  Description : Calcule les ordonnées extrèmes atteintes via liens sortants. *
*                                                                             *
*  Retour      : false si une incapacité de détermination a été rencontrée.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_graph_cluster_compute_min_y_target(const GGraphCluster *cluster, const GGraphCluster *root, gint *pos)
{
    bool result;                            /* Bilan à renvoyer            */
    size_t i;                               /* Boucle de parcours #1       */
    const leaving_link_t *leaving;          /* Lien sortant à traiter      */
    bool stop;                              /* Prépare la fin de parcours  */
    GGraphCluster *iter;                    /* Boucle de parcours #2       */
    gint y;                                 /* Ordonnée rencontrée         */

    result = false;

    for (i = 0; i < cluster->ba_count; i++)
    {
        leaving = cluster->bottom_anchors[i];

        if (leaving->other->type == ILT_LOOP)
            continue;

        stop = leaving->cluster_exit;

        /* Validation d'une sortie du cluster d'origine */

        if (stop)
        {
            for (iter = leaving->other->owner; iter != NULL; iter = iter->owner)
                if (iter == root)
                    break;

            stop = (iter == NULL);

        }

        /* Poursuite du lien ? */

        if (stop)
        {
            y = leaving->other->owner->alloc.y;

            if (y < *pos)
            {
                *pos = y;
                result = true;
            }

        }

        else
            result |= g_graph_cluster_compute_min_y_target(leaving->other->owner, root, pos);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à analyser.                     *
*                origin  = cluster d'origine à considérer.                    *
*                                                                             *
*  Description : Retrouve s'il existe un lien entrant vers un bloc d'origine. *
*                                                                             *
*  Retour      : Lien vers le bloc d'origine trouvé ou NULL.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const leaving_link_t *g_graph_cluster_has_origin(const GGraphCluster *cluster, const GGraphCluster *origin)
{
    const leaving_link_t *result;           /* Lien trouvé à renvoyer      */
    size_t i;                               /* Boucle de parcours          */

    result = NULL;

    for (i = 0; i < cluster->ta_count && result == NULL; i++)
        if (cluster->top_anchors[i]->other->owner == origin)
            result = cluster->top_anchors[i]->other;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = premier graphique de blocs à analyser.             *
*                other   = second graphique de blocs à analyser.              *
*                origin  = cluster d'origine à considérer.                    *
*                                                                             *
*  Description : Compare deux clusters selon un de leurs liens d'origine.     *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int g_graph_cluster_compare_by_origin(const GGraphCluster **cluster, const GGraphCluster **other, const GGraphCluster *origin)
{
    int result;                             /* Bilan à renvoyer            */
    const leaving_link_t *leaving;          /* Accès au lien manipulé      */
    gint x0;                                /* Première abscisse à traiter */
    gint x1;                                /* Seconde abscisse à traiter  */

    leaving = g_graph_cluster_has_origin(*cluster, origin);

    assert(leaving != NULL);

    x0 = compute_leaving_link_position(leaving);

    leaving = g_graph_cluster_has_origin(*other, origin);

    assert(leaving != NULL);

    x1 = compute_leaving_link_position(leaving);

    if (x0 < x1)
        result = -1;

    else if (x0 > x1)
        result = 1;

    else
        result = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à manipuler.                    *
*                                                                             *
*  Description : Réorganise au besoin les liens entrants d'un bloc.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_sort_incoming_links(GGraphCluster *cluster)
{
    size_t i;                               /* Boucle de parcours          */

    qsort(cluster->top_anchors, cluster->ta_count, sizeof(incoming_link_t *), (__compar_fn_t)cmp_incoming_links);

    for (i = 0; i < cluster->ranks_count; i++)
        sort_graph_rank_incoming_links(&cluster->ranks[i]);

    sort_incoming_links_for_vspace_manager(&cluster->self);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster  = graphique de blocs à consulter.                   *
*                incoming = adresse de l'autre bout du lien concerné.         *
*                                                                             *
*  Description : Retrouve l'indice d'un lien entrant donné pour un bloc.      *
*                                                                             *
*  Retour      : Indice à priori toujours valide.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_graph_cluster_find_incoming_link(const GGraphCluster *cluster, const leaving_link_t *leaving)
{
    size_t result;                          /* Indice à retourner          */

    for (result = 0; result < cluster->ta_count; result++)
        if (cluster->top_anchors[result]->other == leaving)
            break;

    assert(result < cluster->ta_count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à actualiser.                   *
*                                                                             *
*  Description : Réordonne les blocs de départ de boucle au mieux.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_reorder_loop_blocks(GGraphCluster *cluster)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < cluster->ranks_count; i++)
        reorder_graph_rank_loop_blocks(&cluster->ranks[i]);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à actualiser.                   *
*                link    = lien à déplacer.                                   *
*                left    = emplacement final : à gauche ou à droite ?         *
*                                                                             *
*  Description : Réordonne le départ des liens en entrée de bloc.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_reorder_link_origins(GGraphCluster *cluster, bool left)
{
    size_t i;                               /* Boucle de parcours #1       */
    leaving_link_t *origin;                 /* Autre extrémité du lien     */
    GGraphCluster *parent;                  /* Parent du bloc courant      */
    size_t k;                               /* Boucle de parcours #2       */

    for (i = 0; i < cluster->ta_count; i++)
    {
        origin = cluster->top_anchors[i]->other;
        parent = origin->owner;

        for (k = 0; k < parent->ba_count; k++)
            if (parent->bottom_anchors[k] == origin)
                break;

        assert(k < parent->ba_count);

        if (left)
        {
            memmove(&parent->bottom_anchors[1], &parent->bottom_anchors[0],
                    k * sizeof(leaving_link_t *));

            parent->bottom_anchors[0] = origin;

        }
        else
        {
            memmove(&parent->bottom_anchors[k], &parent->bottom_anchors[k + 1],
                    (parent->ba_count - k - 1) * sizeof(leaving_link_t *));

            parent->bottom_anchors[parent->ba_count - 1] = origin;

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à actualiser.                   *
*                offset  = décalage à appliquer.                              *
*                                                                             *
*  Description : Décale vers la droite un ensemble de blocs basiques.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_offset_x(GGraphCluster *cluster, gint offset)
{
    size_t i;                               /* Boucle de parcours          */
    cluster->alloc.x += offset;

    for (i = 0; i < cluster->ranks_count; i++)
        offset_x_graph_rank(&cluster->ranks[i], offset);

    offset_x_vspace_manager(&cluster->self, offset);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à actualiser.                   *
*                base    = position ordonnée à appliquer.                     *
*                                                                             *
*  Description : Décale vers le bas un ensemble de blocs basiques.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_set_y(GGraphCluster *cluster, gint base)
{
    size_t i;                               /* Boucle de parcours          */

    cluster->alloc.y = base;

    base += cluster->alloc.height;

    for (i = 0; i < cluster->ranks_count; i++)
        set_y_for_graph_rank(&cluster->ranks[i], &base);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = encapsulation à consulter.                         *
*                                                                             *
*  Description : Fournit le bloc de code principal du groupe.                 *
*                                                                             *
*  Retour      : Bloc de code associé.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GCodeBlock *g_graph_cluster_get_block(GGraphCluster *cluster)
{
    GCodeBlock *result;                     /* Bloc de code à retourner    */

    result = cluster->block;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = encapsulation à consulter.                         *
*                                                                             *
*  Description : Fournit le composant graphique principal du groupe.          *
*                                                                             *
*  Retour      : Composant graphique principal utilisé.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *g_graph_cluster_get_widget(GGraphCluster *cluster)
{
    GtkWidget *result;                      /* Composant à retourner       */

    result = cluster->display;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = encapsulation à consulter.                         *
*                alloc   = emplacement idéal pour l'affichage. [OUT]          *
*                                                                             *
*  Description : Fournit l'emplacement prévu pour un chef de file de blocs.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_get_allocation(const GGraphCluster *cluster, GtkAllocation *alloc)
{
    *alloc = cluster->alloc;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = encapsulation à consulter.                         *
*                alloc   = emplacement idéal pour l'affichage. [OUT]          *
*                                                                             *
*  Description : Détermine l'emplacement requis d'un ensemble de blocs.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_compute_needed_alloc(const GGraphCluster *cluster, GtkAllocation *alloc)
{
    size_t i;                               /* Boucle de parcours #1       */
    GGraphCluster *start;                   /* Départ de boucle extérieure */
    GGraphCluster *container;               /* Arrivée de boucle extérieure*/
    size_t k;                               /* Boucle de parcours #2       */

    *alloc = cluster->alloc;

    for (i = 0; i < cluster->ranks_count; i++)
        compute_graph_rank_needed_alloc(&cluster->ranks[i], (i + 1) == cluster->ranks_count, alloc);

    for (i = 0; i < cluster->ta_count; i++)
        if (cluster->top_anchors[i]->type == ILT_LOOP)
        {
            start = cluster->top_anchors[i]->other->owner;

            container = start->owner;
            assert(container != NULL);

            for (k = 0; k < container->ranks_count; k++)
                if (has_graph_rank_cluster(&container->ranks[k], start))
                {
                    compute_vspace_manager_needed_alloc(&container->ranks[k].vspaces, true, alloc);
                    break;
                }

            assert(k < container->ranks_count);

        }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = encapsulation à traiter.                           *
*                display = support de destination finale.                     *
*                                                                             *
*  Description : Dispose chaque noeud sur la surface de destination donnée.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_place(GGraphCluster *cluster, GtkGraphDisplay *display)
{
    size_t i;                               /* Boucle de parcours #1       */
    size_t j;                               /* Boucle de parcours #2       */

    g_object_ref(G_OBJECT(cluster->display));
    gtk_graph_display_put(display, cluster->display, &cluster->alloc);

    for (i = 0; i < cluster->ta_count; i++)
    {
        g_object_ref(G_OBJECT(cluster->top_anchors[i]->edge));
        gtk_graph_display_add_edge(display, cluster->top_anchors[i]->edge);
    }

    for (i = 0; i < cluster->ranks_count; i++)
        for (j = 0; j < cluster->ranks[i].count; j++)
            g_graph_cluster_place(cluster->ranks[i].clusters[j], display);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à consulter.                    *
*                index   = indice du lien à considérer.                       *
*                half    = moitié du nombre de liens en présence.             *
*                odd     = le nombre de liens considérés est-il impair ?      *
*                                                                             *
*  Description : Calcule l'abscisse d'un lien pour un bloc.                   *
*                                                                             *
*  Retour      : Abscisse à attribuer au lien.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint _g_graph_cluster_compute_link_position(const GGraphCluster *cluster, size_t index, size_t half, bool odd)
{
    gint result;                            /* Position à retourner        */
    gint mid_x;                             /* Abscisse centrale           */

    mid_x = cluster->alloc.x + (cluster->alloc.width / 2);

    if (odd)
    {
        if (index < half)
            result = mid_x - (half - index) * LINK_MARGIN;

        else if (index == half)
            result = mid_x;

        else
            result = mid_x + (index - half) * LINK_MARGIN;

    }

    else
    {
        if (index < half)
            result = mid_x - LINK_MARGIN / 2 - (half - index - 1) * LINK_MARGIN;

        else
            result = mid_x + LINK_MARGIN / 2 + (index - half) * LINK_MARGIN;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à consulter.                    *
*                index   = indice du lien à considérer.                       *
*                                                                             *
*  Description : Calcule l'abscisse d'un lien à son départ d'un bloc.         *
*                                                                             *
*  Retour      : Abscisse à attribuer à un départ de lien.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint g_graph_cluster_compute_leaving_link_position(const GGraphCluster *cluster, size_t index)
{
    gint result;                            /* Position à retourner        */
    size_t half;                            /* Indice de répartition égale */
    bool odd;                               /* Partité du nombre de liens  */

    assert(index < cluster->ba_count);

    half = cluster->ba_count / 2;

    odd = (cluster->ba_count % 2 == 1);

    result = _g_graph_cluster_compute_link_position(cluster, index, half, odd);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à consulter.                    *
*                index   = indice du lien à considérer.                       *
*                                                                             *
*  Description : Calcule l'abscisse d'un lien à son arrivée à un bloc.        *
*                                                                             *
*  Retour      : Abscisse à attribuer à une arrivée de lien.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint g_graph_cluster_compute_incoming_link_position(const GGraphCluster *cluster, size_t index)
{
    gint result;                            /* Position à retourner        */
    size_t half;                            /* Indice de répartition égale */
    bool odd;                               /* Partité du nombre de liens  */

    assert(index < cluster->ta_count);

    half = cluster->ta_count / 2;

    odd = (cluster->ta_count % 2 == 1);

    result = _g_graph_cluster_compute_link_position(cluster, index, half, odd);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à actualiser.                   *
*                margin  = espace nécessaire à gauche aux liens de boucle.    *
*                                                                             *
*  Description : Ajoute une marge à gauche pour les liens remontants.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_cluster_insert_left_margin(GGraphCluster *cluster, gint margin)
{
    GGraphCluster *container;               /* Parent direct à décaler     */
    size_t i;                               /* Boucle de parcours          */
    size_t straight_index;                  /* Indice du lien vertical     */

    if (margin > 0)
    {
        /**
         * Si la routine est une boucle sans fin,
         * alors la boucle peut renvoyer vers le premier bloc.
         */
        if (cluster->owner != NULL)
        {
            container = cluster->owner;

            /**
             * On recherche le plus haut propritétaire bénéficiant d'une chaîne
             * de liens directs et droits, histoire de transmettre le décalage
             * et de garder ces liens bien verticaux.
             */
            while (container->owner != NULL)
            {
                if (container->owner->ba_count == 0)
                    break;

                for (i = 0; i < container->owner->ba_count; i++)
                    if (SHOULD_BE_VERTICAL(container->owner->bottom_anchors[i]))
                    {
                        straight_index = i;
                        break;
                    }

                if (i == container->owner->ba_count)
                    break;

                if (straight_index != *container->parent_index)
                    break;

                container = container->owner;

            }

            g_graph_cluster_offset_x(container, margin);

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à actualiser.                   *
*                                                                             *
*  Description : Détermine les abscisses des liens de boucle en place.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_compute_loop_link_x_positions(GGraphCluster *cluster)
{
    GtkAllocation alloc;                    /* Emplacement à faire évoluer */
    gint margin;                            /* Marge à gauche éventuelle   */
    size_t i;                               /* Boucle de parcours #1       */
    GGraphCluster *start;                   /* Départ de boucle extérieure */
    GGraphCluster *container;               /* Arrivée de boucle extérieure*/
    size_t k;                               /* Boucle de parcours #2       */

    /* Propagation des déterminations */

    alloc = cluster->alloc;

    for (i = 0; i < cluster->ranks_count; i++)
    {
        compute_graph_rank_needed_alloc(&cluster->ranks[i], (i + 1) == cluster->ranks_count, &alloc);

        margin = compute_loop_link_x_positions_with_graph_rank(&cluster->ranks[i], &alloc);

        g_graph_cluster_insert_left_margin(cluster, margin);

    }

    /* Liens de boucle (#1) */

    g_graph_cluster_compute_needed_alloc(cluster, &alloc);

    margin = compute_loop_link_x_with_vspace_manager(&cluster->self, &alloc, false);

    /* Liens de boucle (#2) */

    for (i = 0; i < cluster->ta_count; i++)
        if (cluster->top_anchors[i]->type == ILT_LOOP)
        {
            start = cluster->top_anchors[i]->other->owner;

            container = start->owner;
            assert(container != NULL);

            for (k = 0; k < container->ranks_count; k++)
                if (has_graph_rank_cluster(&container->ranks[k], start))
                {
                    margin += compute_loop_link_x_with_vspace_manager(&container->ranks[k].vspaces, &alloc, true);
                    break;
                }

            assert(k < container->ranks_count);

        }

    g_graph_cluster_insert_left_margin(cluster, margin);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à actualiser.                   *
*                                                                             *
*  Description : Détermine les abscisses de tous les liens en place.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_cluster_compute_link_x_positions(GGraphCluster *cluster)
{
    gint mid_x;                             /* Abscisse centrale           */
    size_t i;                               /* Boucle de parcours #1       */
    size_t half;                            /* Indice de répartition égale */
    GdkPoint *pt;                           /* Point à actualiser          */
    size_t j;                               /* Boucle de parcours #2       */

    mid_x = cluster->alloc.x + (cluster->alloc.width / 2);

    /* Du côté des départs... */

    if (cluster->ba_count > 0)
        for (i = 0; i < cluster->ba_count; i++)
        {
            pt = &cluster->bottom_anchors[i]->start[0];

            pt->x = g_graph_cluster_compute_leaving_link_position(cluster, i);

            cluster->bottom_anchors[i]->start[1].x = pt->x;

        }

    /* Du côté des arrivées... */

    if (cluster->ta_count > 0)
    {
        half = cluster->ta_count / 2;

        if (cluster->ta_count % 2 == 1)
        {
            for (i = half; i > 0; i--)
            {
                pt = &cluster->top_anchors[i - 1]->end[1];

                pt->x = mid_x - (half - i + 1) * LINK_MARGIN;

            }

            cluster->top_anchors[half]->end[1].x = mid_x;

            for (i = half + 1; i < cluster->ta_count; i++)
            {
                pt = &cluster->top_anchors[i]->end[1];

                pt->x = mid_x + (i - half) * LINK_MARGIN;

            }

        }

        else
        {
            for (i = half; i > 0; i--)
            {
                pt = &cluster->top_anchors[i - 1]->end[1];

                pt->x = mid_x - LINK_MARGIN / 2 - (half - i) * LINK_MARGIN;

            }

            for (i = half; i < cluster->ta_count; i++)
            {
                pt = &cluster->top_anchors[i]->end[1];

                pt->x = mid_x + LINK_MARGIN / 2 + (i - half) * LINK_MARGIN;

            }

        }

    }

    for (i = 0; i < cluster->ta_count; i++)
        cluster->top_anchors[i]->end[0].x = cluster->top_anchors[i]->end[1].x;

    /* Propagation des déterminations */

    for (i = 0; i < cluster->ranks_count; i++)
        for (j = 0; j < cluster->ranks[i].count; j++)
            g_graph_cluster_compute_link_x_positions(cluster->ranks[i].clusters[j]);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à traiter.                      *
*                                                                             *
*  Description : Réserve de l'espace vertical pour les lignes horizontales.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_cluster_book_hspace_for_links(GGraphCluster *cluster)
{
    size_t i;                               /* Boucle de parcours #1       */
    graph_rank_t *rank;                     /* Rangée à manipuler          */
    size_t j;                               /* Boucle de parcours #2       */
    GGraphCluster *sub;                     /* Bloc inférieur à manipuler  */
    size_t k;                               /* Boucle de parcours #3       */
    gint x1;                                /* Abscisse de départ de lien  */
    gint x2;                                /* Abscisse d'arrivée de lien  */
    hspace_booking *new;                    /* Nouvelle réservation        */

    for (i = 0; i < cluster->ranks_count; i++)
    {
        rank = &cluster->ranks[i];

        /* Enregistrement des besoins */

        for (j = 0; j < rank->count; j++)
        {
            sub = rank->clusters[j];

            for (k = 0; k < sub->ta_count; k++)
            {
                g_graph_edge_get_x_borders(sub->top_anchors[k]->edge, &x1, &x2);

                new = create_hspace_booking(x1);
                sub->top_anchors[k]->hslot = &new->index;

                if (x1 > x2)
                    rank->right2left = qinsert(rank->right2left, &rank->r2l_count,
                                               sizeof(hspace_booking *),
                                               (__compar_fn_t)cmp_hspace_booking_r2l, &new);

                else if (x1 < x2)
                    rank->left2right = qinsert(rank->left2right, &rank->l2r_count,
                                               sizeof(hspace_booking *),
                                               (__compar_fn_t)cmp_hspace_booking_l2r, &new);

                else
                    sub->top_anchors[k]->hslot = NULL;

            }

        }

        /* Définition des couches */

        for (j = 0; j < rank->r2l_count; j++)
            rank->right2left[j]->index = j;

        for (j = 0; j < rank->l2r_count; j++)
            rank->left2right[j]->index = j;

        /* Propagation des déterminations */

        for (j = 0; j < rank->count; j++)
            g_graph_cluster_book_hspace_for_links(rank->clusters[j]);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à actualiser.                   *
*                                                                             *
*  Description : Détermine les ordonnées de tous les liens en place.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_graph_cluster_compute_link_y_positions(GGraphCluster *cluster)
{
    gint y;                                 /* Ordonnée d'application      */
    size_t i;                               /* Boucle de parcours          */
    incoming_link_t *incoming;              /* Raccourci pour le confort   */
    GtkAllocation alloc;                    /* Emplacement à faire évoluer */

    /* Du côté des départs... */

    if (cluster->ba_count > 0)
    {
        y = cluster->alloc.y + cluster->alloc.height;

        for (i = 0; i < cluster->ba_count; i++)
            cluster->bottom_anchors[i]->start[0].y = y;

    }

    /* Du côté des arrivées... */

    if (cluster->ta_count > 0)
    {
        y = cluster->alloc.y;

        for (i = 0; i < cluster->ta_count; i++)
        {
            incoming = cluster->top_anchors[i];

            incoming->end[1].y = y;

            incoming->end[0].y = incoming->end[1].y - VERTICAL_MARGIN;

            if (incoming->hslot != NULL)
                incoming->end[0].y -= *incoming->hslot * LINK_MARGIN;

            incoming->other->start[1].y = incoming->end[0].y;

        }

    }

    /* Propagation des déterminations */

    alloc = cluster->alloc;

    for (i = 0; i < cluster->ranks_count; i++)
    {
        compute_graph_rank_needed_alloc(&cluster->ranks[i], (i + 1) == cluster->ranks_count, &alloc);
        compute_loop_link_with_graph_rank(&cluster->ranks[i], &alloc);
    }

    /* Définition des liens de boucle */

    compute_loop_link_y_with_vspace_manager(&cluster->self, &cluster->alloc);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à consulter.                    *
*                                                                             *
*  Description : Applique les positions calculées pour chaque lien graphique. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_graph_cluster_resolve_links(const GGraphCluster *cluster)
{
    size_t i;                               /* Boucle de parcours #1       */
    size_t j;                               /* Boucle de parcours #2       */

    for (i = 0; i < cluster->ta_count; i++)
        g_graph_edge_resolve(cluster->top_anchors[i]->edge);

    for (i = 0; i < cluster->ranks_count; i++)
        for (j = 0; j < cluster->ranks[i].count; j++)
            g_graph_cluster_resolve_links(cluster->ranks[i].clusters[j]);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à analyser.                     *
*                block   = bloc de code à retrouver.                          *
*                                                                             *
*  Description : Recherche le groupe de blocs avec un bloc donné comme chef.  *
*                                                                             *
*  Retour      : Groupe trouvé ou NULL en cas d'échec.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGraphCluster *g_graph_cluster_find_by_block(GGraphCluster *cluster, GCodeBlock *block)
{
    GGraphCluster *result;                  /* Trouvaille à retourner      */
    size_t i;                               /* Boucle de parcours          */

    if (cluster->block == block)
    {
        result = cluster;
        g_object_ref(G_OBJECT(result));
    }

    else
    {
        result = NULL;

        for (i = 0; i < cluster->ranks_count && result == NULL; i++)
            result = find_cluster_by_block_in_graph_rank(&cluster->ranks[i], block);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à analyser.                     *
*                widget  = composant graphique à retrouver.                   *
*                                                                             *
*  Description : Recherche le groupe de blocs avec un composant comme chef.   *
*                                                                             *
*  Retour      : Groupe trouvé ou NULL en cas d'échec.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGraphCluster *g_graph_cluster_find_by_widget(GGraphCluster *cluster, GtkWidget *widget)
{
    GGraphCluster *result;                  /* Trouvaille à retourner      */
    size_t i;                               /* Boucle de parcours          */

    if (cluster->display == widget)
    {
        result = cluster;
        g_object_ref(G_OBJECT(result));
    }

    else
    {
        result = NULL;

        for (i = 0; i < cluster->ranks_count && result == NULL; i++)
            result = find_cluster_by_widget_in_graph_rank(&cluster->ranks[i], widget);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à analyser.                     *
*                list    = liste en cours de constitution. [OUT]              *
*                count   = taille de cette liste. [OUT]                       *
*                                                                             *
*  Description : Collecte tous les chefs de file de blocs de code.            *
*                                                                             *
*  Retour      : Liste de graphiques de blocs rassemblés.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGraphCluster **g_graph_cluster_collect(GGraphCluster *cluster, GGraphCluster **list, size_t *count)
{
    GGraphCluster **result;                 /* Liste complétée à renvoyer  */
    size_t i;                               /* Boucle de parcours          */

    result = realloc(list, ++(*count) * sizeof(GGraphCluster *));

    result[*count - 1] = cluster;
    g_object_ref(G_OBJECT(cluster));

    for (i = 0; i < cluster->ranks_count; i++)
        result = collect_graph_ranks_clusters(&cluster->ranks[i], result, count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cluster = graphique de blocs à analyser.                     *
*                list    = liste en cours de constitution. [OUT]              *
*                count   = taille de cette liste. [OUT]                       *
*                                                                             *
*  Description : Collecte tous les liens de chefs de file de blocs de code.   *
*                                                                             *
*  Retour      : Liste de liens graphiques de blocs rassemblés.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGraphEdge **g_graph_cluster_collect_edges(GGraphCluster *cluster, GGraphEdge **list, size_t *count)
{
    GGraphEdge **result;                    /* Liste complétée à renvoyer  */
    size_t i;                               /* Boucle de parcours          */

    result = realloc(list, (*count + cluster->ta_count) * sizeof(GGraphEdge *));

    for (i = 0; i < cluster->ta_count; i++)
    {
        result[*count + i] = cluster->top_anchors[i]->edge;
        g_object_ref(G_OBJECT(result[*count + i]));
    }

    *count += cluster->ta_count;

    for (i = 0; i < cluster->ranks_count; i++)
        result = collect_graph_ranks_cluster_edges(&cluster->ranks[i], result, count);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           CALCUL DE REPARTITION DE BLOCS                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : binary      = binaire charger dont le code est à représenter.*
*                list        = ensemble de blocs basiques à manipuler.        *
*                index       = indice du bloc principal à mettre en place.    *
*                highlighted = gestionnaire de surbrillance pour segments.    *
*                pending     = liste de blocs restant à traiter. [OUT]        *
*                all         = table regroupant tous les groupes créés.       *
*                                                                             *
*  Description : Met en place un ensemble de blocs sous forme graphique.      *
*                                                                             *
*  Retour      : Ensemble de blocs mis en place.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GGraphCluster *setup_graph_clusters(GLoadedBinary *binary, const GBlockList *list, size_t index, segcnt_list *highlighted, pending_blocks *pending, GHashTable *all)
{
    GGraphCluster *result;                  /* Instance nouvelle à renvoyer*/
    GCodeBlock *block;                      /* Bloc à manipuler            */
#ifndef NDEBUG
    gboolean new;                           /* Bloc déjà traité ?          */
#endif
    size_t dcount;                          /* Nombre de liens de dest.    */
    block_link_t *links;                    /* Liens associés au bloc      */
    size_t i;                               /* Boucle de parcours #1       */
    block_link_t *dest;                     /* Bloc visé par un autre      */
    size_t j;                               /* Boucle de parcours #2       */
    bool changed;                           /* Un ajout a été effectué ?   */
    const bitfield_t *dominators;           /* Blocs dominant ce même bloc */
    size_t next;                            /* Indice du prochain bloc     */
    GGraphCluster *sub;                     /* Sous-ensemble à intégrer    */

    block = g_block_list_get_block(list, index);

    result = g_graph_cluster_new(block, highlighted, binary);

#ifndef NDEBUG
    new = g_hash_table_insert(all, block, result);
    assert(new);
#else
    g_hash_table_insert(all, block, result);
#endif

    /* Détermination des blocs suivants */

    links = g_code_block_get_destinations(block, &dcount);

    for (i = 0; i < dcount; i++)
    {
        dest = &links[i];

        switch (dest->type)
        {
            case ILT_EXEC_FLOW:
            case ILT_JUMP:
            case ILT_CASE_JUMP:
            case ILT_JUMP_IF_TRUE:
            case ILT_JUMP_IF_FALSE:

                for (j = 0; j < pending->count; j++)
                    if (pending->list[j] == dest->linked)
                        break;

                if (j == pending->count)
                {
                    /**
                     * Il faut vérifier ici si la destination n'a pas déjà été
                     * empruntée, sauf peine de faire réagir l'assertion plus
                     * haut au moment de l'insertion.
                     *
                     * Le type de code à problème est le suivant :
                     *
                     *    ...
                     *    if (...)
                     *        ...
                     *    ...
                     *
                     * Le code suivant le bloc conditionnel a deux origines,
                     * qui vont chacune poursuivre le traitement vers ce code
                     * commun.
                     *
                     * Et comme les origines ne sont pas dominantes, on utilise
                     * la table globale.
                     */

                    if (!g_hash_table_contains(all, dest->linked))
                    {
                        g_object_ref(G_OBJECT(dest->linked));

                        assert((pending->count + 1) < g_block_list_count_blocks(list));
                        pending->list[pending->count++] = dest->linked;

                    }

                }

                break;

            default:
                break;

        }

        unref_block_link(dest);

    }

    if (links != NULL)
        free(links);

    g_object_unref(G_OBJECT(block));

    /* Intégration de tous les blocs en attente */

    do
    {
        changed = false;

        for (i = 0; i < pending->count && !changed; i++)
        {
            block = pending->list[i];
            dominators = g_code_block_get_domination(block);

            if (test_in_bit_field(dominators, index))
            {
                /* Dépilement */

                changed = true;

                if ((i + 1) < pending->count)
                    memmove(&pending->list[i], &pending->list[i + 1],
                            (pending->count - i - 1) * sizeof(GCodeBlock *));

                pending->count--;

                /* Intégration */

                next = g_code_block_get_index(block);
                assert(next < g_block_list_count_blocks(list));

                sub = setup_graph_clusters(binary, list, next, highlighted, pending, all);

                g_graph_cluster_add_sub(result, sub);

            }

            g_object_ref(G_OBJECT(block));

        }

    }
    while (changed);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : binary      = binaire charger dont le code est à représenter.*
*                list        = ensemble de blocs basiques à manipuler.        *
*                highlighted = gestionnaire de surbrillance pour segments.    *
*                                                                             *
*  Description : Construit un graphique à partir de blocs basiques.           *
*                                                                             *
*  Retour      : Structure mise en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGraphCluster *bootstrap_graph_cluster(GLoadedBinary *binary, const GBlockList *list, segcnt_list *highlighted)
{
    GGraphCluster *result;                  /* Structure à retourner       */
    GHashTable *all;                        /* Collection des créations    */
    size_t count;                           /* Taille de la liste de blocs */
    pending_blocks *pending;                /* Suivi des blocs à traiter   */
    bool loop;                              /* Ordre de relance            */
    GtkAllocation needed;                   /* Taille requise              */

    /* Création des éléments */

    all = g_hash_table_new(NULL, NULL);

    count = g_block_list_count_blocks(list);

    pending = malloc(sizeof(pending_blocks) + count * sizeof(GCodeBlock *));

    pending->count = 0;

    result = setup_graph_clusters(binary, list, 0, highlighted, pending, all);

    free(pending);

    g_graph_cluster_define_links(result, all);

    g_graph_cluster_setup_links(result);

    /* Positionnements dans l'espace */

    g_graph_cluster_dispatch_x(result);

    /**
     * Une première passe d'organisation horizontale est réalisée.
     *
     * A ce point, en proposant des emplacements verticaux en complément,
     * on est en mesure de déterminer si les liens qui sortent de leur
     * conteneur vont en croiser d'autres.
     *
     * On réorganise ainsi au besoin les différents blocs pour éviter ce cas
     * de figure. Les blocs sont replacés à une nouvelle position horizontale
     * au besoin.
     *
     * Une illustration concrête de la nécessité de cette opération est la
     * fonction test_ite_2() de la suite de tests.
     */

    g_graph_cluster_set_y(result, 0);

    g_graph_cluster_sort_leaving_links(result);

    /**
     * Un effet de bord de l'organisation en rangs de profondeur est que, dans
     * une situation où les blocs sont placés de part et d'autre d'un lien vertical,
     * ce lien vertical n'a d'influence que sur les blocs du même cluster.
     *
     * Les positions sont en effet déterminés via la fonction g_graph_cluster_dispatch_x().
     *
     * Si un bloc d'un rang a des enfants qui ne sont pas dominés, la taille de
     * ces enfants n'est pas prise en compte pour s'assurer du respect du lien
     * vertical.
     *
     * On calcule ici un décalage de compensation. Et comme l'opération est de
     * nature à réorganiser les blocs, on itère le nombre de fois nécessaires.
     */

    do
    {
        g_graph_cluster_reset_allocation(result);

        g_graph_cluster_dispatch_x(result);

        g_graph_cluster_set_y(result, 0);

        loop = g_graph_cluster_dispatch_define_extra_offset(result);

    }
    while (loop);

    /**
     * A ce point, tous les blocs sont placés.
     * On est donc en mesure de réorganiser les points d'arrivée
     * des liens afin d'éviter les croisements : un lien qui vient
     * de la gauche ne doit pas arriver tout à droite !
     *
     * Cette consigne est valable pour les liens de boucle également, dont
     * l'origine est toujours dans un bloc inférieur au bloc de destination.
     * Le premier étant traité après le second, cela oblige à appeler
     * g_graph_cluster_dispatch_x() au moins deux fois donc, car on ne peut
     * effectuer le tri des liens au début de cette fonction comme c'était
     * fait dans les premières versions du code.
     */

    g_graph_cluster_sort_incoming_links(result);

    /**
     * Même s'ils ne sont pas encore entièrement tracés, les liens de boucle
     * voient désormais leurs positions d'arrivée et de départ définies.
     *
     * On sait si lesdits liens partent vers la gauche ou la droite.
     *
     * On est donc en mesure de réorganiser latéralement les blocs
     * pour tirer les traits horizontaux au plus court !
     */

    g_graph_cluster_reset_allocation(result);

    g_graph_cluster_reorder_loop_blocks(result);

    g_graph_cluster_dispatch_x(result);

    g_graph_cluster_sort_incoming_links(result);

    /**
     * Placement horizontal définitif.
     */

    g_graph_cluster_reset_allocation(result);

    g_graph_cluster_dispatch_x(result);

    /* Réajustement vers la droite */

    g_graph_cluster_compute_needed_alloc(result, &needed);

    g_graph_cluster_offset_x(result, -needed.x);

    /* Application finale sur les liens */

    /**
     * Comme g_graph_cluster_offset_x() n'agit que sur les abscisses et non sur
     * les largeurs, on ne peut pas définir les positions pour les liens de boucle
     * en amont et les décaler ensuite.
     *
     * Et comme la mise en place de ce type de lien peut déplacer le bloc parent,
     * ses repères pour ses propres liens peuvent être décaler. Il faut ainsi
     * une procédure distincte de g_graph_cluster_compute_link_x_positions().
     *
     * On définit donc l'abscisse de ces liens ici, en redécalant encore un peu
     * les blocs au besoin.
     */

    g_graph_cluster_compute_loop_link_x_positions(result);

    g_graph_cluster_compute_link_x_positions(result);

    g_graph_cluster_book_hspace_for_links(result);

    g_graph_cluster_set_y(result, 0);

    g_graph_cluster_compute_link_y_positions(result);

    g_graph_cluster_resolve_links(result);

    /* Sortie propre */

    g_hash_table_unref(all);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : root  = graphique de blocs à analyser.                       *
*                count = taille de cette liste. [OUT]                         *
*                                                                             *
*  Description : Collecte tous les chefs de file de blocs de code.            *
*                                                                             *
*  Retour      : Liste de graphiques de blocs rassemblés.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGraphCluster **collect_graph_clusters(GGraphCluster *root, size_t *count)
{
    GGraphCluster **result;                 /* Liste à retourner           */

    result = NULL;
    *count = 0;

    result = g_graph_cluster_collect(root, result, count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : root  = graphique de blocs à analyser.                       *
*                count = taille de cette liste. [OUT]                         *
*                                                                             *
*  Description : Collecte tous les liens de chefs de file de blocs de code.   *
*                                                                             *
*  Retour      : Liste de liens graphiques de blocs rassemblés.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGraphEdge **collect_graph_cluster_edges(GGraphCluster *root, size_t *count)
{
    GGraphEdge **result;                    /* Liste à retourner           */

    result = NULL;
    *count = 0;

    result = g_graph_cluster_collect_edges(root, result, count);

    return result;

}
