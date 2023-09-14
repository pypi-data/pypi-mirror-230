
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dllist.c - implantation simple des listes doublement chaînées
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#include "dllist.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : new  = nouvel élément à ajouter.                             *
*                head = adresse d'enregistrement de la tête de la liste.      *
*                prev = élément précédent dans la liste.                      *
*                next = élément suivant dans la liste.                        *
*                                                                             *
*  Description : Ajoute un élément dans une liste doublement chaînée.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void __dl_list_add(dl_list_item *new, dl_list_head *head, dl_list_item *prev, dl_list_item *next)
{
    prev->next = new;
    new->prev = prev;

    new->next = next;
    next->prev = new;

    if (*head == NULL)
        *head = new;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : item = élément à supprimer.                                  *
*                head = adresse d'enregistrement de la tête de la liste.      *
*                                                                             *
*  Description : Supprime un élément d'une liste doublement chaînée.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void __dl_list_del(dl_list_item *item, dl_list_head *head)
{
    item->next->prev = item->prev;
    item->prev->next = item->next;

    if (*head == item)
    {
        *head = item->next;
        if (*head == item) *head = NULL;
    }

}
