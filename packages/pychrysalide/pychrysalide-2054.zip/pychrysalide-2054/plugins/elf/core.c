
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - intégration du support du format ELF
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#include <core/global.h>
#include <plugins/self.h>


#include "format.h"
#ifdef INCLUDE_PYTHON3_BINDINGS
#   include "python/module.h"
#endif


#ifdef INCLUDE_PYTHON3_BINDINGS
#   define PG_REQ RL("PyChrysalide")
#else
#   define PG_REQ NO_REQ
#endif



DEFINE_CHRYSALIDE_PLUGIN("Elf", "ELF format support",
                         PACKAGE_VERSION, CHRYSALIDE_WEBSITE("doc/formats"),
                         PG_REQ, AL(PGA_PLUGIN_INIT, PGA_CONTENT_RESOLVER));



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

#ifdef INCLUDE_PYTHON3_BINDINGS
    result = add_format_elf_module_to_python_module();
#else
    result = true;
#endif

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin  = greffon à manipuler.                               *
*                action  = type d'action attendue.                            *
*                content = contenu binaire à traiter.                         *
*                wid     = identifiant du groupe de traitement.               *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Procède à une opération liée à un contenu binaire.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT void chrysalide_plugin_handle_binary_content(const GPluginModule *plugin, PluginAction action, GBinContent *content, wgroup_id_t wid, GtkStatusStack *status)
{
    bool test;                              /* Bilan des accès mémoire     */
    GExeFormat *format;                     /* Format ELF reconnu          */
    GLoadedContent *loaded;                 /* Représentation chargée      */
    GContentResolver *resolver;             /* Resolveur de contenus       */

    test = check_elf_format(content);

    if (test)
    {
        format = g_elf_format_new(content);
        loaded = g_loaded_binary_new(format);

        resolver = get_current_content_resolver();
        g_content_resolver_add_detected(resolver, wid, loaded);
        g_object_unref(G_OBJECT(resolver));

        g_object_unref(G_OBJECT(loaded));

    }

}
