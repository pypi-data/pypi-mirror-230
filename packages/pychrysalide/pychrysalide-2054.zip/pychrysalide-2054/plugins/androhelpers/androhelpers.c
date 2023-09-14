
/* Chrysalide - Outil d'analyse de fichiers binaires
 * androhelpers.c - greffon d'appoint pour les traitements Android
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#include "androhelpers.h"


#include <string.h>


#include <format/dex/dex.h>


#include "params.h"
#include "switch.h"
#include "try_n_catch.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Précise le nom associé au greffon.                           *
*                                                                             *
*  Retour      : Nom à libérer de la mémoire.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *get_plugin_name(void)
{
    return strdup("AndroHelpers");

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à consulter.                                *
*                                                                             *
*  Description : Indique les opérations offertes par un greffon donné.        *
*                                                                             *
*  Retour      : Action(s) offerte(s) par le greffon.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PluginAction get_plugin_action(const GPluginModule *plugin)
{
    PluginAction result;                    /* Combinaison à retourner     */

    result = PGA_BINARY_DISASSEMBLED | PGA_BINARY_LINKED | PGA_BINARY_PRINTED;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon de prise en charge à utiliser.              *
*                binary = représentation binaire à traiter.                   *
*                action = action attendue.                                    *
*                                                                             *
*  Description : Exécute une action définie sur un binaire chargé.            *
*                                                                             *
*  Retour      : true si une action a été menée, false sinon.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool execute_action_on_binary(GPluginModule *plugin, GLoadedBinary *binary, PluginAction action)
{
    bool result;                            /* Bilan à retourner           */
    GExeFormat *format;                     /* Format associé au binaire   */

    format = g_loaded_binary_get_format(binary);

    result = G_IS_DEX_FORMAT(format);

    g_object_unref(G_OBJECT(format));

    if (!result)
        return false;

    if (action == PGA_BINARY_DISASSEMBLED)
        result &= replace_parameters(binary);

    else if (action == PGA_BINARY_LINKED)
    {
        result &= extract_switch_info(binary, true);
        result &= process_exception_handlers(binary, true);
    }

    else if (action == PGA_BINARY_PRINTED)
    {
        result &= extract_switch_info(binary, false);
        result &= process_exception_handlers(binary, false);
    }

    return result;

}
