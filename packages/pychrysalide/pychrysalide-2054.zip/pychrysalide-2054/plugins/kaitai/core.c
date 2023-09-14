
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - prise en charge des descriptions de binaires au format Kaitai
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#ifdef INCLUDE_PYTHON3_BINDINGS
#   include "python/module.h"
#endif


#ifdef INCLUDE_PYTHON3_BINDINGS
#   define PG_REQ RL("PyChrysalide")
#else
#   define PG_REQ NO_REQ
#endif



DEFINE_CHRYSALIDE_PLUGIN("Kaitai", "Content parser using Kaitai structure definitions",
                         PACKAGE_VERSION, CHRYSALIDE_WEBSITE("doc/kaitai"),
                         PG_REQ, AL(PGA_PLUGIN_INIT));



/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                                                                             *
*  Description : Prend acte du chargement du greffon.                         *
*                                                                             *
*  Retour      : Bilan du chargement mené.                                    *
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
        result = add_kaitai_module_to_python_module();

    if (result)
        result = populate_kaitai_module();

#endif

    return result;

}
