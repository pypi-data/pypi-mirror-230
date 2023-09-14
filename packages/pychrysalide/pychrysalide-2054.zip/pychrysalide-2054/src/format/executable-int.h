
/* Chrysalide - Outil d'analyse de fichiers binaires
 * executable-int.h - prototypes de code utile aux formats d'exécutables
 *
 * Copyright (C) 2009-2019 Cyrille Bagard
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


#ifndef _FORMAT_EXECUTABLE_INT_H
#define _FORMAT_EXECUTABLE_INT_H


#include "executable.h"


#include "format-int.h"



/* Indique le type d'architecture visée par le format. */
typedef const char * (* get_target_machine_fc) (const GExeFormat *);

/* Fournit l'adresse principale associée à un format. */
typedef bool (* get_main_addr_fc) (GExeFormat *, vmpa2t *);

/* Etend la définition des portions au sein d'un binaire. */
typedef void (* refine_portions_fc) (GExeFormat *);

/* Fournit l'emplacement correspondant à une position physique. */
typedef bool (* translate_phys_fc) (GExeFormat *, phys_t, vmpa2t *);

/* Fournit l'emplacement correspondant à une adresse virtuelle. */
typedef bool (* translate_virt_fc) (GExeFormat *, virt_t, vmpa2t *);

/* Fournit l'emplacement d'une section donnée. */
typedef bool (* get_range_by_name_fc) (const GExeFormat *, const char *, mrange_t *);



/* Format d'exécutable générique (instance) */
struct _GExeFormat
{
    GBinFormat parent;                      /* A laisser en premier        */

    GDbgFormat **debugs;                    /* Informations de débogage    */
    size_t debugs_count;                    /* Nombre de ces informations  */

    GBinPortion **user_portions;            /* Couches de morceaux binaires*/
    size_t user_count;                      /* Nombre de ces portions      */
    GBinPortion *portions;                  /* Couches de morceaux binaires*/
    GMutex mutex;                           /* Accès à l'arborescence      */

};

/* Format d'exécutable générique (classe) */
struct _GExeFormatClass
{
    GBinFormatClass parent;                 /* A laisser en premier        */

    get_target_machine_fc get_machine;      /* Architecture ciblée         */
    get_main_addr_fc get_main_addr;         /* Obtention d'adresse première*/
    refine_portions_fc refine_portions;     /* Décrit les portions binaires*/

    translate_phys_fc translate_phys;       /* Correspondance phys -> vmpa */
    translate_virt_fc translate_virt;       /* Correspondance virt -> vmpa */

    get_range_by_name_fc get_range_by_name; /* Emplacement de sections     */     

};


/* Crée les portions potentiellement utiles aux traductions. */
void g_executable_format_setup_portions(GExeFormat *, GtkStatusStack *);

/* Effectue les ultimes opérations de chargement d'un binaire. */
bool g_executable_format_complete_loading(GExeFormat *, wgroup_id_t, GtkStatusStack *);

/* Fournit l'emplacement correspondant à une position physique. */
bool g_exe_format_without_virt_translate_offset_into_vmpa(const GExeFormat *, phys_t, vmpa2t *);

/* Fournit l'emplacement correspondant à une adresse virtuelle. */
bool g_exe_format_without_virt_translate_address_into_vmpa(const GExeFormat *, virt_t, vmpa2t *);

/* Fournit l'emplacement correspondant à une position physique. */
bool g_exe_format_translate_offset_into_vmpa_using_portions(GExeFormat *, phys_t, vmpa2t *);

/* Fournit l'emplacement correspondant à une adresse virtuelle. */
bool g_exe_format_translate_address_into_vmpa_using_portions(GExeFormat *, virt_t, vmpa2t *);



#endif  /* _FORMAT_EXECUTABLE_INT_H */
