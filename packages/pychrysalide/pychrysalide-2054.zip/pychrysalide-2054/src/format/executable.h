
/* Chrysalide - Outil d'analyse de fichiers binaires
 * executable.h - prototypes pour le support des formats d'exécutables
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


#ifndef _FORMAT_EXECUTABLE_H
#define _FORMAT_EXECUTABLE_H


#include <glib-object.h>


#include "debuggable.h"
#include "../glibext/gbinportion.h"



#define G_TYPE_EXE_FORMAT            g_executable_format_get_type()
#define G_EXE_FORMAT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_EXE_FORMAT, GExeFormat))
#define G_IS_EXE_FORMAT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_EXE_FORMAT))
#define G_EXE_FORMAT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_EXE_FORMAT, GExeFormatClass))
#define G_IS_EXE_FORMAT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_EXE_FORMAT))
#define G_EXE_FORMAT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_EXE_FORMAT, GExeFormatClass))


/* Format d'exécutable générique (instance) */
typedef struct _GExeFormat GExeFormat;

/* Format d'exécutable générique (classe) */
typedef struct _GExeFormatClass GExeFormatClass;


/* Indique le type défini pour un format d'exécutable générique. */
GType g_executable_format_get_type(void);

/* Rajoute des informations de débogage à un exécutable. */
void g_exe_format_add_debug_info(GExeFormat *, GDbgFormat *);

/* Compte le nombre de formats de débogage liés à l'exécutable. */
size_t g_exe_format_count_debug_info(const GExeFormat *);

/* Fournit un format de débogage attaché à l'exécutable. */
GDbgFormat *g_exe_format_get_debug_info(const GExeFormat *, size_t);

/* Indique le type d'architecture visée par le format. */
const char *g_exe_format_get_target_machine(const GExeFormat *);

/* Fournit l'adresse principale associée à un format. */
bool g_exe_format_get_main_address(GExeFormat *, vmpa2t *);

/* Enregistre une portion artificielle pour le format. */
void g_exe_format_register_user_portion(GExeFormat *, GBinPortion *);

/* Procède à l'enregistrement d'une portion dans un format. */
void g_exe_format_include_portion(GExeFormat *, GBinPortion *, const vmpa2t *);

/* Fournit la première couche des portions composent le binaire. */
GBinPortion *g_exe_format_get_portions(GExeFormat *);

/* Fournit les espaces mémoires des portions exécutables. */
mrange_t *g_exe_format_get_x_ranges(GExeFormat *, size_t *);

/* Fournit l'emplacement correspondant à une position physique. */
bool g_exe_format_translate_offset_into_vmpa(GExeFormat *, phys_t, vmpa2t *);

/* Fournit l'emplacement correspondant à une position physique. */
bool g_exe_format_translate_address_into_vmpa(GExeFormat *, virt_t, vmpa2t *);


#define g_exe_format_translate_offset_into_address(fmt, off, addr)              \
    ({                                                                          \
        bool __result;                                                          \
        vmpa2t __pos;                                                           \
        __result = g_exe_format_translate_offset_into_vmpa(fmt, off, &__pos);   \
        *addr = get_virt_addr(&__pos);                                          \
        __result;                                                               \
    })

#define g_exe_format_translate_address_into_offset(fmt, addr, off)              \
    ({                                                                          \
        bool __result;                                                          \
        vmpa2t __pos;                                                           \
        __result = g_exe_format_translate_address_into_vmpa(fmt, addr, &__pos); \
        *off = get_phy_addr(&__pos);                                            \
        __result;                                                               \
    })


/* Fournit l'emplacement d'une section donnée. */
bool g_exe_format_get_section_range_by_name(const GExeFormat *, const char *, mrange_t *);



#endif  /* _FORMAT_EXECUTABLE_H */
