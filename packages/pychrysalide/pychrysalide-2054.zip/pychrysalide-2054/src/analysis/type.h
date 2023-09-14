
/* Chrysalide - Outil d'analyse de fichiers binaires
 * type.h - prototypes pour la manipulation des types en tout genre
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_TYPE_H
#define _ANALYSIS_TYPE_H


#include <glib-object.h>
#include <stdbool.h>



#define G_TYPE_DATA_TYPE            g_data_type_get_type()
#define G_DATA_TYPE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DATA_TYPE, GDataType))
#define G_IS_DATA_TYPE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DATA_TYPE))
#define G_DATA_TYPE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DATA_TYPE, GDataTypeClass))
#define G_IS_DATA_TYPE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DATA_TYPE))
#define G_DATA_TYPE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DATA_TYPE, GDataTypeClass))


/* Description de type quelconque (instance) */
typedef struct _GDataType GDataType;

/* Description de type quelconque (classe) */
typedef struct _GDataTypeClass GDataTypeClass;


/* Qualificatifs de variables */
typedef enum _TypeQualifier
{
    TQF_NONE        = (0 << 0),             /* Néant                       */
    TQF_RESTRICT    = (1 << 0),             /* restrict (C99)              */
    TQF_VOLATILE    = (1 << 1),             /* volatile                    */
    TQF_CONST       = (1 << 2),             /* const                       */

    TQF_ALL         = ((1 << 3) - 1)        /* Masque de qualificatifs     */

} TypeQualifier;

/* Propriétés particulières d'un type */
typedef enum _TypeFlag
{
    TFL_NONE            = (0 << 0),         /* Aucune propriété            */
    TFL_SINGLETON_SOON  = (1 << 0),         /* Singleton en devenir        */
    TFL_SINGLETON       = (1 << 1),         /* Singleton effectif          */

    TFL_USER_LOW_BIT    = (1 << 2),         /* Premier bit libre           */
    TFL_USER_HIGH_BIT   = (1 << 7)          /* Dernier bit libre           */

} TypeFlag;


/* Indique le type défini pour un type quelconque. */
GType g_data_type_get_type(void);

/* Calcule une empreinte pour un type de données. */
guint g_data_type_hash(const GDataType *);

/* Crée un copie d'un type existant. */
GDataType *g_data_type_dup(const GDataType *);

/* Décrit le type fourni sous forme de caractères. */
char *g_data_type_to_string(const GDataType *, bool);

/* Définit l'ensemble des qualificatifs d'une instance de type. */
void g_data_type_set_qualifiers(GDataType *, TypeQualifier);

/* Ajoute un qualificatif à une instance de type. */
void g_data_type_add_qualifier(GDataType *, TypeQualifier);

/* Fournit les qualificatifs associés à une instance de type. */
TypeQualifier g_data_type_get_qualifiers(const GDataType *);

/* Définit le groupe d'appartenance d'un type donné. */
bool g_data_type_set_namespace(GDataType *, GDataType *, const char *);

/* Fournit le groupe d'appartenance d'un type donné. */
GDataType *g_data_type_get_namespace(const GDataType *);

/* Fournit la chaîne de séparation entre deux entités. */
char *g_data_type_get_namespace_separator(const GDataType *);

/* Indique si le type assure une gestion des espaces de noms. */
bool g_data_type_handle_namespaces(const GDataType *);

/* Définit l'ensemble des fanions d'une instance de type. */
void g_data_type_set_flags(GDataType *, TypeFlag);

/* Ajoute un fanion à une instance de type. */
void g_data_type_add_flag(GDataType *, TypeFlag);

/* Fournit les fanions associés à une instance de type. */
TypeFlag g_data_type_get_flags(const GDataType *);

/* Indique si le type est un pointeur. */
bool g_data_type_is_pointer(const GDataType *);

/* Indique si le type est une référence. */
bool g_data_type_is_reference(const GDataType *);



#endif  /* _ANALYSIS_TYPE_H */
