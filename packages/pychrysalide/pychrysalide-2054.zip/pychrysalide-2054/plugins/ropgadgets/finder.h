
/* Chrysalide - Outil d'analyse de fichiers binaires
 * finder.h - prototypes pour la recherche de gadgets pour ROP
 *
 * Copyright (C) 2015-2018 Cyrille Bagard
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


#ifndef _PLUGINS_ROPGADGETS_FINDER_H
#define _PLUGINS_ROPGADGETS_FINDER_H


#include <arch/instruction.h>
#include <format/executable.h>



/* Actualise la barre de progression affichée. */
typedef void (* update_search_progress_cb) (GObject *, gdouble);


/* Chaîne d'instructions idéales */
typedef struct _rop_chain
{
    GArchInstruction **instrs;              /* Instructions bien combinées */
    size_t count;                           /* Taille de cette liste       */

} rop_chain;

/* Catégorisation des résultats */
typedef struct _found_rop_list
{
    const char *category;                   /* Désignation du groupe       */

    rop_chain **gadgets;                    /* Gadgets pour ROP trouvés    */
    size_t count;                           /* Taille de cette liste       */

} found_rop_list;


/* Etablit une liste de tous les gadgets présents. */
found_rop_list *list_all_gadgets(GExeFormat *, unsigned int, update_search_progress_cb, GObject *, size_t *);

/* Libère la mémoire des gadgets trouvés pour du ROP. */
void free_rop_list(found_rop_list *);



#endif  /* _PLUGINS_ROPGADGETS_FINDER_H */
