
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


#ifndef _GUI_TBITEM_INT_H
#define _GUI_TBITEM_INT_H


#include "../item-int.h"



/* Elément réactif pour barre d'outils de l'éditeur (instance) */
struct _GToolbarItem
{
    GEditorItem parent;                     /* A laisser en premier        */

};


/* Elément réactif pour barre d'outils de l'éditeur (classe) */
struct _GToolbarItemClass
{
    GEditorItemClass parent;                /* A laisser en premier        */

};



/* Termine la préparation d'un élément de barre d'outils. */
void g_toolbar_item_setup(GToolbarItem *, GObject *);



#endif  /* _GUI_TBITEM_INT_H */
