
/* Chrysalide - Outil d'analyse de fichiers binaires
 * block.h - encadrement des blocs de code
 *
 * Copyright (C) 2012-2019 Cyrille Bagard
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


#include "block.h"


#include <assert.h>
#include <malloc.h>


#include "block-int.h"



/* ----------------------------- BLOC DE CODE GENERIQUE ----------------------------- */


/* Initialise la classe des blocs de code. */
static void g_code_block_class_init(GCodeBlockClass *);

/* Initialise un bloc de code. */
static void g_code_block_init(GCodeBlock *);

/* Supprime toutes les références externes. */
static void g_code_block_dispose(GCodeBlock *);

/* Procède à la libération totale de la mémoire. */
static void g_code_block_finalize(GCodeBlock *);

/* Indique l'indice d'intégration du bloc dans une liste. */
static void g_code_block_set_index(GCodeBlock *, size_t);



/* ------------------------- REGROUPEMENT EN LISTE DE BLOCS ------------------------- */


/* Description d'une liste de blocs de code (instance) */
struct _GBlockList
{
    GObject parent;                         /* A laisser en premier        */

    GCodeBlock **blocks;                    /* Blocs de code rassemblés    */
    size_t count;                           /* Quantité de ces blocs       */

};

/* Description d'une liste de blocs de code (classe) */
struct _GBlockListClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des listes de blocs de code. */
static void g_block_list_class_init(GBlockListClass *);

/* Initialise une liste de blocs de code. */
static void g_block_list_init(GBlockList *);

/* Supprime toutes les références externes. */
static void g_block_list_dispose(GBlockList *);

/* Procède à la libération totale de la mémoire. */
static void g_block_list_finalize(GBlockList *);



/* ---------------------------------------------------------------------------------- */
/*                               BLOC DE CODE GENERIQUE                               */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un bloc de code. */
G_DEFINE_TYPE(GCodeBlock, g_code_block, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des blocs de code.                      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_code_block_class_init(GCodeBlockClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_code_block_dispose;
    object->finalize = (GObjectFinalizeFunc)g_code_block_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise un bloc de code.                                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_code_block_init(GCodeBlock *block)
{
    block->list = NULL;

    block->index = (size_t)-1;
    block->rank = (size_t)-1;

#ifdef INCLUDE_GTK_SUPPORT
    block->view = NULL;
#endif

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_code_block_dispose(GCodeBlock *block)
{
#ifdef INCLUDE_GTK_SUPPORT
    g_clear_object(&block->view);
#endif

    G_OBJECT_CLASS(g_code_block_parent_class)->dispose(G_OBJECT(block));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_code_block_finalize(GCodeBlock *block)
{
    delete_bit_field(block->domination);

    G_OBJECT_CLASS(g_code_block_parent_class)->finalize(G_OBJECT(block));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc de code à consulter.                            *
*                                                                             *
*  Description : Indique la liste des blocs de code dominés.                  *
*                                                                             *
*  Retour      : Champ de bits représentant des blocs.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const bitfield_t *g_code_block_get_domination(const GCodeBlock *block)
{
    return block->domination;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc à mettre à jour.                                *
*                index = indice valide dans la liste d'appartenance.          *
*                                                                             *
*  Description : Indique l'indice d'intégration du bloc dans une liste.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_code_block_set_index(GCodeBlock *block, size_t index)
{
    assert(block->index == (size_t)-1);

    block->index = index;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc à consulter.                                    *
*                                                                             *
*  Description : Indique l'indice d'intégration du bloc dans une liste.       *
*                                                                             *
*  Retour      : Indice valide dans une liste.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_code_block_get_index(const GCodeBlock *block)
{
    size_t result;                          /* Indice à retourner          */

    assert(block->index != (size_t)-1);

    result = block->index;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc de code à consulter.                            *
*                addr  = localisation à comparer.                             *
*                                                                             *
*  Description : Détermine si un bloc de code contient une adresse donnée.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_code_block_contains_addr(const GCodeBlock *block, const vmpa2t *addr)
{
    bool result;                            /* Bilan à retourner           */
    GCodeBlockClass *class;                 /* Classe des blocs de code    */

    class = G_CODE_BLOCK_GET_CLASS(block);

    result = class->contains(block, addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc de code à consulter.                            *
*                                                                             *
*  Description : Fournit le rang du bloc de code dans le flot d'exécution.    *
*                                                                             *
*  Retour      : Indice supérieur ou égal à zéro.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_code_block_get_rank(const GCodeBlock *block)
{
    size_t result;                          /* Rang à retourner            */

    result = block->rank;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc de code à mettre à jour.                        *
*                rank  = indice supérieur à zéro à prendre en compte.         *
*                                                                             *
*  Description : Définit le rang du bloc de code dans le flot d'exécution.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_code_block_set_rank(GCodeBlock *block, size_t rank)
{
    block->rank = rank;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : block       = bloc de code à manipuler.                      *
*                highlighted = gestionnaire de surbrillance pour segments.    *
*                                                                             *
*  Description : Fournit la représentation graphique d'un bloc de code.       *
*                                                                             *
*  Retour      : Vue d'un cache de lignes.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBufferView *g_code_block_get_view(GCodeBlock *block, segcnt_list *highlighted)
{
    GBufferView *result;                    /* Instance à retourner        */
    GCodeBlockClass *class;                 /* Classe des blocs de code    */

    if (block->view == NULL)
    {
        class = G_CODE_BLOCK_GET_CLASS(block);

        block->view = class->build(block, highlighted);

    }

    result = block->view;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc de code à consulter.                            *
*                                                                             *
*  Description : Construit un ensemble d'indications pour bloc.               *
*                                                                             *
*  Retour      : Informations à présenter sous forme de bulle d'aide.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_code_block_build_tooltip(const GCodeBlock *block)
{
    char *result;                           /* Description à retourner     */
    GCodeBlockClass *class;                 /* Classe des blocs de code    */

    class = G_CODE_BLOCK_GET_CLASS(block);

    result = class->build_tooltip(block);

    return result;

}


#endif



/* ---------------------------------------------------------------------------------- */
/*                     DEFINITION DE LIAISONS ENTRE BLOCS DE CODE                     */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : link_a = premier lien à traiter.                             *
*                link_b = second lien à traiter.                              *
*                                                                             *
*  Description : Compare deux liens entre blocs de code.                      *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int g_code_block_compare_links(const block_link_t *link_a, const block_link_t *link_b)
{
    int result;                             /* Bilan à retourner           */
    GCodeBlockClass *class;                 /* Classe des blocs de code    */

    assert(G_TYPE_FROM_INSTANCE(link_a->linked) == G_TYPE_FROM_INSTANCE(link_b->linked));

    class = G_CODE_BLOCK_GET_CLASS(link_a->linked);

    result = class->cmp_links(link_a, link_b);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : link_a = premier lien à traiter.                             *
*                link_b = second lien à traiter.                              *
*                                                                             *
*  Description : Compare deux liens entre blocs de code.                      *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int g_code_block_compare_links_reversed(const block_link_t *link_a, const block_link_t *link_b)
{
    int result;                             /* Bilan à retourner           */

    result = g_code_block_compare_links(link_a, link_b);

    result *= -1;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc dont les informations sont à consulter.         *
*                count = nombre de ces origines. [OUT]                        *
*                                                                             *
*  Description : Fournit les détails des origines d'un bloc de code donné.    *
*                                                                             *
*  Retour      : Liens déterminés vers des blocs de code d'origine.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

block_link_t *g_code_block_get_sources(const GCodeBlock *block, size_t *count)
{
    block_link_t *result;                   /* Détails présents à renvoyer */
    GCodeBlockClass *class;                 /* Classe des blocs de code    */

    if (block->list == NULL)
    {
        result = NULL;
        *count = 0;
    }

    else
    {
        class = G_CODE_BLOCK_GET_CLASS(block);

        result = class->get_src(block, block->list, count);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = bloc dont les informations sont à consulter.         *
*                count = nombre de ces destinations. [OUT]                    *
*                                                                             *
*  Description : Fournit les détails des destinations de bloc de code.        *
*                                                                             *
*  Retour      : Liens déterminés vers des blocs de code de destination.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

block_link_t *g_code_block_get_destinations(const GCodeBlock *block, size_t *count)
{
    block_link_t *result;                   /* Détails présents à renvoyer */
    GCodeBlockClass *class;                 /* Classe des blocs de code    */

    if (block->list == NULL)
    {
        result = NULL;
        *count = 0;
    }

    else
    {
        class = G_CODE_BLOCK_GET_CLASS(block);

        result = class->get_dest(block, block->list, count);

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           REGROUPEMENT EN LISTE DE BLOCS                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une liste de blocs de code. */
G_DEFINE_TYPE(GBlockList, g_block_list, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des listes de blocs de code.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_block_list_class_init(GBlockListClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_block_list_dispose;
    object->finalize = (GObjectFinalizeFunc)g_block_list_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une liste de blocs de code.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_block_list_init(GBlockList *list)
{
    list->blocks = NULL;
    list->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_block_list_dispose(GBlockList *list)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < list->count; i++)
        g_clear_object(&list->blocks[i]);

    G_OBJECT_CLASS(g_block_list_parent_class)->dispose(G_OBJECT(list));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : block = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_block_list_finalize(GBlockList *list)
{
    if (list->blocks != NULL)
        free(list->blocks);

    G_OBJECT_CLASS(g_block_list_parent_class)->finalize(G_OBJECT(list));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : count = quantité finale de blocs présentie.                  *
*                                                                             *
*  Description : Crée une liste de blocs de code.                             *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBlockList *g_block_list_new(size_t count)
{
    GBlockList *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_BLOCK_LIST, NULL);

    if (count == 0)
        result->blocks = NULL;
    else
        result->blocks = calloc(count, sizeof(GCodeBlock *));

    result->count = count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = liste de blocs de code à consulter.                   *
*                                                                             *
*  Description : Compte le nombre de blocs de code représentés.               *
*                                                                             *
*  Retour      : Quantité de blocs de code rassemblés.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_block_list_count_blocks(const GBlockList *list)
{
    size_t result;                          /* Quantité à retourner        */

    result = list->count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list  = liste de blocs de code à compléter.                  *
*                block = bloc de code à intégrer.                             *
*                index = indice de la position d'insertion du bloc.           *
*                                                                             *
*  Description : Ajoute un bloc de code à une liste définie.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_block_list_add_block(GBlockList *list, GCodeBlock *block, size_t index)
{
    assert(index < list->count);
    assert(list->blocks[index] == NULL);

    list->blocks[index] = block;

    block->list = list;

    g_code_block_set_index(block, index);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list  = liste de blocs de code à compléter.                  *
*                block = bloc de code à intégrer.                             *
*                                                                             *
*  Description : Ajoute un bloc de code à une liste en construction.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_block_list_append_block(GBlockList *list, GCodeBlock *block)
{
    list->blocks = realloc(list->blocks, ++list->count * sizeof(GCodeBlock *));

    list->blocks[list->count - 1] = block;

    g_code_block_set_index(block, list->count - 1);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list  = liste de blocs de code à consulter.                  *
*                index = indice de la position du bloc recherché.             *
*                                                                             *
*  Description : Fournit le bloc de code correspondant à un indice de liste.  *
*                                                                             *
*  Retour      : Bloc de code trouvé, ou NULL en cas d'erreur.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GCodeBlock *g_block_list_get_block(const GBlockList *list, size_t index)
{
    GCodeBlock *result;                     /* Bloc de code à retourner    */

    assert(index < list->count);

    if (index < list->count)
        result = list->blocks[index];
    else
        result = NULL;

    /**
     * La liste peut être dimensionnée sans avoir été remplie...
     * Donc on fait attention avec le compteur de références.
     */

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list = liste de blocs de code à consulter.                   *
*                addr = localisation à comparer.                              *
*                                                                             *
*  Description : Recherche un bloc de code contenant une adresse donnée.      *
*                                                                             *
*  Retour      : Bloc de code trouvé ou NULL si aucun.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GCodeBlock *g_block_list_find_by_addr(const GBlockList *list, const vmpa2t *addr)
{
    GCodeBlock *result;                     /* Trouvaille à retourner      */
    size_t i;                               /* Boucle de parcours          */
    GCodeBlock *block;                      /* Bloc basique analysé        */

    result = NULL;

    for (i = 0; i < list->count && result == NULL; i++)
    {
        block = list->blocks[i];

        /**
         * La liste peut être dimensionnée sans avoir été remplie...
         * Donc on fait attention.
         */

        assert(block != NULL);

        if (block == NULL)
            continue;

        if (g_code_block_contains_addr(block, addr))
        {
            result = block;
            g_object_ref(G_OBJECT(result));
        }

    }

    return result;

}
