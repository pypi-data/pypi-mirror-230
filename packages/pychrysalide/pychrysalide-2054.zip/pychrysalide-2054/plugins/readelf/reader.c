
/* Chrysalide - Outil d'analyse de fichiers binaires
 * reader.c - interprétation des informations secondaires contenues dans un fichier ELF
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#include "reader.h"


#include <plugins/elf/format.h>
#include <plugins/self.h>


#include "header.h"
#include "program.h"
#include "section.h"
#include "strtab.h"



DEFINE_CHRYSALIDE_PLUGIN("ElfReader", "Information about ELF files",
                         PACKAGE_VERSION, CHRYSALIDE_WEBSITE(""),
                         NO_REQ, AL(PGA_FORMAT_PRELOAD));


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Etablit des symboles complémentaires dans un format ELF.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT bool chrysalide_plugin_preload_binary_format(const GPluginModule *plugin, PluginAction action, GBinFormat *format, GPreloadInfo *info, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    GElfFormat *elf_fmt;                    /* Version ELF                 */

    if (!G_IS_ELF_FORMAT(format))
    {
        result = true;
        goto pbf_exit;
    }

    elf_fmt = G_ELF_FORMAT(format);

    result = annotate_elf_header(format, info);

    result &= annotate_elf_program_header_table(elf_fmt, info, status);

    result &= annotate_elf_section_header_table(elf_fmt, info, status);

    show_elf_section_string_table(elf_fmt, info, status);

 pbf_exit:

    return result;

}
