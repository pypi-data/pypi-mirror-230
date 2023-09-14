
/* Chrysalide - Outil d'analyse de fichiers binaires
 * items.c - manipulation de l'ensemble des composants graphiques actifs
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#include "items.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "global.h"
#include "../../analysis/binary.h"
#include "../../analysis/db/items/move.h"



/* Liste des éléments en place */
static GEditorItem **_item_list = NULL;
static size_t _item_count = 0;

/* Initialisations premières de façon unique */
static bool _first_content_change = true;
static bool _first_panel_change = true;


/* Lance une procédure de déplacement de la position courante. */
static void start_moving_to_cursor_in_loaded_panel(GLoadedPanel *, const GLineCursor *, gboolean, gpointer);

/* Suit les changements de position dans du code d'assembleur. */
static void track_cursor_on_view_panel(GLoadedPanel *, const GLineCursor *, gpointer);



/******************************************************************************
*                                                                             *
*  Paramètres  : item = élément de l'interface graphique à intégrer.          *
*                                                                             *
*  Description : Procède à l'enregistrement d'un élément reactif de l'éditeur.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_editor_item(GEditorItem *item)
{
    _item_list = realloc(_item_list, ++_item_count * sizeof(GEditorItem *));

    _item_list[_item_count - 1] = item;

    g_object_ref(G_OBJECT(item));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = type de l'élément réactif à retrouver.              *
*                                                                             *
*  Description : Retrouve un élément reactif de l'éditeur par son type.       *
*                                                                             *
*  Retour      : Elément retrouvé ou NULL.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GEditorItem *find_editor_item_by_type(GType target)
{
    GEditorItem *result;                    /* Elément à retourner         */
    size_t i;                               /* Boucle de parcours          */
    GType type;                             /* Type d'un élément analysé   */

    result = NULL;

    for (i = 0; i < _item_count && result == NULL; i++)
    {
        type = G_TYPE_FROM_INSTANCE(_item_list[i]);

        if (type == target)
        {
            result = _item_list[i];
            g_object_ref(G_OBJECT(result));
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = élément de l'interface graphique à oublier.           *
*                                                                             *
*  Description : Retire un des éléments reactifs de l'éditeur.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unregister_editor_item(GEditorItem *item)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < _item_count; i++)
        if (_item_list[i] == item)
            break;

    assert(i < _item_count);

    g_object_unref(G_OBJECT(item));

    memmove(&_item_list[i], &_item_list[i + 1], (_item_count - i - 1) * sizeof(GEditorItem *));

    _item_list = realloc(_item_list, --_item_count * sizeof(GEditorItem *));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = nouvelle instance de contenu analysé.              *
*                                                                             *
*  Description : Lance une actualisation du fait d'un changement de contenu.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void change_editor_items_current_content(GLoadedContent *content)
{
    GLoadedContent *old;                    /* Ancien contenu              */
    size_t i;                               /* Boucle de parcours          */

    old = get_current_content();

    if (content != old || _first_content_change)
    {
        _first_content_change = false;

        if (content != NULL)
            g_object_ref(G_OBJECT(content));

        set_current_content(content);

        for (i = 0; i < _item_count; i++)
            g_editor_item_change_content(_item_list[i], old, content);

    }

    if (old != NULL)
        g_object_unref(G_OBJECT(old));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = composant d'affichage parcouru.                     *
*                cursor = emplacement à cibler pour un déplacement.           *
*                save   = le changement est-il majeur ?                       *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Lance une procédure de déplacement de la position courante.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void start_moving_to_cursor_in_loaded_panel(GLoadedPanel *panel, const GLineCursor *cursor, gboolean save, gpointer unused)
{
    GLineCursor *src;                       /* Position courante de curseur*/
    GDbMove *move;                          /* Déplacement à organiser     */
    GLoadedBinary *binary;                  /* Binaire en cours d'étude    */

    src = g_loaded_panel_get_cursor(panel);

    if (save && src != NULL)
    {
        move = g_db_move_new(src, cursor);

        binary = G_LOADED_BINARY(g_loaded_panel_get_content(panel));
        g_loaded_binary_add_to_collection(binary, G_DB_ITEM(move));
        g_object_unref(G_OBJECT(binary));

    }

    else
        g_loaded_panel_scroll_to_cursor(panel, cursor, SPT_CENTER, true);

    if (src != NULL)
        g_object_unref(G_OBJECT(src));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel  = composant d'affichage parcouru.                     *
*                cursor = nouvel emplacement du curseur courant.              *
*                unused = adresse non utilisée ici.                           *
*                                                                             *
*  Description : Suit les changements de position dans du code d'assembleur.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void track_cursor_on_view_panel(GLoadedPanel *panel, const GLineCursor *cursor, gpointer unused)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < _item_count; i++)
        g_editor_item_track_cursor(_item_list[i], panel, cursor);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = nouveau panneau d'affichage actif.                   *
*                                                                             *
*  Description : Lance une actualisation du fait d'un changement de vue.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void change_editor_items_current_view(GLoadedPanel *panel)
{
    GLoadedPanel *old;                      /* Ancien affichage            */
    size_t i;                               /* Boucle de parcours          */

    /* Suivi des affichages */

    old = get_current_view();

    if (panel != old || _first_panel_change)
    {
        _first_panel_change = false;

        if (panel != NULL)
            g_object_ref(G_OBJECT(panel));

        set_current_view(panel);

        for (i = 0; i < _item_count; i++)
            g_editor_item_change_view(_item_list[i], old, panel);

        /* Suivi du curseur */

        if (old != NULL)
        {
            g_signal_handlers_disconnect_by_func(old,
                                                 G_CALLBACK(start_moving_to_cursor_in_loaded_panel),
                                                 NULL);
            g_signal_handlers_disconnect_by_func(old,
                                                 G_CALLBACK(track_cursor_on_view_panel),
                                                 NULL);
        }

        if (panel != NULL)
        {
            g_signal_connect(panel, "move-request",
                             G_CALLBACK(start_moving_to_cursor_in_loaded_panel),
                             NULL);

            g_signal_connect(panel, "cursor-moved",
                             G_CALLBACK(track_cursor_on_view_panel),
                             NULL);
        }

    }

    if (old != NULL)
        g_object_unref(G_OBJECT(old));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : panel = nouveau panneau d'affichage actif.                   *
*                                                                             *
*  Description : Lance une actualisation du fait d'un changement de contenu.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void update_editor_items_current_view(GLoadedPanel *panel)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < _item_count; i++)
        g_editor_item_update_view(_item_list[i], panel);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu contenant le curseur à représenter.        *
*                cursor  = nouvel emplacement du curseur courant.             *
*                source  = composant à l'origine du changement.               *
*                                                                             *
*  Description : Concentre l'attention de l'ensemble sur une adresse donnée.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void focus_cursor_in_editor_items(GLoadedContent *content, const GLineCursor *cursor, GEditorItem *source)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < _item_count; i++)
    {
        if (_item_list[i] != source)
            g_editor_item_focus_cursor(_item_list[i], content, cursor);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : project = projet concerné par l'évolution.                   *
*                                                                             *
*  Description : Lance une actualisation relative à l'étendue du projet.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void update_project_area(GStudyProject *project)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < _item_count; i++)
        g_editor_item_update_project_area(_item_list[i], project);

}
