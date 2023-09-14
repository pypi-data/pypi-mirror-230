
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - intégration du support du format MobiCore
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


#include <core/global.h>
#include <plugins/self.h>


#include "mclf.h"



DEFINE_CHRYSALIDE_PLUGIN("Mobicore", "MobiCore file format support for Trusted Applications",
                         PACKAGE_VERSION, CHRYSALIDE_WEBSITE("doc/formats"),
                         NO_REQ, AL(PGA_CONTENT_RESOLVER));



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

    test = check_mclf_format(content);

    if (test)
    {
        format = g_mclf_format_new(content);
        loaded = g_loaded_binary_new(format);

        resolver = get_current_content_resolver();
        g_content_resolver_add_detected(resolver, wid, loaded);
        g_object_unref(G_OBJECT(resolver));

        g_object_unref(G_OBJECT(loaded));

    }

}
