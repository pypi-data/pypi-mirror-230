
/* Chrysalide - Outil d'analyse de fichiers binaires
 * reader.c - interprétation des informations secondaires contenues dans un fichier Mobicore
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


#include "reader.h"


#include <plugins/mobicore/mclf.h>
#include <plugins/self.h>


#include "header.h"
#include "text.h"
#include "v21.h"
#include "v23.h"
#include "v24.h"



DEFINE_CHRYSALIDE_PLUGIN("MCReader", "Information about Mobicore files",
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
*  Description : Etablit des symboles complémentaires dans un format Mobicore.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT bool chrysalide_plugin_preload_binary_format(const GPluginModule *plugin, PluginAction action, GBinFormat *format, GPreloadInfo *info, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    vmpa2t pos;                             /* Tête de lecture des symboles*/
    uint32_t version;                       /* Version du format analysé   */

    if (!G_IS_MCLF_FORMAT(format))
    {
        result = true;
        goto pbf_exit;
    }

    result = g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), 0, &pos);

    if (result)
        result = annotate_mobicore_header(format, info, &pos, &version);

    if (result)
        result = annotate_mobicore_v21_header(format, info, &pos);

    if (result)
        result = annotate_mobicore_v23_header(format, info, &pos);

    if (result)
        result = annotate_mobicore_v24_header(format, info, &pos);

    if (result)
        result = annotate_mobicore_text_header(format, info, &pos);

 pbf_exit:

    return result;

}
