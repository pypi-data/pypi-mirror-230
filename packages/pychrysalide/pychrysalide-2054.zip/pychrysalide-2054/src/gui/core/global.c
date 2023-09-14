
/* Chrysalide - Outil d'analyse de fichiers binaires
 * global.c - conservation de variables globales à vocation graphique
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


#include "global.h"



/* Constructeur principal de l'éditeur */
static GtkBuilder *_builder = NULL;

/* Composant d'affichage en tuile */
static GtkTiledGrid *_grid = NULL;

/* Barre de statut principale */
static GtkStatusStack *_status = NULL;

/* Contenu en cours d'étude ou NULL */
static GLoadedContent *_current_content = NULL;

G_LOCK_DEFINE_STATIC(_cc_mutex);

/* Suivi du panneau d'affichage courant ou NULL */
static GLoadedPanel *_current_view = NULL;

G_LOCK_DEFINE_STATIC(_cv_mutex);



/******************************************************************************
*                                                                             *
*  Paramètres  : editor = fenêtre principale à référencer.                    *
*                                                                             *
*  Description : Note l'adresse du constructeur principal de l'éditeur.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_editor_builder(GtkBuilder *builder)
{
    g_clear_object(&_builder);

    _builder = builder;

    if (builder != NULL)
        g_object_ref(G_OBJECT(builder));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit l'adresse du constructeur principal de l'éditeur.    *
*                                                                             *
*  Retour      : Constructeur principal référencé.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkBuilder *get_editor_builder(void)
{
    GtkBuilder *result;                     /* Instance à retourner        */

    result = _builder;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit l'adresse de la fenêtre principale de l'éditeur.     *
*                                                                             *
*  Retour      : Fenêtre principale référencée.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWindow *get_editor_window(void)
{
    GtkWindow *result;                      /* Instance à retourner        */

    result = GTK_WINDOW(gtk_builder_get_object(_builder, "window"));

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : grid = composant GTK à conserver.                            *
*                                                                             *
*  Description : Note l'adresse du composant d'affichage en tuiles.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_tiled_grid(GtkTiledGrid *grid)
{
    _grid = grid;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit l'adresse du composant d'affichage en tuiles.        *
*                                                                             *
*  Retour      : Composant GTK à manipuler.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkTiledGrid *get_tiled_grid(void)
{
    return _grid;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Note l'adresse de la barre de statut principale.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_global_status(GtkStatusStack *status)
{
    _status = status;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit l'adresse de la barre de statut principale.          *
*                                                                             *
*  Retour      : Barre de statut à tenir informée.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkStatusStack *get_global_status(void)
{
    return _status;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = instance de contenu chargé.                        *
*                                                                             *
*  Description : Définit le contenu actif en cours d'étude.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_current_content(GLoadedContent *content)
{
    G_LOCK(_cc_mutex);

    if (_current_content != NULL)
        g_object_unref(G_OBJECT(_current_content));

    _current_content = content;

    G_UNLOCK(_cc_mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit le contenu actif en cours d'étude.                   *
*                                                                             *
*  Retour      : Instance courante de contenu étudié ou NULL.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GLoadedContent *get_current_content(void)
{
    GLoadedContent *result;                  /* Instance à retourner        */

    G_LOCK(_cc_mutex);

    result = _current_content;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    G_UNLOCK(_cc_mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view = représentation courante de contenu.                   *
*                                                                             *
*  Description : Définit l'affichage de contenu courant.                      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_current_view(GLoadedPanel *view)
{
    G_LOCK(_cv_mutex);

    if (_current_view != NULL)
        g_object_unref(G_OBJECT(_current_view));

    _current_view = view;

    G_UNLOCK(_cv_mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit l'affichage de contenu courant.                      *
*                                                                             *
*  Retour      : Instance en place ou NULL si aucune.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GLoadedPanel *get_current_view(void)
{
    GLoadedPanel *result;                   /* Instance à retourner        */

    G_LOCK(_cv_mutex);

    result = _current_view;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    G_UNLOCK(_cv_mutex);

    return result;

}
