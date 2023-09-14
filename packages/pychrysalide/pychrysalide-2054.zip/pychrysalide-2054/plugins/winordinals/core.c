
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - connaissance de valeurs ordinales pour certains fichiers DLL
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#include <assert.h>


#include <plugins/self.h>


#include "assign.h"
#ifdef INCLUDE_PYTHON3_BINDINGS
#   include "python/module.h"
#endif


#ifdef INCLUDE_PYTHON3_BINDINGS
#   define PG_REQ RL("PyChrysalide")
#else
#   define PG_REQ NO_REQ
#endif


DEFINE_CHRYSALIDE_PLUGIN("WinOrdinals", "Ordinals database for some DLL files",
                         PACKAGE_VERSION, CHRYSALIDE_WEBSITE(""),
                         PG_REQ, AL(PGA_PLUGIN_INIT, PGA_FORMAT_ANALYSIS_ENDED));



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

#ifdef INCLUDE_PYTHON3_BINDINGS

    if (result)
        result = add_winordinals_module_to_python_module();

    if (result)
        result = populate_winordinals_module();

#endif

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                action = type d'action attendue.                             *
*                format = format de binaire à manipuler pendant l'opération.  *
*                gid    = groupe de travail dédié.                            *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Procède à une opération liée à l'analyse d'un format.        *
*                                                                             *
*  Retour      : Bilan de l'exécution du traitement.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT bool chrysalide_plugin_handle_binary_format_analysis(const GPluginModule *plugin, PluginAction action, GKnownFormat *format, wgroup_id_t gid, GtkStatusStack *status)
{
    assert(action == PGA_FORMAT_ANALYSIS_ENDED);

    if (G_IS_PE_FORMAT(format))
        assign_name_imported_ordinals(G_PE_FORMAT(format), status);

    return true;

}
