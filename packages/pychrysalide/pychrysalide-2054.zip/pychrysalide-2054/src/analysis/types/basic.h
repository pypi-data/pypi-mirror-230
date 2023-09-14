
/* Chrysalide - Outil d'analyse de fichiers binaires
 * basic.h - prototypes pour la manipulation des types de données de base
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_TYPES_BASIC_H
#define _ANALYSIS_TYPES_BASIC_H


#include <glib-object.h>


#include "../type.h"



/* Liste des types de base existants */
typedef enum _BaseType
{
    BTP_VOID,                               /* void                        */
    BTP_WCHAR_T,                            /* wchar_t                     */
    BTP_BOOL,                               /* bool                        */
    BTP_CHAR,                               /* char                        */
    BTP_SCHAR,                              /* signed char                 */
    BTP_UCHAR,                              /* unsigned char               */
    BTP_SHORT,                              /* short                       */
    BTP_USHORT,                             /* unsigned short              */
    BTP_INT,                                /* int                         */
    BTP_UINT,                               /* unsigned int                */
    BTP_LONG,                               /* long                        */
    BTP_ULONG,                              /* unsigned long               */
    BTP_LONG_LONG,                          /* long long, __int64          */
    BTP_ULONG_LONG,                         /* unsigned long long, __int64 */
    BTP_INT128,                             /* __int128                    */
    BTP_UINT128,                            /* unsigned __int128           */
    BTP_FLOAT,                              /* float                       */
    BTP_DOUBLE,                             /* double                      */
    BTP_LONG_DOUBLE,                        /* long double, __float80      */
    BTP_FLOAT128,                           /* __float128                  */
    BTP_ELLIPSIS,                           /* ...                         */
    BTP_754R_64,                            /* IEEE 754r float (64 bits)   */
    BTP_754R_128,                           /* IEEE 754r float (128 bits)  */
    BTP_754R_32,                            /* IEEE 754r float (32 bits)   */
    BTP_754R_16,                            /* IEEE 754r float (16 bits)   */
    BTP_754R_N,                             /* IEEE 754r float (n bits)    */
    BTP_CHAR32_T,                           /* char32_t                    */
    BTP_CHAR16_T,                           /* char16_t                    */
    BTP_AUTO,                               /* auto                        */
    BTP_DECL_AUTO,                          /* decltype(auto)              */

    BTP_INVALID

} BaseType;


#define G_TYPE_BASIC_TYPE            g_basic_type_get_type()
#define G_BASIC_TYPE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BASIC_TYPE, GBasicType))
#define G_IS_BASIC_TYPE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BASIC_TYPE))
#define G_BASIC_TYPE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BASIC_TYPE, GBasicTypeClass))
#define G_IS_BASIC_TYPE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BASIC_TYPE))
#define G_BASIC_TYPE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BASIC_TYPE, GBasicTypeClass))


/* Description de type basique (instance) */
typedef struct _GBasicType GBasicType;

/* Description de type basique (classe) */
typedef struct _GBasicTypeClass GBasicTypeClass;


/* Indique le type défini pour un type basique. */
GType g_basic_type_get_type(void);

/* Crée une représentation de type basique. */
GDataType *g_basic_type_new(BaseType);

/* Fournit le type de base géré par le type. */
BaseType g_basic_type_get_base(const GBasicType *);



#endif  /* _ANALYSIS_TYPES_BASIC_H */
