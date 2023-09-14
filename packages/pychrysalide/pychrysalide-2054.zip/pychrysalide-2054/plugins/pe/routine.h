
/* Chrysalide - Outil d'analyse de fichiers binaires
 * routine.h - prototypes pour la manipulation des routines du format PE
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _PLUGINS_PE_ROUTINE_H
#define _PLUGINS_PE_ROUTINE_H


#include <glib-object.h>


#include <analysis/routine.h>



/* ------------------------ SYMBOLES D'UN FORMAT PE EXPORTES ------------------------ */


#define G_TYPE_PE_EXPORTED_ROUTINE            g_pe_exported_routine_get_type()
#define G_PE_EXPORTED_ROUTINE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_PE_EXPORTED_ROUTINE, GPeExportedRoutine))
#define G_IS_PE_EXPORTED_ROUTINE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_PE_EXPORTED_ROUTINE))
#define G_PE_EXPORTED_ROUTINE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_PE_EXPORTED_ROUTINE, GPeExportedRoutineClass))
#define G_IS_PE_EXPORTED_ROUTINE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_PE_EXPORTED_ROUTINE))
#define G_PE_EXPORTED_ROUTINE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_PE_EXPORTED_ROUTINE, GPeExportedRoutineClass))


/* Représentation de routine PE exportée (instance) */
typedef struct _GPeExportedRoutine GPeExportedRoutine;

/* Représentation de routine PE exportée (classe) */
typedef struct _GPeExportedRoutineClass GPeExportedRoutineClass;


/* Drapeaux pour informations complémentaires */
typedef enum _PeSymbolFlag
{
    PSF_HAS_ORDINAL = (1 << (SFL_LOW_USER + 0)), /* Numérotation présente  */
    PSF_FORWARDED   = (1 << (SFL_LOW_USER + 1)), /* Renvoi vers une DLL ?  */

} PeSymbolFlag;


#define UNDEF_PE_ORDINAL 0xffff


/* Indique le type défini pour une représentation de routine exportée. */
GType g_pe_exported_routine_get_type(void);

/* Crée une représentation de routine exportée pour format PE. */
GPeExportedRoutine *g_pe_exported_routine_new(const char *);

/* Définit l'indice de la routine dans un fichier PE. */
void g_pe_exported_routine_set_ordinal(GPeExportedRoutine *, uint16_t);

/* Fournit l'indice de la routine dans un fichier PE. */
uint16_t g_pe_exported_routine_get_ordinal(const GPeExportedRoutine *);



/* ------------------------ SYMBOLES D'UN FORMAT PE IMPORTES ------------------------ */


#define G_TYPE_PE_IMPORTED_ROUTINE            g_pe_imported_routine_get_type()
#define G_PE_IMPORTED_ROUTINE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_PE_IMPORTED_ROUTINE, GPeImportedRoutine))
#define G_IS_PE_IMPORTED_ROUTINE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_PE_IMPORTED_ROUTINE))
#define G_PE_IMPORTED_ROUTINE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_PE_IMPORTED_ROUTINE, GPeImportedRoutineClass))
#define G_IS_PE_IMPORTED_ROUTINE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_PE_IMPORTED_ROUTINE))
#define G_PE_IMPORTED_ROUTINE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_PE_IMPORTED_ROUTINE, GPeImportedRoutineClass))


/* Représentation de routine PE importée (instance) */
typedef struct _GPeImportedRoutine GPeImportedRoutine;

/* Représentation de routine PE importée (classe) */
typedef struct _GPeImportedRoutineClass GPeImportedRoutineClass;


/* Indique le type défini pour une représentation de routine importée. */
GType g_pe_imported_routine_get_type(void);

/* Crée une représentation de routine importée pour format PE. */
GPeImportedRoutine *g_pe_imported_routine_new(const char *, size_t);

/* Fournit la position du symbole dans les importations. */
size_t g_pe_imported_routine_get_index(const GPeImportedRoutine *);

/* Définit le fichier DLL visé par une importation de format PE. */
void g_pe_imported_routine_set_library(GPeImportedRoutine *, const char *);

/* Fournit le fichier DLL visé par une importation de format PE. */
const char *g_pe_imported_routine_get_library(const GPeImportedRoutine *);



#endif  /* _PLUGINS_PE_ROUTINE_H */
