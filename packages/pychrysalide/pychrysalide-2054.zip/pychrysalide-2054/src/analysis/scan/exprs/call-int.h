
/* Chrysalide - Outil d'analyse de fichiers binaires
 * call-int.h - prototypes internes pour l'organisation d'un appel à un élément de scan enregistré
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


#ifndef _ANALYSIS_SCAN_EXPRS_CALL_INT_H
#define _ANALYSIS_SCAN_EXPRS_CALL_INT_H


#include "call.h"


#include "access-int.h"



/* Exécution d'une fonction auxiliaire d'analyse (instance) */
struct _GScanPendingCall
{
    GScanNamedAccess parent;                /* A laisser en premier        */

    GScanExpression **args;                 /* Arguments d'appel fournis   */
    size_t count;                           /* Quantité de ces arguments   */

};

/* Exécution d'une fonction auxiliaire d'analyse (classe) */
struct _GScanPendingCallClass
{
    GScanNamedAccessClass parent;           /* A laisser en premier        */

};


/* Met en place une expression d'appel. */
bool g_scan_pending_call_create(GScanPendingCall *, const sized_string_t *, GScanExpression **, size_t);



#endif  /* _ANALYSIS_SCAN_EXPRS_CALL_INT_H */
