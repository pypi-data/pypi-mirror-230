
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.c - chargement et le déchargement du tronc commun
 *
 * Copyright (C) 2014-2019 Cyrille Bagard
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


#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <openssl/err.h>
#include <openssl/ssl.h>


#include "collections.h"
#include "demanglers.h"
#include "global.h"
#include "params.h"
#include "processors.h"
#include "queue.h"
#include "../analysis/scan/core.h"
#ifdef INCLUDE_MAGIC_SUPPORT
#   include "../analysis/scan/items/magic/cookie.h"
#endif
#include "../common/io.h"
#include "../common/xdg.h"
#include "../glibext/linesegment.h"
#include "../plugins/dt.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : cs = précise si l'appel est réalisé du côté client.          *
*                                                                             *
*  Description : Charge les éléments de base du programme.                    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_all_core_components(bool cs)
{
    static bool result = false;             /* Bilan à retourner           */
    char *cfgdir;                           /* Répertoire de configuration */
    GContentExplorer *explorer;             /* Explorateur de contenus     */
    GContentResolver *resolver;             /* Résolveur de contenus       */
    GScanNamespace *root_ns;                /* Espace de noms ROST racine  */

    /**
     * On mémorise les passages réussis.
     */
    if (!result)
    {
        result = true;

        srand(time(NULL) + getpid());

        cfgdir = get_xdg_config_dir("chrysalide" G_DIR_SEPARATOR_S "chrysalide");
        result &= (ensure_path_exists(cfgdir) == 0);
        free(cfgdir);

        ERR_load_crypto_strings();
        SSL_load_error_strings();
        SSL_library_init();

        if (result) result = init_global_works();

        if (result) result = load_hard_coded_collection_definitions();

        if (cs)
        {
            g_boxed_type_register_static("vmpa_t",
                                         (GBoxedCopyFunc)dup_vmpa,
                                         (GBoxedFreeFunc)delete_vmpa);

            if (result) result = load_main_config_parameters();

            if (result) result = g_generic_config_read(get_main_configuration());

            explorer = g_content_explorer_new();
            set_current_content_explorer(explorer);

            resolver = g_content_resolver_new();
            set_current_content_resolver(resolver);

#ifdef INCLUDE_MAGIC_SUPPORT
            if (result) result = init_magic_cookie();
#endif

            root_ns = g_scan_namespace_new(NULL);
            set_rost_root_namespace(root_ns);

            if (result) result = populate_main_scan_namespace(root_ns);
            if (result) result = load_all_known_scan_token_modifiers();

            if (result) result = init_segment_content_hash_table();

            register_arch_gtypes();
            init_operands_factory();

            if (result) result = init_chrysalide_dynamic_types();

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cs = précise si l'appel est réalisé du côté client.          *
*                                                                             *
*  Description : Décharge les éléments de base du programme.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_all_core_components(bool cs)
{
    if (cs)
    {
        exit_chrysalide_dynamic_types();

        exit_operands_factory();

        unload_demanglers_definitions();

        unload_processors_definitions();

        unload_all_scan_token_modifiers();
        set_rost_root_namespace(NULL);

#ifdef INCLUDE_MAGIC_SUPPORT
        exit_magic_cookie();
#endif

        set_current_content_resolver(NULL);

        set_current_content_explorer(NULL);

        g_generic_config_write(get_main_configuration());

        unload_main_config_parameters();

    }

    unload_collection_definitions();

    exit_global_works();

    ERR_free_strings();

}
