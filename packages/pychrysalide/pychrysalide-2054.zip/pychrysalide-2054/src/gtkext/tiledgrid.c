
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tiledgrid.c - composant d'affichage avec des chemins vers les composants contenus
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include "tiledgrid.h"


#include <assert.h>
#include <ctype.h>
#include <malloc.h>
#include <string.h>


#include "../core/logs.h"



/* -------------------------- GESTION DES TUILES AFFICHEES -------------------------- */


/* Informations concernant une tuile */
typedef struct _grid_tile_t
{
    struct _grid_tile_t *parent;            /* Tuile parente               */

    GtkWidget *widget;                      /* Support d'affichage         */

    char *path;                             /* Chemin d'accès              */

    struct _grid_tile_t *children[2];       /* Tuiles encastrées ou 2xNULL */

} grid_tile_t;


#define IS_LEAF_TILE(t)                                 \
    ({                                                  \
        bool __result;                                  \
        __result = GTK_IS_DOCK_STATION((t)->widget);    \
        assert(__result || GTK_IS_PANED((t)->widget));  \
        __result;                                       \
    })


/* Valide un chemin d'accès à une tuile. */
static bool is_valid_tile_path(const char *);

/* Crée une tuile finale d'affichage de panneaux. */
static grid_tile_t *create_leaf_tile(const char *, GtkTiledGrid *);

/* Crée une tuile intermédiaire d'affichage de panneaux. */
static grid_tile_t *create_inter_tile(grid_tile_t *, bool, grid_tile_t *, grid_tile_t *);

/* Supprime une tuile de la mémoire. */
static void delete_tile(grid_tile_t *);

/* Calcule la taille comme entre un chemin et celui d'une tuile. */
static size_t compute_tile_score(const grid_tile_t *, const char *);

/* Indique la tuile adaptée pour un chemin donné. */
static grid_tile_t *find_suitable_tile(grid_tile_t **, const char *, GtkTiledGrid *);

/* Découpe une tuile pour y insérer une zone. */
static grid_tile_t *split_tile(grid_tile_t **, const char *, char, GtkTiledGrid *);

/* Tente de mettre la main sur une station d'accueil. */
static grid_tile_t *find_tile_for_widget(grid_tile_t *, GtkWidget *);

/* Retire une moitié de tuile vide au plein profit de l'autre. */
static void collapse_tile(grid_tile_t *, grid_tile_t *);



/* --------------------------- INTERFACE DU COMPOSANT GTK --------------------------- */


/* Conteneur pour un affichage en tuiles nommées (instance) */
struct _GtkTiledGrid
{
    GtkBin parent;                          /* A laisser en premier        */

    grid_tile_t *tiles;                     /* Tuiles représentées         */

    GPanelItem *def_panel;                  /* Panneau principal par défaut*/

};

/* Conteneur pour un affichage en tuiles nommées (classe) */
struct _GtkTiledGridClass
{
    GtkBinClass parent;                     /* A laisser en premier        */

    /* Signaux */

    void (* station_created) (GtkTiledGrid *, GtkDockStation *, gpointer);

};


/* Initialise la classe des conteneurs d'affichage en tuiles. */
static void gtk_tiled_grid_class_init(GtkTiledGridClass *);

/* Initialise une instance de conteneur d'affichage en tuiles. */
static void gtk_tiled_grid_init(GtkTiledGrid *);

/* Supprime toutes les références externes. */
static void gtk_tiled_grid_dispose(GtkTiledGrid *);

/* Procède à la libération totale de la mémoire. */
static void gtk_tiled_grid_finalize(GtkTiledGrid *);



/* ---------------------------------------------------------------------------------- */
/*                            GESTION DES TUILES AFFICHEES                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin destiné à sélectionner une tuile.              *
*                                                                             *
*  Description : Valide un chemin d'accès à une tuile.                        *
*                                                                             *
*  Retour      : true si le chemin est utilisable, false sinon.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_valid_tile_path(const char *path)
{
    bool result;                            /* Bilan à retourner           */
    size_t len;                             /* Taille du chemin            */
    size_t i;                               /* Boucle de parcours          */
    char c;                                 /* Caractère de chemin analysé */

    /**
     * M[NESWnesw]*
     */

    len = strlen(path);

    result = (len >= 1);

    if (result)
        result = (path[0] == 'M');

    for (i = 1; i < len && result; i++)
    {
        c = path[i];

        if (c == '\0')
            break;

        result = (c == 'N' || c == 'n'
                  || c == 'E' || c == 'e'
                  || c == 'S' || c == 's'
                  || c == 'W' || c == 'w');

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path  = chemin d'accès à la future tuile.                    *
*  Paramètres  : tgrid = conteneur d'affichage en tuiles à manipuler.         *
*                                                                             *
*  Description : Crée une tuile finale d'affichage de panneaux.               *
*                                                                             *
*  Retour      : Structure mise en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static grid_tile_t *create_leaf_tile(const char *path, GtkTiledGrid *tgrid)
{
    grid_tile_t *result;                    /* Structure à retourner       */

    result = (grid_tile_t *)malloc(sizeof(grid_tile_t));

    result->parent = NULL;

    result->widget = gtk_dock_station_new();
    gtk_widget_show(result->widget);

    result->path = strdup(path);

    result->children[0] = NULL;
    result->children[1] = NULL;

    g_signal_emit_by_name(tgrid, "station-created", result->widget);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = tuile parente ou NULL si aucune.                    *
*                horiz  = indique le type d'orientation désiré.               *
*                first  = première tuile à intégrer.                          *
*                second = seconde tuile à intégrer.                           *
*                                                                             *
*  Description : Crée une tuile intermédiaire d'affichage de panneaux.        *
*                                                                             *
*  Retour      : Structure mise en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static grid_tile_t *create_inter_tile(grid_tile_t *parent, bool horiz, grid_tile_t *first, grid_tile_t *second)
{
    grid_tile_t *result;                    /* Structure à retourner       */
    GtkWidget *container;                   /* Conteneur à vider           */

    result = (grid_tile_t *)malloc(sizeof(grid_tile_t));

    result->parent = parent;

    if (horiz)
        result->widget = gtk_paned_new(GTK_ORIENTATION_HORIZONTAL);
    else
        result->widget = gtk_paned_new(GTK_ORIENTATION_VERTICAL);

    gtk_widget_show(result->widget);

    result->path = NULL;

    result->children[0] = first;
    result->children[1] = second;

    /* Changement de propriétaire */

    container = gtk_widget_get_parent(first->widget);

    if (container != NULL)
        gtk_container_remove(GTK_CONTAINER(container), first->widget);

    g_object_ref(G_OBJECT(first->widget));
    gtk_paned_pack1(GTK_PANED(result->widget), first->widget, TRUE, FALSE);

    container = gtk_widget_get_parent(second->widget);

    if (container != NULL)
        gtk_container_remove(GTK_CONTAINER(container), second->widget);

    g_object_ref(G_OBJECT(second->widget));
    gtk_paned_pack2(GTK_PANED(result->widget), second->widget, TRUE, FALSE);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tile = tuile à supprimer.                                    *
*                                                                             *
*  Description : Supprime une tuile de la mémoire.                            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void delete_tile(grid_tile_t *tile)
{
    if (!IS_LEAF_TILE(tile))
    {
        delete_tile(tile->children[0]);
        delete_tile(tile->children[1]);
    }

    else
        free(tile->path);

    g_object_unref(G_OBJECT(tile->widget));

    free(tile);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tile = tuile à analyser.                                     *
*                path = chemin final complet recherché.                       *
*                                                                             *
*  Description : Calcule la taille comme entre un chemin et celui d'une tuile.*
*                                                                             *
*  Retour      : Quantité de caractères communs.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t compute_tile_score(const grid_tile_t *tile, const char *path)
{
    size_t result;                          /* Nombre de points à renvoyer */
    size_t max;                             /* Taille du chemin de la tuile*/
    size_t i;                               /* Boucle de parcours          */
    size_t score_0;                         /* Score du sous-élément #1    */
    size_t score_1;                         /* Score du sous-élément #2    */

    if (IS_LEAF_TILE(tile))
    {
        max = strlen(tile->path);

        if (strlen(path) < max)
            result = 0;

        else
        {
            result = 0;

            for (i = 0; i < max; i++)
            {
                if (tolower((unsigned char)tile->path[i]) == tolower((unsigned char)path[i]))
                    result++;
                else
                    break;
            }

        }

    }
    else
    {
        score_0 = compute_tile_score(tile->children[0], path);
        score_1 = compute_tile_score(tile->children[1], path);

        result = score_0 > score_1 ? score_0 : score_1;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tile  = tuile ou NULL si aucune. [OUT]                       *
*                path  = chemin d'accès à la tuile visée.                     *
*                tgrid = conteneur d'affichage en tuiles à manipuler.         *
*                                                                             *
*  Description : Indique la tuile adaptée pour un chemin donné.               *
*                                                                             *
*  Retour      : Structure d'acceuil à disposition.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static grid_tile_t *find_suitable_tile(grid_tile_t **tile, const char *path, GtkTiledGrid *tgrid)
{
    grid_tile_t *result;                    /* Structure à renvoyer        */
    size_t best_len;                        /* Taille du chemin associé    */
    size_t score_0;                         /* Score du sous-élément #1    */
    size_t score_1;                         /* Score du sous-élément #2    */
    char *sub_path;                         /* Nouvelle tentative d'accès  */
    grid_tile_t **best;                     /* Direction à prendre         */
    unsigned char next;                     /* Prochaine étape             */

    /* Cas d'école : appel initial */
    if (*tile == NULL)
    {
        assert(path[0] == 'M' && path[1] == '\0');

        result = create_leaf_tile("M", tgrid);
        *tile = result;

    }

    else
    {
        if (IS_LEAF_TILE(*tile))
        {
            best_len = compute_tile_score(*tile, path);

            assert(best_len > 0);

            if (path[best_len] == '\0')
                result = *tile;

            else
                result = split_tile(tile, path, path[best_len], tgrid);

        }

        else
        {
            score_0 = compute_tile_score((*tile)->children[0], path);
            score_1 = compute_tile_score((*tile)->children[1], path);

            assert(score_0 > 0 || score_0 > 0);

            if (score_0 == score_1)
            {
                sub_path = strndup(path, score_0);

                score_0 = compute_tile_score((*tile)->children[0], sub_path);
                score_1 = compute_tile_score((*tile)->children[1], sub_path);

                free(sub_path);

            }

            if (score_0 == score_1)
                result = split_tile(tile, path, path[score_0], tgrid);

            else
            {
                if (score_0 > score_1)
                {
                    best = &(*tile)->children[0];
                    best_len = score_0;
                }
                else
                {
                    best = &(*tile)->children[1];
                    best_len = score_1;
                }

                /**
                 * Si on vient de tomber une feuille, trois cas de figure :
                 *    - soit c'est elle qui est visée.
                 *    - soit on veut la diviser.
                 *    - soit on veut la diviser en englobant ses voisines.
                 */

                if (IS_LEAF_TILE(*best))
                {
                    assert(best_len <= strlen(path));

                    next = path[best_len];

                    /* Premier cas */
                    if (next == '\0')
                        result = *best;

                    else
                    {
                        /* Second cas */
                        if (islower(next))
                            result = find_suitable_tile(best, path, tgrid);

                        /* Troisième cas */
                        else
                            result = split_tile(tile, path, next, tgrid);

                    }

                }

                else
                    result = find_suitable_tile(best, path, tgrid);

            }

        }

    }

    assert(IS_LEAF_TILE(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tile     = tuile à découper en deux. [OUT]                   *
*                path     = chemin d'accès à la future tuile.                 *
*                endpoint = désignation de la zone représentée.               *
*                tgrid    = conteneur d'affichage en tuiles à manipuler.      *
*                                                                             *
*  Description : Découpe une tuile pour y insérer une zone.                   *
*                                                                             *
*  Retour      : Structure fille mise en place.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static grid_tile_t *split_tile(grid_tile_t **tile, const char *path, char endpoint, GtkTiledGrid *tgrid)
{
    grid_tile_t *result;                    /* Création à retourner        */
    GtkWidget *container;                   /* Conteneur à vider           */
    grid_tile_t *new;                       /* Nouvelle tuile intermédiaire*/

    container = gtk_widget_get_parent((*tile)->widget);

    /* Création */

    result = create_leaf_tile(path, tgrid);

    /* Encapsulation */

    switch (endpoint)
    {
        case 'N':
        case 'n':
            new = create_inter_tile((*tile)->parent, false, result, *tile);
            break;

        case 'E':
        case 'e':
            new = create_inter_tile((*tile)->parent, true, *tile, result);
            break;

        case 'S':
        case 's':
            new = create_inter_tile((*tile)->parent, false, *tile, result);
            break;

        case 'W':
        case 'w':
            new = create_inter_tile((*tile)->parent, true, result, *tile);
            break;

        default:
            assert(false);
            new = NULL;
            break;

    }

    /* Connexions */

    *tile = new;

    result->parent = new;

    if (container != NULL)
    {
        g_object_ref(G_OBJECT(new->widget));
        gtk_container_add(GTK_CONTAINER(container), new->widget);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tile = tuile parente, prochaine victime de promotion.        *
*                side = côté de tuile amené à disparaître.                    *
*                                                                             *
*  Description : Retire une moitié de tuile vide au plein profit de l'autre.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void collapse_tile(grid_tile_t *tile, grid_tile_t *side)
{
    grid_tile_t *promoted;                  /* Tuile à faire remonter      */
    GtkWidget *container;                   /* Conteneur à vider           */

    assert(!IS_LEAF_TILE(tile));

    /* Sélection du remplaçant */

    if (side == tile->children[0])
        promoted = tile->children[1];
    else
        promoted = tile->children[0];

    /* Etablissement d'une place nette */

    gtk_container_remove(GTK_CONTAINER(tile->widget), promoted->widget);

    container = gtk_widget_get_parent(tile->widget);
    gtk_container_remove(GTK_CONTAINER(container), tile->widget);

    delete_tile(side);

    /* Promotion effective */

    tile->widget = promoted->widget;

    tile->path = promoted->path;

    tile->children[0] = promoted->children[0];
    tile->children[1] = promoted->children[1];

    g_object_ref(G_OBJECT(promoted->widget));
    gtk_container_add(GTK_CONTAINER(container), tile->widget);

    free(promoted);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tile   = point de départ des recherches locales.             *
*                widget = composant graphique à retrouver.                    *
*                                                                             *
*  Description : Tente de mettre la main sur une station d'accueil.           *
*                                                                             *
*  Retour      : Eventuelle tuile trouvée ou NULL.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static grid_tile_t *find_tile_for_widget(grid_tile_t *tile, GtkWidget *widget)
{
    grid_tile_t *result;                    /* Tuile à retourner           */

    if (IS_LEAF_TILE(tile))
        result = tile->widget == widget ? tile : NULL;

    else
    {
        result = find_tile_for_widget(tile->children[0], widget);

        if (result == NULL)
            result = find_tile_for_widget(tile->children[1], widget);

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                             INTERFACE DU COMPOSANT GTK                             */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type du conteneur d'affichage en tuiles nommées. */
G_DEFINE_TYPE(GtkTiledGrid, gtk_tiled_grid, GTK_TYPE_BIN)


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe GTK à initialiser.                            *
*                                                                             *
*  Description : Initialise la classe des conteneurs d'affichage en tuiles.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_tiled_grid_class_init(GtkTiledGridClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)gtk_tiled_grid_dispose;
    object->finalize = (GObjectFinalizeFunc)gtk_tiled_grid_finalize;

    g_signal_new("station-created",
                 GTK_TYPE_TILED_GRID,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GtkTiledGridClass, station_created),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, GTK_TYPE_DOCK_STATION);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tgrid = instance GTK à initialiser.                          *
*                                                                             *
*  Description : Initialise une instance de conteneur d'affichage en tuiles.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_tiled_grid_init(GtkTiledGrid *tgrid)
{
    tgrid->tiles = NULL;

    tgrid->def_panel = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tgrid = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_tiled_grid_dispose(GtkTiledGrid *tgrid)
{
    if (tgrid->tiles != NULL)
    {
        delete_tile(tgrid->tiles);
        tgrid->tiles = NULL;
    }

    g_clear_object(&tgrid->def_panel);

    G_OBJECT_CLASS(gtk_tiled_grid_parent_class)->dispose(G_OBJECT(tgrid));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tgrid = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_tiled_grid_finalize(GtkTiledGrid *tgrid)
{
    G_OBJECT_CLASS(gtk_tiled_grid_parent_class)->finalize(G_OBJECT(tgrid));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une nouvelle instance de conteneur avec tuiles.         *
*                                                                             *
*  Retour      : Composant GTK mis en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *gtk_tiled_grid_new(void)
{
    return g_object_new(GTK_TYPE_TILED_GRID, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tgrid = conteneur d'affichage en tuiles à consulter.         *
*                                                                             *
*  Description : Donne le panneau fourni par défaut pour la zone principale.  *
*                                                                             *
*  Retour      : Panneau d'affichage par défault ou NULL.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GPanelItem *gtk_tiled_grid_get_default_main_panel(const GtkTiledGrid *tgrid)
{
    GPanelItem *result;                     /* Panneau à retourner         */

    result = tgrid->def_panel;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tgrid = conteneur d'affichage en tuiles à modifier.          *
*                panel = panneau d'affichage par défault ou NULL.             *
*                                                                             *
*  Description : Fournit le panneau par défaut pour la zone principale.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_tiled_grid_set_default_main_panel(GtkTiledGrid *tgrid, GPanelItem *panel)
{
    GtkWidget *widget;                      /* Composant GTK à retirer     */
    GtkWidget *parent;                      /* Conteneur à vider           */
    grid_tile_t *tile;                      /* Première tuile d'accueil    */

    if (tgrid->def_panel != NULL)
    {
        widget = gtk_dockable_build_widget(GTK_DOCKABLE(tgrid->def_panel));

        parent = gtk_widget_get_parent(widget);

        if (parent != NULL)
            gtk_container_remove(GTK_CONTAINER(parent), widget);

        g_object_unref(G_OBJECT(widget));

        g_object_unref(G_OBJECT(tgrid->def_panel));

    }

    tgrid->def_panel = panel;

    if (panel != NULL)
    {
        g_object_ref(G_OBJECT(panel));

        if (tgrid->tiles == NULL)
            gtk_tiled_grid_add(tgrid, panel);

        else
        {
            tile = find_suitable_tile(&tgrid->tiles, "M", tgrid);

            if (gtk_notebook_get_n_pages(GTK_NOTEBOOK(tile->widget)) == 0)
                gtk_tiled_grid_add(tgrid, panel);

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tgrid = conteneur d'affichage en tuiles à modifier.          *
*                panel = panneau d'affichage à intégrer.                      *
*                                                                             *
*  Description : Incorpore un nouveau panneau dans le conteneur en tuiles.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_tiled_grid_add(GtkTiledGrid *tgrid, GPanelItem *panel)
{
    char *path;                             /* Chemin d'accès              */
    char *name;                             /* Nom à donner à l'onglet     */
    grid_tile_t *tile;                      /* Tuile d'accueil             */

    path = gtk_panel_item_class_get_path(G_PANEL_ITEM_GET_CLASS(panel));

    if (!is_valid_tile_path(path))
    {
        name = gtk_dockable_get_name(GTK_DOCKABLE(panel));
        log_variadic_message(LMT_ERROR, _("Invalid path '%s' for panel '%s'"), path, name);
        free(name);
    }

    else
    {
        tile = find_suitable_tile(&tgrid->tiles, path, tgrid);
        assert(tile != NULL);

        gtk_dock_station_add_dockable(GTK_DOCK_STATION(tile->widget), GTK_DOCKABLE(panel));

        g_panel_item_set_dock_at_startup(panel, true);

        /* Si c'est la toute première fois... */
        if (gtk_widget_get_parent(tile->widget) == NULL)
        {
            assert(tile == tgrid->tiles);
            assert(tile->path[0] == 'M' && tile->path[1] == '\0');
            g_object_ref(G_OBJECT(tile->widget));
            gtk_container_add(GTK_CONTAINER(tgrid), tile->widget);
        }

        /* Si on n'a plus besoin du panneau par défaut */
        if (tgrid->def_panel != NULL && tile->path[0] == 'M' && tile->path[1] == '\0')
        {
            /* Si ce n'est pas le panneau qu'on vient de rajouter...*/
            if (panel != tgrid->def_panel)
            {
                /* Enfin : si ce panneau par défaut est réellement en place */
                if (g_panel_item_is_docked(tgrid->def_panel))
                    gtk_tiled_grid_remove(tgrid, tgrid->def_panel);

            }

        }

    }

    free(path);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tgrid = conteneur d'affichage en tuiles à modifier.          *
*                panel = panneau d'affichage à supprimer.                     *
*                                                                             *
*  Description : Retire un panneau dans le conteneur en tuiles.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_tiled_grid_remove(GtkTiledGrid *tgrid, GPanelItem *panel)
{
    GtkWidget *station;                     /* Support courant             */
    grid_tile_t *tile;                      /* Tuile d'accueil             */

    assert(g_panel_item_is_docked(panel));

    gtk_dockable_decompose(GTK_DOCKABLE(panel), &station);

    tile = find_tile_for_widget(tgrid->tiles, station);
    assert(tile != NULL);

    gtk_dock_station_remove_dockable(GTK_DOCK_STATION(station), GTK_DOCKABLE(panel));

    g_panel_item_set_dock_at_startup(panel, false);

    if (gtk_notebook_get_n_pages(GTK_NOTEBOOK(station)) == 0)
    {
        /* Si le panneau par défaut devient nécessaire */
        if (tgrid->def_panel != NULL && tile->path[0] == 'M' && tile->path[1] == '\0')
            gtk_tiled_grid_add(tgrid, tgrid->def_panel);

        else
        {
            /* La racine est concernée ! */
            if (tile->parent == NULL)
            {
                assert(tile == tgrid->tiles);

                g_object_ref(G_OBJECT(tile->widget));
                gtk_container_remove(GTK_CONTAINER(tgrid), tile->widget);

                delete_tile(tile);
                tgrid->tiles = NULL;

            }

            else
                collapse_tile(tile->parent, tile);

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tgrid   = conteneur d'affichage en tuiles à consulter.       *
*                station = station d'accueil à retrouver.                     *
*                                                                             *
*  Description : Indique le chemin correspondant à une station intégrée.      *
*                                                                             *
*  Retour      : Copie de chemin trouvé, à libérer ensuite, ou NULL si échec. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *gtk_tiled_grid_get_path_for_station(const GtkTiledGrid *tgrid, GtkDockStation *station)
{
    char *result;                           /* Chemin d'accès à renvoyer   */
    grid_tile_t *tile;                      /* Tuile d'accueil             */

    tile = find_tile_for_widget(tgrid->tiles, GTK_WIDGET(station));

    if (tile == NULL)
        result = NULL;

    else
        result = strdup(tile->path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tgrid  = conteneur d'affichage en tuiles à mettre à jour.    *
*                config = configuration à consulter.                          *
*                                                                             *
*  Description : Replace les positions des séparateurs de tuiles.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_tiled_grid_restore_positions(const GtkTiledGrid *tgrid, GGenConfig *config)
{

    void visit_tiles_for_restoring(grid_tile_t *tile, const char *vpath)
    {
        GtkOrientation orientation;         /* Direction de la tuile       */
        char hint;                          /* Inutile donc indispensable  */
        char *key;                          /* Clef d'accès à un paramètre */
        gint position;                      /* Nouvelle position de barre  */
        size_t i;                           /* Boucle de parcours          */
        char *child_key;                    /* Clef d'accès des suivants   */

        if (!IS_LEAF_TILE(tile))
        {
            orientation = gtk_orientable_get_orientation(GTK_ORIENTABLE(tile->widget));

            hint = orientation == GTK_ORIENTATION_HORIZONTAL ? 'h' : 'v';

            asprintf(&key, "%s%c", vpath, hint);

            if (g_generic_config_get_value(config, key, &position))
                gtk_paned_set_position(GTK_PANED(tile->widget), position);

            for (i = 0; i < 2; i++)
            {
                asprintf(&child_key, "%s%zu", key, i);

                visit_tiles_for_restoring(tile->children[i], child_key);

                free(child_key);

            }

            free(key);

        }

    }


    visit_tiles_for_restoring(tgrid->tiles, "gui.panels.positions.R");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : tgrid  = conteneur d'affichage en tuiles à consulter.        *
*                config = configuration à mettre à jour.                      *
*                                                                             *
*  Description : Sauvegarde les positions des séparateurs de tuiles.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_tiled_grid_save_positions(const GtkTiledGrid *tgrid, GGenConfig *config)
{

    void visit_tiles_for_saving(grid_tile_t *tile, const char *vpath)
    {
        GtkOrientation orientation;         /* Direction de la tuile       */
        char hint;                          /* Inutile donc indispensable  */
        char *key;                          /* Clef d'accès à un paramètre */
        gint position;                      /* Nouvelle position de barre  */
        size_t i;                           /* Boucle de parcours          */
        char *child_key;                    /* Clef d'accès des suivants   */

        if (!IS_LEAF_TILE(tile))
        {
            orientation = gtk_orientable_get_orientation(GTK_ORIENTABLE(tile->widget));

            hint = orientation == GTK_ORIENTATION_HORIZONTAL ? 'h' : 'v';

            asprintf(&key, "%s%c", vpath, hint);

            position = gtk_paned_get_position(GTK_PANED(tile->widget));
            g_generic_config_create_or_udpdate_param(config, key, CPT_INTEGER, -1, position);

            for (i = 0; i < 2; i++)
            {
                asprintf(&child_key, "%s%zu", key, i);

                visit_tiles_for_saving(tile->children[i], child_key);

                free(child_key);

            }

            free(key);

        }

    }


    visit_tiles_for_saving(tgrid->tiles, "gui.panels.positions.R");

}
