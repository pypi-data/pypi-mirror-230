
/* Chrysalide - Outil d'analyse de fichiers binaires
 * symbols.h - prototypes pour le panneau d'affichage des symboles
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _GUI_PANELS_SYMBOLS_H
#define _GUI_PANELS_SYMBOLS_H


#include <i18n.h>


#include "../panel.h"



#define PANEL_SYMBOLS_ID "symbols"


#define G_TYPE_SYMBOLS_PANEL            g_symbols_panel_get_type()
#define G_SYMBOLS_PANEL(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SYMBOLS_PANEL, GSymbolsPanel))
#define G_IS_SYMBOLS_PANEL(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SYMBOLS_PANEL))
#define G_SYMBOLS_PANEL_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SYMBOLS_PANEL, GSymbolsPanelClass))
#define G_IS_SYMBOLS_PANEL_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SYMBOLS_PANEL))
#define G_SYMBOLS_PANEL_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SYMBOLS_PANEL, GSymbolsPanelClass))


/* Panneau d'affichage des symboles (instance) */
typedef struct _GSymbolsPanel GSymbolsPanel;

/* Panneau d'affichage des symboles (classe) */
typedef struct _GSymbolsPanelClass GSymbolsPanelClass;


/* Indique le type défini pour un panneau d'affichage des symboles. */
GType g_symbols_panel_get_type(void);

/* Crée un panneau d'affichage des symboles. */
GPanelItem *g_symbols_panel_new(void);



#endif  /* _GUI_PANELS_SYMBOLS_H */
