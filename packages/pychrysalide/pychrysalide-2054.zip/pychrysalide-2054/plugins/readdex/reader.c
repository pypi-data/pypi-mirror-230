
/* Chrysalide - Outil d'analyse de fichiers binaires
 * reader.c - interprétation des informations secondaires contenues dans un fichier DEX
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#include <plugins/dex/format.h>
#include <plugins/self.h>


#include "class.h"
#include "header.h"
#include "ids.h"



DEFINE_CHRYSALIDE_PLUGIN("DexReader", "Information about DEX files",
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
*  Description : Etablit des symboles complémentaires dans un format DEX.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT bool chrysalide_plugin_preload_binary_format(const GPluginModule *plugin, PluginAction action, GBinFormat *format, GPreloadInfo *info, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    GDexFormat *dex_fmt;                    /* Version DEX                 */

    if (!G_IS_DEX_FORMAT(format))
    {
        result = true;
        goto pbf_exit;
    }

    dex_fmt = G_DEX_FORMAT(format);

    result = annotate_dex_header(dex_fmt, info);

    result &= annotate_dex_string_ids(dex_fmt, info, status);

    result &= annotate_dex_type_ids(dex_fmt, info, status);

    result &= annotate_dex_proto_ids(dex_fmt, info, status);

    result &= annotate_dex_field_ids(dex_fmt, info, status);

    result &= annotate_dex_method_ids(dex_fmt, info, status);

    result &= annotate_dex_class_defs(dex_fmt, info, status);

 pbf_exit:

    return result;

}
