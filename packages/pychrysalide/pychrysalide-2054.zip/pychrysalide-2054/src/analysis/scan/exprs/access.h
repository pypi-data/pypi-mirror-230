
/* Chrysalide - Outil d'analyse de fichiers binaires
 * access.h - prototypes pour l'accès à un élément d'expression sous-jacent
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


#ifndef _ANALYSIS_SCAN_EXPRS_ACCESS_H
#define _ANALYSIS_SCAN_EXPRS_ACCESS_H


#include "../expr.h"
#include "../item.h"
#include "../../../common/szstr.h"



#define G_TYPE_SCAN_NAMED_ACCESS            g_scan_named_access_get_type()
#define G_SCAN_NAMED_ACCESS(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_NAMED_ACCESS, GScanNamedAccess))
#define G_IS_SCAN_NAMED_ACCESS(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_NAMED_ACCESS))
#define G_SCAN_NAMED_ACCESS_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_NAMED_ACCESS, GScanNamedAccessClass))
#define G_IS_SCAN_NAMED_ACCESS_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_NAMED_ACCESS))
#define G_SCAN_NAMED_ACCESS_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_NAMED_ACCESS, GScanNamedAccessClass))


/* Accès à un élément d'expression sous-jacent (instance) */
typedef struct _GScanNamedAccess GScanNamedAccess;

/* Accès à un élément d'expression sous-jacent (classe) */
typedef struct _GScanNamedAccessClass GScanNamedAccessClass;


/* Indique le type défini pour un appel de fonction enregistrée. */
GType g_scan_named_access_get_type(void);

/* Organise un accès à un élément d'expression sous-jacent. */
GScanExpression *g_scan_named_access_new(const sized_string_t *);

/* Reproduit un accès en place dans une nouvelle instance. */
GScanExpression *g_scan_named_access_duplicate(const GScanNamedAccess *, GRegisteredItem *);

/* Définit une base de recherche pour la cible d'accès. */
void g_scan_named_access_set_base(GScanNamedAccess *, GRegisteredItem *);

/* Complète la chaine d'accès à des expressions. */
void g_scan_named_access_attach_next(GScanNamedAccess *, GScanNamedAccess *);



#endif  /* _ANALYSIS_SCAN_EXPRS_ACCESS_H */
