
/* Chrysalide - Outil d'analyse de fichiers binaires
 * variable.h - prototypes pour la manipulation des variables en tout genre
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#ifndef _ANALYSIS_VARIABLE_H
#define _ANALYSIS_VARIABLE_H


#include <stdbool.h>
#include <glib-object.h>


#include "types/basic.h"
#include "types/encaps.h"



/* ------------------- ASSOCIATION D'UN TYPE ET D'UNE DESIGNATION ------------------- */


#define G_TYPE_BIN_VARIABLE            g_binary_variable_get_type()
#define G_BIN_VARIABLE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BIN_VARIABLE, GBinVariable))
#define G_IS_BIN_VARIABLE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BIN_VARIABLE))
#define G_BIN_VARIABLE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BIN_VARIABLE, GBinVariableClass))
#define G_IS_BIN_VARIABLE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BIN_VARIABLE))
#define G_BIN_VARIABLE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BIN_VARIABLE, GBinVariableClass))


/* Base de variable (instance) */
typedef struct _GBinVariable GBinVariable;

/* Base de variable (classe) */
typedef struct _GBinVariableClass GBinVariableClass;


/* Indique le type défini pour une base de variable. */
GType g_binary_variable_get_type(void);

/* Crée une représentation de variable de type donné. */
GBinVariable *g_binary_variable_new(GDataType *);

/* Fournit le type d'une variable donnée. */
GDataType *g_binary_variable_get_vtype(const GBinVariable *);

/* Fournit le nom d'une variable donnée. */
const char *g_binary_variable_get_name(const GBinVariable *);

/* Définit le nom d'une variable donnée. */
void g_binary_variable_set_name(GBinVariable *, const char *);

/* Fournit la zone d'appartenance d'une variable donnée. */
GDataType *g_binary_variable_get_owner(const GBinVariable *);

/* Définit la zone d'appartenance d'une variable donnée. */
void g_binary_variable_set_owner(GBinVariable *, GDataType *);

/* Décrit la variable donnée sous forme de caractères. */
char *g_binary_variable_to_string(const GBinVariable *, bool);



/* -------------------- BASE DE VARIABLES OU VARIABLES INCONNUES -------------------- */


#define G_TYPE_UNKNOWN_VARIABLE            g_unknown_variable_get_type()
#define G_UNKNOWN_VARIABLE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_UNKNOWN_VARIABLE, GUnknownVariable))
#define G_IS_UNKNOWN_VARIABLE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_UNKNOWN_VARIABLE))
#define G_UNKNOWN_VARIABLE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_UNKNOWN_VARIABLE, GUnknownVariableClass))
#define G_IS_UNKNOWN_VARIABLE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_UNKNOWN_VARIABLE))
#define G_UNKNOWN_VARIABLE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_UNKNOWN_VARIABLE, GUnknownVariableClass))


/* Base de variable (instance) */
typedef struct _GUnknownVariable GUnknownVariable;

/* Base de variable (classe) */
typedef struct _GUnknownVariableClass GUnknownVariableClass;


/* Indique le type défini pour une base de variable. */
GType g_unknown_variable_get_type(void);

/* Crée une représentation de variable de type inconnu. */
GUnknownVariable *g_unknown_variable_new(void);

/* Etablit la comparaison ascendante entre deux variables. */
int g_unknown_variable_compare(const GUnknownVariable **, const GUnknownVariable **);

/* Définit la position associée à une variable. */
void g_unknown_variable_set_offset(GUnknownVariable *, size_t);

/* Fournit la position associée à une variable. */
size_t g_unknown_variable_get_offset(const GUnknownVariable *);

/* Indique si une position est contenue dans une variable. */
bool g_unknown_variable_contains_offset(const GUnknownVariable *, size_t);



#endif  /* _ANALYSIS_VARIABLE_H */
