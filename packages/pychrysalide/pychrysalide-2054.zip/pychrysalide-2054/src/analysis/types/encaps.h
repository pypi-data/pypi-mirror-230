
/* Chrysalide - Outil d'analyse de fichiers binaires
 * encaps.h - prototypes pour la manipulation des types de données encapsulés
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


#ifndef _ANALYSIS_TYPES_ENCAPS_H
#define _ANALYSIS_TYPES_ENCAPS_H


#include <glib-object.h>


#include "../type.h"



#define G_TYPE_ENCAPSULATED_TYPE            g_encapsulated_type_get_type()
#define G_ENCAPSULATED_TYPE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ENCAPSULATED_TYPE, GEncapsulatedType))
#define G_IS_ENCAPSULATED_TYPE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ENCAPSULATED_TYPE))
#define G_ENCAPSULATED_TYPE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ENCAPSULATED_TYPE, GEncapsulatedTypeClass))
#define G_IS_ENCAPSULATED_TYPE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ENCAPSULATED_TYPE))
#define G_ENCAPSULATED_TYPE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ENCAPSULATED_TYPE, GEncapsulatedTypeClass))


/* Description de type encapsulé (instance) */
typedef struct _GEncapsulatedType GEncapsulatedType;

/* Description de type encapsulé (classe) */
typedef struct _GEncapsulatedTypeClass GEncapsulatedTypeClass;


/* Cas d'encapsulation possibles */
typedef enum _EncapsulationType
{
    ECT_POINTER,                            /* Pointeur                    */
    ECT_ARRAY,                              /* Tableau                     */
    ECT_REFERENCE,                          /* Référence                   */
    ECT_RVALUE_REF,                         /* Référence ?? (C++0x)        */
    ECT_COMPLEX,                            /* Complexe (C 2000)           */
    ECT_IMAGINARY,                          /* Imaginaire (C 2000)         */

    ECT_COUNT

} EncapsulationType;


/* Indique le type défini pour un type encapsulé. */
GType g_encapsulated_type_get_type(void);

/* Crée une représentation de variable dérivée. */
GDataType *g_encapsulated_type_new(EncapsulationType, GDataType *);

/* Fournit le type d'encapsulation gérée par le type. */
EncapsulationType g_encapsulated_type_get_etype(const GEncapsulatedType *);

/* Fournit le type encapsulée dans le type. */
GDataType *g_encapsulated_type_get_item(const GEncapsulatedType *);

/* Fournit la dimension éventuellement associée au type. */
size_t g_encapsulated_type_get_dimension(const GEncapsulatedType *);

/* Définit la dimension éventuellement associée au type. */
void g_encapsulated_type_set_dimension(GEncapsulatedType *, size_t);



#endif  /* _ANALYSIS_TYPES_ENCAPS_H */
