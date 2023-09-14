
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tbitem.h - prototypes pour la gestion des éléments réactifs spécifiques à la barre d'outils
 *
 * Copyright (C) 2014-2016 Cyrille Bagard
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


#ifndef _GUI_TBITEM_H
#define _GUI_TBITEM_H


#include "../item.h"



#define G_TYPE_TOOLBAR_ITEM               g_toolbar_item_get_type()
#define G_TOOLBAR_ITEM(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_toolbar_item_get_type(), GToolbarItem))
#define G_IS_TOOLBAR_ITEM(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_toolbar_item_get_type()))
#define G_TOOLBAR_ITEM_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_TOOLBAR_ITEM, GToolbarItemClass))
#define G_IS_TOOLBAR_ITEM_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_TOOLBAR_ITEM))
#define G_TOOLBAR_ITEM_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_TOOLBAR_ITEM, GToolbarItemClass))


/* Elément réactif pour barre d'outils de l'éditeur (instance) */
typedef struct _GToolbarItem GToolbarItem;

/* Elément réactif pour barre d'outils de l'éditeur (classe) */
typedef struct _GToolbarItemClass GToolbarItemClass;


/* Indique le type défini pour un élément destiné à une barre d'outils. */
GType g_toolbar_item_get_type(void);



#endif  /* _GUI_TBITEM_H */
