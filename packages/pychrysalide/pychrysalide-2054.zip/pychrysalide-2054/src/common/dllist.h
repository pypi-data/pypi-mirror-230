
/* Chrysalide - Outil d'analyse de fichiers binaires
 * dllist.h - prototypes de l'implantation simple des listes doublement chaînées
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


#ifndef _COMMON_DLLIST_H
#define _COMMON_DLLIST_H


#include "macros.h"



/* Structure à inclure en tête de structure */
typedef struct _dl_list_item
{
    struct _dl_list_item *prev;             /* Elément précédent           */
    struct _dl_list_item *next;             /* Elément suivant             */

} dl_list_item;

typedef dl_list_item *dl_list_head;


#define DL_LIST_ITEM(name) dl_list_item name


#define DL_LIST_ITEM_INIT(item)                                                     \
    do                                                                              \
    {                                                                               \
        (item)->prev = (item);                                                      \
        (item)->next = (item);                                                      \
                                                                                    \
    } while(0)


/* Ajoute un élément dans une liste doublement chaînée. */
void __dl_list_add(dl_list_item *, dl_list_head *, dl_list_item *, dl_list_item *);

/* Supprime un élément d'une liste doublement chaînée. */
void __dl_list_del(dl_list_item *, dl_list_head *);


#define dl_list_empty(head)                                                         \
    ((head) == NULL)

#define dl_list_last(head, type, member)                                            \
    (dl_list_empty(head) ? NULL : (type *)container_of(head->member.prev, type, member))

#define dl_list_add(new, head, type, member)                                        \
    do                                                                              \
    {                                                                               \
        dl_list_item *hmbr = (dl_list_empty(*(head)) ? NULL : &(*head)->member);    \
        __dl_list_add(&new->member, &hmbr,                                          \
                      dl_list_empty(*(head)) ? &new->member : hmbr->prev,           \
                      dl_list_empty(*(head)) ? &new->member : hmbr);                \
        *(head) = new;                                                              \
    }                                                                               \
    while (0)

#define dl_list_add_before(new, head, pos, member)                                  \
    do                                                                              \
    {                                                                               \
        pos->member.prev->next = &new->member;                                      \
        new->member.prev = pos->member.prev;                                        \
        pos->member.prev = &new->member;                                            \
        new->member.next = &pos->member;                                            \
        if (pos == *head) *head = new;                                              \
    }                                                                               \
    while (0)

#define dl_list_add_tail(new, head, type, member)                                   \
    do                                                                              \
    {                                                                               \
        dl_list_item *hmbr = (dl_list_empty(*(head)) ? NULL : &(*head)->member);    \
        __dl_list_add(&new->member, &hmbr,                                          \
                      dl_list_empty(*(head)) ? &new->member : hmbr->prev,           \
                      dl_list_empty(*(head)) ? &new->member : hmbr);                \
        *(head) = container_of(hmbr, type, member);                                 \
    }                                                                               \
    while (0)

#define dl_list_del(item, head, type, member)                                       \
    do                                                                              \
    {                                                                               \
        dl_list_item *hmbr = &(*head)->member;                                      \
        __dl_list_del(&item->member, &hmbr);                                        \
        *(head) = (hmbr ? container_of(hmbr, type, member) : NULL);                 \
        DL_LIST_ITEM_INIT(&item->member);                                           \
    }                                                                               \
    while(0)

#define dl_list_merge(head1, head2, type, member)                                   \
    do                                                                              \
    {                                                                               \
        if (dl_list_empty(*head1)) *head1 = *head2;                                 \
        else if (!dl_list_empty(*head2))                                            \
        {                                                                           \
            dl_list_item *hmbr1 = &(*head1)->member;                                \
            dl_list_item *hmbr2 = &(*head2)->member;                                \
            dl_list_item *mid = hmbr1->prev;                                        \
            mid->next = hmbr2;                                                      \
            hmbr1->prev = hmbr2->prev;                                              \
            hmbr2->prev->next = hmbr1;                                              \
            hmbr2->prev = mid;                                                      \
        }                                                                           \
    }                                                                               \
    while(0)

#define dl_list_push dl_list_add_tail

#define dl_list_pop(head, type, member)                                             \
    ({                                                                              \
        type *_result = *head;/* FIXME : ARgh ! */                                  \
        dl_list_del(_result, head, type, member);                                   \
        _result;                                                                    \
    })

#define dl_list_next_iter(iter, head, type, member)                                 \
    (iter->member.next == &head->member ?                                           \
     NULL : container_of(iter->member.next, type, member))

#define dl_list_prev_iter(iter, head, type, member)                                 \
    (&iter->member == &head->member ?                                               \
     NULL : container_of(iter->member.prev, type, member))

#define dl_list_for_each(pos, head, type, member)                                   \
	for (pos = head;                                                                \
         pos != NULL;                                                               \
         pos = dl_list_next_iter(pos, (head), type, member))

#define dl_list_next_iter_safe(iter, head, type, member)                            \
    (iter == NULL || iter->member.next == &(*head)->member ?                        \
     NULL : container_of(iter->member.next, type, member))

#define dl_list_for_each_safe(pos, head, next, type, member)                        \
	for (pos = *head,                                                               \
             next = dl_list_next_iter_safe(pos, (head), type, member);              \
         pos != NULL;                                                               \
         pos = next,                                                                \
             next = dl_list_next_iter_safe(pos, (head), type, member))

#define dl_list_for_each_rev(pos, head, type, member)                               \
	for (pos = dl_list_last(head, type, member);                                    \
         pos != NULL;                                                               \
         pos = dl_list_prev_iter(pos, (head), type, member))



#endif  /* _COMMON_DLLIST_H */
