
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cse.h - prototypes pour la manipulation des types classes / structures / énumérations
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


#ifndef _ANALYSIS_TYPES_CSE_H
#define _ANALYSIS_TYPES_CSE_H


#include <glib-object.h>


#include "../type.h"



#define G_TYPE_CLASS_ENUM_TYPE            g_class_enum_type_get_type()
#define G_CLASS_ENUM_TYPE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_CLASS_ENUM_TYPE, GClassEnumType))
#define G_IS_CLASS_ENUM_TYPE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_CLASS_ENUM_TYPE))
#define G_CLASS_ENUM_TYPE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_CLASS_ENUM_TYPE, GClassEnumTypeClass))
#define G_IS_CLASS_ENUM_TYPE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_CLASS_ENUM_TYPE))
#define G_CLASS_ENUM_TYPE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_CLASS_ENUM_TYPE, GClassEnumTypeClass))


/* Description de type classe/structure et énumération (instance) */
typedef struct _GClassEnumType GClassEnumType;

/* Description de type classe/structure et énumération (classe) */
typedef struct _GClassEnumTypeClass GClassEnumTypeClass;


/* Type pris en compte */
typedef enum _ClassEnumKind
{
    CEK_UNKNOWN,                            /* Statut inconnu              */
    CEK_STRUCT,                             /* Structure                   */
    CEK_ENUM,                               /* Enumération                 */
    CEK_CLASS,                              /* Classe                      */
    CEK_NAMESPACE,                          /* Espace de nom               */
    CEK_VIRTUAL_TABLE,                      /* Table virtuelle             */
    CEK_VIRTUAL_STRUCT,                     /* Indice de construction VT   */

    CEK_COUNT

} ClassEnumKind;


/* Indique le type défini pour un type classe ou assimilé. */
GType g_class_enum_type_get_type(void);

/* Crée une représentation de classe, structure ou énumération. */
GDataType *g_class_enum_type_new(ClassEnumKind, char *);

/* Fournit le type pris en compte géré par le type. */
ClassEnumKind g_class_enum_type_get_kind(const GClassEnumType *);

/* Donne la désignation de la classe / structure / énumération. */
const char *g_class_enum_type_get_name(const GClassEnumType *);



#endif  /* _ANALYSIS_TYPES_CSE_H */
