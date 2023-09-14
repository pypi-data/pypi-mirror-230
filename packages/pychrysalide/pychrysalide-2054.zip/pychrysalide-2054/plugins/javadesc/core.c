
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - intégration du décodage pour symboles Java
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


#include <core/demanglers.h>
#include <plugins/self.h>


#include "demangler.h"
#ifdef INCLUDE_PYTHON3_BINDINGS
#   include "python/module.h"
#endif


#ifdef INCLUDE_PYTHON3_BINDINGS
#   define PG_REQ RL("PyChrysalide")
#else
#   define PG_REQ NO_REQ
#endif



DEFINE_CHRYSALIDE_PLUGIN("JavaDesc", "Java symbol demangling",
                         PACKAGE_VERSION, CHRYSALIDE_WEBSITE("doc/mangling"),
                         PG_REQ, AL(PGA_PLUGIN_INIT));



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

    result = register_demangler_type(G_TYPE_JAVA_DEMANGLER);

#ifdef INCLUDE_PYTHON3_BINDINGS
    if (result)
        result = add_mangling_javadesc_module_to_python_module();
#endif

    return result;

}
