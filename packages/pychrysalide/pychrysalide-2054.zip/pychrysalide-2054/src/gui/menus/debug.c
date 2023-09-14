
/* Chrysalide - Outil d'analyse de fichiers binaires
 * debug.c - gestion du menu 'Débogage'
 *
 * Copyright (C) 2011-2018 Cyrille Bagard
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


#include "debug.h"


#include <string.h>


#include <i18n.h>


#include "../../gtkext/easygtk.h"



/* Réagit avec le menu "Débogage -> Continuer". */
static void mcb_debug_continue(GtkMenuItem *, GObject *);

/* Réagit avec le menu "Débogage -> Continuer jusqu'à...". */
static void mcb_debug_continue_to(GtkMenuItem *, GObject *);

/* Réagit avec le menu "Débogage -> Mettre en pause". */
static void mcb_debug_pause(GtkMenuItem *, GObject *);

/* Réagit avec le menu "Débogage -> Redémarrer". */
static void mcb_debug_restart(GtkMenuItem *, GObject *);

/* Réagit avec le menu "Débogage -> Arrêter". */
static void mcb_debug_close(GtkMenuItem *, GObject *);

/* Réagit avec le menu "Débogage -> Avancer pas à pas en ...". */
static void mcb_debug_step_into(GtkMenuItem *, GObject *);

/* Réagit avec le menu "Débogage -> Avancer pas à pas en ...". */
static void mcb_debug_step_over(GtkMenuItem *, GObject *);

/* Réagit avec le menu "Débogage -> Visiter les blocs ...". */
static void mcb_debug_visit_blocks_into(GtkMenuItem *, GObject *);

/* Réagit avec le menu "Débogage -> Visiter les blocs ...". */
static void mcb_debug_visit_blocks_over(GtkMenuItem *, GObject *);

/* Réagit avec le menu "Débogage -> Continuer jusqu'au retour". */
static void mcb_debug_return(GtkMenuItem *, GObject *);

/* Réagit avec le menu "Débogage -> Options de débogage". */
static void mcb_debug_options(GtkMenuItem *, GObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : builder = constructeur avec l'ensemble des références.       *
*                                                                             *
*  Description : Complète la définition du menu "Débogage".                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void setup_menu_debug_callbacks(GtkBuilder *builder)
{
    gtk_builder_add_callback_symbols(builder,
                                     BUILDER_CALLBACK(mcb_debug_continue),
                                     BUILDER_CALLBACK(mcb_debug_continue_to),
                                     BUILDER_CALLBACK(mcb_debug_pause),
                                     BUILDER_CALLBACK(mcb_debug_restart),
                                     BUILDER_CALLBACK(mcb_debug_close),
                                     BUILDER_CALLBACK(mcb_debug_step_into),
                                     BUILDER_CALLBACK(mcb_debug_step_over),
                                     BUILDER_CALLBACK(mcb_debug_visit_blocks_into),
                                     BUILDER_CALLBACK(mcb_debug_visit_blocks_over),
                                     BUILDER_CALLBACK(mcb_debug_return),
                                     BUILDER_CALLBACK(mcb_debug_options),
                                     NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                ref      = adresse de l'espace de référencement global.      *
*                                                                             *
*  Description : Réagit avec le menu "Débogage -> Continuer".                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_debug_continue(GtkMenuItem *menuitem, GObject *ref)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                ref      = adresse de l'espace de référencement global.      *
*                                                                             *
*  Description : Réagit avec le menu "Débogage -> Continuer jusqu'à...".      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_debug_continue_to(GtkMenuItem *menuitem, GObject *ref)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                ref      = adresse de l'espace de référencement global.      *
*                                                                             *
*  Description : Réagit avec le menu "Débogage -> Mettre en pause".           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_debug_pause(GtkMenuItem *menuitem, GObject *ref)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                ref      = adresse de l'espace de référencement global.      *
*                                                                             *
*  Description : Réagit avec le menu "Débogage -> Redémarrer".                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_debug_restart(GtkMenuItem *menuitem, GObject *ref)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                ref      = adresse de l'espace de référencement global.      *
*                                                                             *
*  Description : Réagit avec le menu "Débogage -> Arrêter".                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_debug_close(GtkMenuItem *menuitem, GObject *ref)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                ref      = adresse de l'espace de référencement global.      *
*                                                                             *
*  Description : Réagit avec le menu "Débogage -> Avancer pas à pas en ...".  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_debug_step_into(GtkMenuItem *menuitem, GObject *ref)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                ref      = adresse de l'espace de référencement global.      *
*                                                                             *
*  Description : Réagit avec le menu "Débogage -> Avancer pas à pas en ...".  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_debug_step_over(GtkMenuItem *menuitem, GObject *ref)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                ref      = adresse de l'espace de référencement global.      *
*                                                                             *
*  Description : Réagit avec le menu "Débogage -> Visiter les blocs ...".     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_debug_visit_blocks_into(GtkMenuItem *menuitem, GObject *ref)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                ref      = adresse de l'espace de référencement global.      *
*                                                                             *
*  Description : Réagit avec le menu "Débogage -> Visiter les blocs ...".     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_debug_visit_blocks_over(GtkMenuItem *menuitem, GObject *ref)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                ref      = adresse de l'espace de référencement global.      *
*                                                                             *
*  Description : Réagit avec le menu "Débogage -> Continuer jusqu'au retour". *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_debug_return(GtkMenuItem *menuitem, GObject *ref)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : menuitem = élément de menu sélectionné.                      *
*                ref      = adresse de l'espace de référencement global.      *
*                                                                             *
*  Description : Réagit avec le menu "Débogage -> Options de débogage".       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mcb_debug_options(GtkMenuItem *menuitem, GObject *ref)
{

}
