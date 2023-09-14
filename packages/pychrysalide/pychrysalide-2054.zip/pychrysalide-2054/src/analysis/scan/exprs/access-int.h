
/* Chrysalide - Outil d'analyse de fichiers binaires
 * access-int.h - prototypes internes pour l'accès à un élément d'expression sous-jacent
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


#ifndef _ANALYSIS_SCAN_EXPRS_ACCESS_INT_H
#define _ANALYSIS_SCAN_EXPRS_ACCESS_INT_H


#include "access.h"


#include "../expr-int.h"



/* Reproduit un accès en place dans une nouvelle instance. */
typedef void (* copy_scan_access_fc) (GScanNamedAccess *, const GScanNamedAccess *);

/* Accès à un élément d'expression sous-jacent (instance) */
struct _GScanNamedAccess
{
    GScanExpression parent;                 /* A laisser en premier        */

    union
    {
        GRegisteredItem *base;              /* Base de recherche           */
        GRegisteredItem *resolved;          /* Elément ciblé au final      */
        GObject *any;                       /* Accès indistinct            */
    };

    char *target;                           /* Cible dans l'espace         */

    struct _GScanNamedAccess *next;         /* Evnetuel prochain élément   */

};

/* Accès à un élément d'expression sous-jacent (classe) */
struct _GScanNamedAccessClass
{
    GScanExpressionClass parent;            /* A laisser en premier        */

    copy_scan_access_fc copy;               /* Reproduction d'accès        */

};


/* Met en place une expression d'accès. */
bool g_scan_named_access_create(GScanNamedAccess *, const sized_string_t *);

/* Prépare une réduction en menant une résolution locale. */
GRegisteredItem *_g_scan_named_access_prepare_reduction(const GScanNamedAccess *, GScanContext *, GScanScope *);



#endif  /* _ANALYSIS_SCAN_EXPRS_ACCESS_INT_H */
