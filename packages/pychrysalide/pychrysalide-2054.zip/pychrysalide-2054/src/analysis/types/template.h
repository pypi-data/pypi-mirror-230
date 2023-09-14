
/* Chrysalide - Outil d'analyse de fichiers binaires
 * template.h - prototypes pour la manipulation des types reposant sur des gabarits
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


#ifndef _ANALYSIS_TYPES_TEMPLATE_H
#define _ANALYSIS_TYPES_TEMPLATE_H


#include <glib-object.h>


#include "../type.h"



#define G_TYPE_TEMPLATE_TYPE            g_template_type_get_type()
#define G_TEMPLATE_TYPE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_TEMPLATE_TYPE, GTemplateType))
#define G_IS_TEMPLATE_TYPE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_TEMPLATE_TYPE))
#define G_TEMPLATE_TYPE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_TEMPLATE_TYPE, GTemplateTypeClass))
#define G_IS_TEMPLATE_TYPE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_TEMPLATE_TYPE))
#define G_TEMPLATE_TYPE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_TEMPLATE_TYPE, GTemplateTypeClass))


/* Description de type reposant sur des gabarits (instance) */
typedef struct _GTemplateType GTemplateType;

/* Description de type reposant sur des gabarits (classe) */
typedef struct _GTemplateTypeClass GTemplateTypeClass;


/* Indique le type défini pour un type reposant sur des gabarits. */
GType g_template_type_get_type(void);

/* Crée une représentation de type reposant sur des gabarits. */
GDataType *g_template_type_new(void);

/* Indique la désignation principale du type. */
const char *g_template_type_get_name(GTemplateType *);

/* Précise la désignation principale du type. */
void g_template_type_set_name(GTemplateType *, const char *);

/* Ajoute un paramètre à un gabarit. */
void g_template_type_add_param(GTemplateType *, GDataType *);

/* Indique le nombre de paramètres associés au gabarit. */
size_t g_template_type_count_params(const GTemplateType *);

/* Fournit un paramètre donné du gabarit. */
GDataType *g_template_type_get_param(const GTemplateType *, size_t);



#endif  /* _ANALYSIS_TYPES_TEMPLATE_H */
