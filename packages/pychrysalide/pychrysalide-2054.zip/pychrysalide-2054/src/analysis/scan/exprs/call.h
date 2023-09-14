
/* Chrysalide - Outil d'analyse de fichiers binaires
 * call.h - prototypes pour l'organisation d'un appel à un élément de scan enregistré
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


#ifndef _ANALYSIS_SCAN_EXPRS_CALL_H
#define _ANALYSIS_SCAN_EXPRS_CALL_H


#include "../expr.h"
#include "../../../common/szstr.h"



#define G_TYPE_SCAN_PENDING_CALL            g_scan_pending_call_get_type()
#define G_SCAN_PENDING_CALL(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_PENDING_CALL, GScanPendingCall))
#define G_IS_SCAN_PENDING_CALL(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_PENDING_CALL))
#define G_SCAN_PENDING_CALL_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_PENDING_CALL, GScanPendingCallClass))
#define G_IS_SCAN_PENDING_CALL_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_PENDING_CALL))
#define G_SCAN_PENDING_CALL_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_PENDING_CALL, GScanPendingCallClass))


/* Exécution d'une fonction auxiliaire d'analyse (instance) */
typedef struct _GScanPendingCall GScanPendingCall;

/* Exécution d'une fonction auxiliaire d'analyse (classe) */
typedef struct _GScanPendingCallClass GScanPendingCallClass;


/* Indique le type défini pour un appel de fonction enregistrée. */
GType g_scan_pending_call_get_type(void);

/* Organise un appel de fonction avec ses arguments. */
GScanExpression *g_scan_pending_call_new(const sized_string_t *, GScanExpression **, size_t);



#endif  /* _ANALYSIS_SCAN_EXPRS_CALL_H */
