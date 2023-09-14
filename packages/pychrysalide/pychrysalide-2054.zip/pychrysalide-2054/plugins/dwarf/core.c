
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - intégration du support du format DWARF
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include "core.h"


#include <plugins/self.h>


#include "format.h"


#ifdef INCLUDE_PYTHON3_BINDINGS
#   define PG_REQ RL("PyChrysalide")
#else
#   define PG_REQ NO_REQ
#endif



DEFINE_CHRYSALIDE_PLUGIN("Dwarf", "DWARF format support",
                         PACKAGE_VERSION, CHRYSALIDE_WEBSITE("doc/formats"),
                         PG_REQ, AL(PGA_PLUGIN_INIT, PGA_FORMAT_ATTACH_DEBUG));



/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                                                                             *
*  Description : Prend acte du chargement du greffon.                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT bool chrysalide_plugin_init(GPluginModule *plugin)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                format = format de binaire à manipuler pendant l'opération.  *
*                                                                             *
*  Description : Procède au rattachement d'éventuelles infos de débogage.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT void chrysalide_plugin_attach_debug(const GPluginModule *plugin, PluginAction action, GExeFormat *format)
{
    GDbgFormat *info;

    info = check_dwarf_format(format);

    if (info != NULL)
        g_exe_format_add_debug_info(format, info);

}
