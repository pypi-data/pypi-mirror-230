
/* Chrysalide - Outil d'analyse de fichiers binaires
 * item.c - gestion des différents éléments réactifs de l'éditeurs
 *
 * Copyright (C) 2010-2020 Cyrille Bagard
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "item.h"


#include <assert.h>


#include "item-int.h"



/* Initialise la classe des éléments réactifs de l'éditeur. */
static void g_editor_item_class_init(GEditorItemClass *);

/* Initialise une instance d'élément réactif pour l'éditeur. */
static void g_editor_item_init(GEditorItem *);


/* Indique le type défini pour un élément réactif d'éditeur. */
G_DEFINE_TYPE(GEditorItem, g_editor_item, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des éléments réactifs de l'éditeur.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_editor_item_class_init(GEditorItemClass *klass)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance d'élément réactif pour l'éditeur.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_editor_item_init(GEditorItem *item)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe à consulter.                                  *
*                                                                             *
*  Description : Fournit le nom interne attribué à l'élément réactif.         *
*                                                                             *
*  Retour      : Désignation (courte) de l'élément de l'éditeur.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_editor_item_class_get_key(const GEditorItemClass *class)
{
    char *result;                           /* Description à renvoyer      */

    assert(class->get_key != NULL);

    result = class->get_key(class);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance à consulter.                                 *
*                                                                             *
*  Description : Fournit le composant GTK associé à l'élément réactif.        *
*                                                                             *
*  Retour      : Instance de composant graphique chargé.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *g_editor_item_get_widget(const GEditorItem *item)
{
    GtkWidget *result;                      /* Composant à retourner       */
    GEditorItemClass *klass;                /* Classe correspondante       */

    klass = G_EDITOR_ITEM_GET_CLASS(item);

    assert(klass->get_widget != NULL);

    result = klass->get_widget(item);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance à consulter.                                 *
*                old  = ancien contenu chargé analysé.                        *
*                new  = nouveau contenu chargé à analyser.                    *
*                                                                             *
*  Description : Réagit à un changement de contenu chargé en cours d'analyse. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_editor_item_change_content(GEditorItem *item, GLoadedContent *old, GLoadedContent *new)
{
    GEditorItemClass *klass;                /* Classe correspondante       */

    klass = G_EDITOR_ITEM_GET_CLASS(item);

    if (klass->change_content != NULL)
        klass->change_content(item, old, new);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = instance à consulter.                                 *
*                old  = ancienne vue du contenu chargé analysé.               *
*                new  = nouvelle vue du contenu chargé analysé.               *
*                                                                             *
*  Description : Réagit à un changement de vue du contenu en cours d'analyse. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_editor_item_change_view(GEditorItem *item, GLoadedPanel *old, GLoadedPanel *new)
{
    GEditorItemClass *klass;                /* Classe correspondante       */

    klass = G_EDITOR_ITEM_GET_CLASS(item);

    if (klass->change_view != NULL)
        klass->change_view(item, old, new);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item  = instance à consulter.                                *
*                panel = vue du contenu chargé analysé modifiée.              *
*                                                                             *
*  Description : Réagit à une modification de la vue du contenu analysé.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_editor_item_update_view(GEditorItem *item, GLoadedPanel *panel)
{
    GEditorItemClass *klass;                /* Classe correspondante       */

    klass = G_EDITOR_ITEM_GET_CLASS(item);

    if (klass->update_view != NULL)
        klass->update_view(item, panel);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item   = instance à consulter.                               *
*                panel  = composant d'affichage parcouru.                     *
*                cursor = nouvel emplacement du curseur courant.              *
*                                                                             *
*  Description : Réagit à une modification de la vue du contenu analysé.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_editor_item_track_cursor(GEditorItem *item, GLoadedPanel *panel, const GLineCursor *cursor)
{
    GEditorItemClass *klass;                /* Classe correspondante       */

    klass = G_EDITOR_ITEM_GET_CLASS(item);

    if (klass->track_cursor != NULL)
        klass->track_cursor(item, panel, cursor);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item    = instance à consulter.                              *
*                content = contenu contenant le curseur à représenter.        *
*                cursor  = nouvel emplacement du curseur courant.             *
*                                                                             *
*  Description : Réagit à une modification de la vue du contenu analysé.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_editor_item_focus_cursor(GEditorItem *item, GLoadedContent *content, const GLineCursor *cursor)
{
    GEditorItemClass *klass;                /* Classe correspondante       */

    klass = G_EDITOR_ITEM_GET_CLASS(item);

    if (klass->focus_cursor != NULL)
        klass->focus_cursor(item, content, cursor);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item    = instance à consulter.                              *
*                project = projet concerné par l'évolution.                   *
*                                                                             *
*  Description : Lance une actualisation relative à l'étendue du projet.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_editor_item_update_project_area(GEditorItem *item, GStudyProject *project)
{
    GEditorItemClass *klass;                /* Classe correspondante       */

    klass = G_EDITOR_ITEM_GET_CLASS(item);

    if (klass->update_project != NULL)
        klass->update_project(item, project);

}
