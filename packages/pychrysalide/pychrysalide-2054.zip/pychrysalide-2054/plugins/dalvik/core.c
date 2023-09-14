
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - intégration du support de l'architecture Dalvik
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


#include <plugins/self.h>


#include "register.h"
#include "operands/args.h"
#include "operands/pool.h"
#include "operands/register.h"
#ifdef INCLUDE_PYTHON3_BINDINGS
#   include "python/module.h"
#endif
#include "v35/core.h"


#ifdef INCLUDE_PYTHON3_BINDINGS
#   define PG_REQ RL("PyChrysalide")
#else
#   define PG_REQ NO_REQ
#endif



DEFINE_CHRYSALIDE_PLUGIN("Dalvik", "Dalvik architecture support",
                         PACKAGE_VERSION, CHRYSALIDE_WEBSITE("doc/architectures"),
                         PG_REQ, AL(PGA_PLUGIN_INIT, PGA_PLUGIN_EXIT));



/* Assure l'enregistrement de types pour les caches à charger. */
static void register_dalvik_gtypes(void);



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Assure l'enregistrement de types pour les caches à charger.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void register_dalvik_gtypes(void)
{
    g_type_ensure(G_TYPE_DALVIK_ARGS_OPERAND);
    g_type_ensure(G_TYPE_DALVIK_POOL_OPERAND);
    g_type_ensure(G_TYPE_DALVIK_REGISTER_OPERAND);

    g_type_ensure(G_TYPE_DALVIK_REGISTER);

}


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

    register_dalvik_gtypes();

    result = init_dalvik35_core();

#ifdef INCLUDE_PYTHON3_BINDINGS
    if (result)
        result = add_arch_dalvik_module_to_python_module();
#endif

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : plugin = greffon à manipuler.                                *
*                                                                             *
*  Description : Prend acte du déchargement du greffon.                       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

G_MODULE_EXPORT void chrysalide_plugin_exit(GPluginModule *plugin)
{
    exit_dalvik35_core();

    clean_dalvik_register_cache();

}
