
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.c - instances d'actions d'un greffon donné
 *
 * Copyright (C) 2010-2016 Cyrille Bagard
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


#include "context.h"


#include "context-int.h"



/* Initialise la classe des instances de greffon. */
static void g_plugin_context_class_init(GPluginContextClass *);

/* Initialise une instance d'instance de greffon. */
static void g_plugin_context_init(GPluginContext *);



/* Indique le type défini pour une instance de greffon. */
G_DEFINE_TYPE(GPluginContext, g_plugin_context, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des instances de greffon.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_plugin_context_class_init(GPluginContextClass *klass)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : context = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance d'instance de greffon.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_plugin_context_init(GPluginContext *context)
{

}
