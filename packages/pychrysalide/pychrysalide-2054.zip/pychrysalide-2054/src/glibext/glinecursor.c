
/* Chrysalide - Outil d'analyse de fichiers binaires
 * glinecursor.c - suivi de positions dans des panneaux de chargement
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


#include "glinecursor.h"


#include <assert.h>


#include "glinecursor-int.h"



/* ----------------------- FONCTIONNALITES D'UN SUIVI DE BASE ----------------------- */


/* Procède à l'initialisation d'une classe de suivi de position. */
static void g_line_cursor_class_init(GLineCursorClass *);

/* Procède à l'initialisation d'un suivi de positions. */
static void g_line_cursor_init(GLineCursor *);

/* Supprime toutes les références externes. */
static void g_line_cursor_dispose(GLineCursor *);

/* Procède à la libération totale de la mémoire. */
static void g_line_cursor_finalize(GLineCursor *);



/* ---------------------------------------------------------------------------------- */
/*                         FONCTIONNALITES D'UN SUIVI DE BASE                         */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type du gestionnaire de largeurs associées aux lignes. */
G_DEFINE_TYPE(GLineCursor, g_line_cursor, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe de composant GTK à initialiser.               *
*                                                                             *
*  Description : Procède à l'initialisation d'une classe de suivi de position.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_line_cursor_class_init(GLineCursorClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_line_cursor_dispose;
    object->finalize = (GObjectFinalizeFunc)g_line_cursor_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = composant GLib à initialiser.                       *
*                                                                             *
*  Description : Procède à l'initialisation d'un suivi de positions.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_line_cursor_init(GLineCursor *cursor)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_line_cursor_dispose(GLineCursor *cursor)
{
    G_OBJECT_CLASS(g_line_cursor_parent_class)->dispose(G_OBJECT(cursor));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_line_cursor_finalize(GLineCursor *cursor)
{
    G_OBJECT_CLASS(g_line_cursor_parent_class)->finalize(G_OBJECT(cursor));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi d'emplacement à dupliquer.                    *
*                                                                             *
*  Description : Réalise la copie d'un suivi d'emplacements.                  *
*                                                                             *
*  Retour      : Nouvelle instance copiée.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GLineCursor *g_line_cursor_duplicate(const GLineCursor *cursor)
{
    GLineCursor *result;                    /* Instance à retourner        */

    result = G_LINE_CURSOR_GET_CLASS(cursor)->duplicate(cursor);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = premier suivi d'emplacement à comparer.             *
*                other  = second suivi d'emplacement à comparer.              *
*                                                                             *
*  Description : Compare deux suivis d'emplacements.                          *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int g_line_cursor_compare(const GLineCursor *cursor, const GLineCursor *other)
{
    int result;                             /* Bilan à renvoyer            */

    assert(G_OBJECT_TYPE(cursor) == G_OBJECT_TYPE(other));

    result = G_LINE_CURSOR_GET_CLASS(cursor)->compare(cursor, other);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi d'emplacement à consulter.                    *
*                                                                             *
*  Description : Détermine si la position de suivi est pertinente ou non.     *
*                                                                             *
*  Retour      : Bilan de validité.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_line_cursor_is_valid(const GLineCursor *cursor)
{
    bool result;                            /* Bilan à renvoyer            */

    result = G_LINE_CURSOR_GET_CLASS(cursor)->is_valid(cursor);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi d'emplacement à consulter.                    *
*                                                                             *
*  Description : Construit une étiquette de représentation d'un suivi.        *
*                                                                             *
*  Retour      : Etiquette à libérer de la mémoire après usage.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_line_cursor_build_label(const GLineCursor *cursor)
{
    char *result;                           /* Etiquette à retourner       */

    result = G_LINE_CURSOR_GET_CLASS(cursor)->build_label(cursor);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor  = emplacement du curseur à afficher.                 *
*                stack   = pile de statuts à mettre à jour.                   *
*                content = contenu contenant le curseur à représenter.        *
*                                                                             *
*  Description : Affiche une position dans une barre de statut.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_line_cursor_show_status(const GLineCursor *cursor, GtkStatusStack *stack, GLoadedContent *content)
{
    G_LINE_CURSOR_GET_CLASS(cursor)->show_status(cursor, stack, content);

}



/* ---------------------------------------------------------------------------------- */
/*                        ENCADREMENT DES TRANSFERTS DE DONEES                        */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi de positions à sauvegarder.                   *
*                pbuf   = paquet de données où venir inscrire les infos.      *
*                                                                             *
*  Description : Exporte la définition d'un emplacement dans un flux réseau.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_line_cursor_serialize(const GLineCursor *cursor, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = G_LINE_CURSOR_GET_CLASS(cursor)->serialize(cursor, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi de positions à charger. [OUT]                 *
*                pbuf = paquet de données où venir inscrire les infos.        *
*                                                                             *
*  Description : Importe la définition d'un emplacement depuis un flux réseau.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_line_cursor_unserialize(GLineCursor *cursor, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = G_LINE_CURSOR_GET_CLASS(cursor)->unserialize(cursor, pbuf);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           LIENS AVEC UNE BASE DE DONNEES                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi de positions à traiter.                       *
*                base   = tronc commun pour les champs de la base de données. *
*                                                                             *
*  Description : Donne les éléments requis pour la construction d'une table.  *
*                                                                             *
*  Retour      : Partie de requête à insérer dans la requête globale.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_line_cursor_create_db_table(const GLineCursor *cursor, const char *base)
{
    char *result;                           /* Requête à retourner         */

    result = G_LINE_CURSOR_GET_CLASS(cursor)->create_db(base);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi de positions à traiter.                       *
*                base   = tronc commun pour les champs de la base de données. *
*                values = tableau d'éléments à compléter. [OUT]               *
*                count  = nombre de descriptions renseignées. [OUT]           *
*                                                                             *
*  Description : Décrit les colonnes utiles à un chargement de données.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_line_cursor_setup_load(const GLineCursor *cursor, const char *base, bound_value **values, size_t *count)
{
    bool result;                            /* Bilan à renvoyer            */

    result = G_LINE_CURSOR_GET_CLASS(cursor)->store(NULL, base, values, count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi de positions dont la définition est à définir.*
*                base   = tronc commun pour les champs de la base de données. *
*                values = tableau d'éléments à consulter.                     *
*                count  = nombre de descriptions renseignées.                 *
*                                                                             *
*  Description : Charge les valeurs utiles pour une localisation.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_line_cursor_load(GLineCursor *cursor, const char *base, const bound_value *values, size_t count)
{
    bool result;                            /* Bilan à renvoyer            */

    result = G_LINE_CURSOR_GET_CLASS(cursor)->load(cursor, base, values, count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi de positions à traiter.                       *
*                base   = tronc commun pour les champs de la base de données. *
*                values = couples de champs et de valeurs à lier. [OUT]       *
*                count  = nombre de ces couples. [OUT]                        *
*                                                                             *
*  Description : Constitue les champs destinés à une insertion / modification.*
*                                                                             *
*  Retour      : Bilan de l'opération : succès ou non.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_line_cursor_store(const GLineCursor *cursor, const char *base, bound_value **values, size_t *count)
{
    bool result;                            /* Bilan à renvoyer            */

    result = G_LINE_CURSOR_GET_CLASS(cursor)->store(cursor, base, values, count);

    return result;

}
