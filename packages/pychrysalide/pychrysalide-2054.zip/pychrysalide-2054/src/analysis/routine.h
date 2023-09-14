
/* Chrysalide - Outil d'analyse de fichiers binaires
 * routine.h - prototypes pour la manipulation des prototypes de fonctions et de variables
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


#ifndef _ANALYSIS_ROUTINE_H
#define _ANALYSIS_ROUTINE_H


#include <glib-object.h>
#include <stdint.h>
#include <sys/types.h>


#include "binary.h"
#include "variable.h"
#include "block.h"
#include "../arch/processor.h"



/* Type de routine traitée */
typedef enum _RoutineType
{
    RTT_CLASSIC,                            /* Fonction ou méthode         */
    RTT_CONSTRUCTOR,                        /* Constructeur                */
    RTT_DESTRUCTOR                          /* Destructeur                 */

} RoutineType;


#define G_TYPE_BIN_ROUTINE            g_bin_routine_get_type()
#define G_BIN_ROUTINE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_BIN_ROUTINE, GBinRoutine))
#define G_IS_BIN_ROUTINE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_BIN_ROUTINE))
#define G_BIN_ROUTINE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BIN_ROUTINE, GBinRoutineClass))
#define G_IS_BIN_ROUTINE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BIN_ROUTINE))
#define G_BIN_ROUTINE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BIN_ROUTINE, GBinRoutineClass))


/* Représentation générique de routine (instance) */
typedef struct _GBinRoutine GBinRoutine;

/* Représentation générique de routine (classe) */
typedef struct _GBinRoutineClass GBinRoutineClass;


/* Indique le type défini pour une représentation de routine. */
GType g_bin_routine_get_type(void);

/* Crée une représentation de routine. */
GBinRoutine *g_binary_routine_new(void);

/* Crée une représentation de routine construisant une instance. */
GBinRoutine *g_binary_routine_new_constructor(GDataType *);

/* Définit le type d'une routine. */
void g_binary_routine_set_type(GBinRoutine *, RoutineType);

/* Définit le groupe d'appartenance d'une routine donnée. */
void g_binary_routine_set_namespace(GBinRoutine *, GDataType *, char *);

/* Fournit le groupe d'appartenance d'une routine donnée. */
GDataType *g_binary_routine_get_namespace(const GBinRoutine *);

/* Définit le nom humain d'une routine. */
void g_binary_routine_set_name(GBinRoutine *, char *);

/* Désignation humainement lisible ou NULL si non définie. */
const char *g_binary_routine_get_name(const GBinRoutine *);

/* Définit de façon indirecte le nom humain d'une routine. */
void g_binary_routine_set_typed_name(GBinRoutine *, GDataType *);

/* Fournit le type construisant le nom humain d'une routine. */
GDataType *g_binary_routine_get_typed_name(const GBinRoutine *);

/* Définit le type de retour d'une routine. */
void g_binary_routine_set_return_type(GBinRoutine *, GDataType *);

/* Fournit le type de retour d'une routine. */
GDataType *g_binary_routine_get_return_type(const GBinRoutine *);

/* Ajoute un argument à une routine. */
void g_binary_routine_add_arg(GBinRoutine *, GBinVariable *);

/* Indique le nombre d'arguments associés à une routine. */
size_t g_binary_routine_get_args_count(const GBinRoutine *);

/* Fournit un argument d'une routine. */
GBinVariable *g_binary_routine_get_arg(const GBinRoutine *, size_t);

/* Retire un argument d'une routine. */
void g_binary_routine_remove_arg(GBinRoutine *, size_t);

/* S'assure qu'une variable est bien associée à une routine. */
void g_binary_routine_register_if_needed(GBinRoutine *, size_t, bool);

/* Donne l'indice d'une variable dans la liste d'une routine. */
size_t g_binary_routine_get_var_index_from_offset(const GBinRoutine *, size_t, bool);

/* Fournit les blocs basiques de la routine. */
GBlockList *g_binary_routine_get_basic_blocks(const GBinRoutine *);

/* Définit les blocs basiques de la routine. */
void g_binary_routine_set_basic_blocks(GBinRoutine *, GBlockList *);

/* Décrit le prototype de la routine sous forme de caractères. */
char *g_binary_routine_to_string(const GBinRoutine *, bool);

/* Procède à l'impression de la description d'une routine. */
//void g_binary_routine_output_info(const GBinRoutine *, GLangOutput *, GCodeBuffer *);

/* Procède à l'impression de la décompilation d'une routine. */
//void g_binary_routine_print_code(const GBinRoutine *, GLangOutput *, GCodeBuffer *, bool);



#ifdef INCLUDE_GTK_SUPPORT

/* Construit un petit résumé concis de la routine. */
char *g_binary_routine_build_tooltip(const GBinRoutine *, const GLoadedBinary *);

#endif



#endif  /* _ANALYSIS_ROUTINE_H */
