
/* Chrysalide - Outil d'analyse de fichiers binaires
 * modifier-int.h - prototypes internes pour la modification d'une séquence d'octets pour un motif recherché
 *
 * Copyright (C) 2023 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_SCAN_MODIFIER_INT_H
#define _ANALYSIS_SCAN_MODIFIER_INT_H


#include "modifier.h"



/* Fournit le nom d'appel d'un modificateur pour motif. */
typedef char * (* get_scan_modifier_name_fc) (const GScanTokenModifier *);

/* Transforme une séquence d'octets pour motif de recherche. */
typedef bool (* transform_scan_token_fc) (const GScanTokenModifier *, const sized_binary_t *, sized_binary_t **, size_t *);


/* Transformation d'une séquence d'octets en une ou plusieurs autres formes (instance) */
struct _GScanTokenModifier
{
    GObject parent;                         /* A laisser en premier        */

};

/* Transformation d'une séquence d'octets en une ou plusieurs autres formes (classe) */
struct _GScanTokenModifierClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    get_scan_modifier_name_fc get_name;     /* Fourniture du nom d'appel   */

    transform_scan_token_fc transform;      /* Opération de transformation */

};



#endif  /* _ANALYSIS_SCAN_MODIFIER_INT_H */
