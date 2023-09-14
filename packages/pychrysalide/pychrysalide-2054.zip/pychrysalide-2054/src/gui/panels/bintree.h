
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bintree.h - prototypes pour le panneau d'accueil par défaut
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#ifndef _GUI_PANELS_BINTREE_H
#define _GUI_PANELS_BINTREE_H


#include <i18n.h>


#include "../panel.h"



#define PANEL_BINTREE_ID "bintree"


#define G_TYPE_BINTREE_PANEL               g_bintree_panel_get_type()
#define G_BINTREE_PANEL(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_bintree_panel_get_type(), GBintreePanel))
#define G_IS_BINTREE_PANEL(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_bintree_panel_get_type()))
#define G_BINTREE_PANEL_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BINTREE_PANEL, GBintreePanelClass))
#define G_IS_BINTREE_PANEL_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BINTREE_PANEL))
#define G_BINTREE_PANEL_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BINTREE_PANEL, GBintreePanelClass))


/* Panneau de présentation des portions (instance) */
typedef struct _GBintreePanel GBintreePanel;

/* Panneau de présentation des portions (classe) */
typedef struct _GBintreePanelClass GBintreePanelClass;


/* Indique le type défini pour un panneau d'affichage des portions. */
GType g_bintree_panel_get_type(void);

/* Crée un panneau présentant l'arborescence des portions. */
GPanelItem *g_bintree_panel_new(void);



#endif  /* _GUI_PANELS_BINTREE_H */
