
/* Chrysalide - Outil d'analyse de fichiers binaires
 * portions.h - prototypes pour la navigation dans les portions de binaire
 *
 * Copyright (C) 2013-2016 Cyrille Bagard
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


#ifndef _GUI_TB_PORTIONS_H
#define _GUI_TB_PORTIONS_H


#include "tbitem.h"



#define PORTIONS_TBITEM_ID "portions"


#define G_TYPE_PORTIONS_TBITEM               g_portions_tbitem_get_type()
#define G_PORTIONS_TBITEM(obj)               (G_TYPE_CHECK_INSTANCE_CAST((obj), g_portions_tbitem_get_type(), GToolbarItem))
#define G_IS_PORTIONS_TBITEM(obj)            (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_portions_tbitem_get_type()))
#define G_PORTIONS_TBITEM_CLASS(klass)       (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_PORTIONS_TBITEM, GToolbarItemClass))
#define G_IS_PORTIONS_TBITEM_CLASS(klass)    (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_PORTIONS_TBITEM))
#define G_PORTIONS_TBITEM_GET_CLASS(obj)     (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_PORTIONS_TBITEM, GToolbarItemClass))


/* Elément réactif présentant des portions de binaire (instance) */
typedef struct _GPortionsTbItem GPortionsTbItem;

/* Elément réactif présentant des portions de binaire (classe) */
typedef struct _GPortionsTbItemClass GPortionsTbItemClass;


/* Indique le type défini pour un affichage de portions destiné à une barre d'outils. */
GType g_portions_tbitem_get_type(void);

/* Crée une sélection de fichier réactive pour barre d'outils. */
GEditorItem *g_portions_tbitem_new(GObject *ref);



#endif  /* _GUI_TB_PORTIONS_H */
