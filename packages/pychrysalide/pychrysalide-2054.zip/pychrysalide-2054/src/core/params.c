
/* Chrysalide - Outil d'analyse de fichiers binaires
 * params.c - éléments de la configuration principale
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


#include "params.h"


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Procède au chargement de la configuration principale.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_main_config_parameters(void)
{
    bool result;                            /* Bilan à retourner           */
    GGenConfig *config;                     /* Configuration à charger     */

    config = g_generic_config_new_from_file("main");
    set_main_configuration(config);

    result = g_generic_config_create_param(config, MPK_FORMAT_NO_NAME, CPT_BOOLEAN, false);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_INTERNAL_THEME, CPT_STRING, "Adwaita");
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_TITLE_BAR, CPT_BOOLEAN, true);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_LAST_PROJECT, CPT_STRING, NULL);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_SKIP_EXIT_MSG, CPT_BOOLEAN, false);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_MAXIMIZED, CPT_BOOLEAN, true);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_ELLIPSIS_HEADER, CPT_INTEGER, 54);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_ELLIPSIS_TAB, CPT_INTEGER, 35);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_WELCOME_STARTUP, CPT_BOOLEAN, true);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_WELCOME_CHECK, CPT_BOOLEAN, false);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_LABEL_OFFSET, CPT_INTEGER, 10);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_HEX_PADDING, CPT_INTEGER, 10);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_SELECTION_LINE, CPT_BOOLEAN, true);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_TOOLTIP_MAX_CALLS, CPT_INTEGER, 5);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_TOOLTIP_MAX_STRINGS, CPT_INTEGER, 5);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_HEX_UPPER_CASE, CPT_BOOLEAN, true);
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_LINK_DEFAULT, CPT_COLOR, ((GdkRGBA []) { { 0, 0, 0, 1.0 } }));
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_LINK_BRANCH_TRUE, CPT_COLOR, ((GdkRGBA []) { { 0, 0.6, 0, 1.0 } }));
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_LINK_BRANCH_FALSE, CPT_COLOR, ((GdkRGBA []) { { 0.8, 0, 0, 1.0 } }));
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_LINK_LOOP, CPT_COLOR, ((GdkRGBA []) { { 0, 0, 0.8, 1.0 } }));
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_KEYBINDINGS_EDIT, CPT_STRING, "<Shift>F2");
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_TMPDIR, CPT_STRING, "/tmp/chrysalide");
    if (!result) goto exit;

    result = g_generic_config_create_param(config, MPK_AUTO_SAVE, CPT_BOOLEAN, true);
    if (!result) goto exit;

    g_generic_config_create_group(config, "gui.panels.positions", CPT_INTEGER);

    g_generic_config_create_group(config, "gui.panels.dock_at_startup", CPT_BOOLEAN);
    g_generic_config_create_group(config, "gui.panels.path", CPT_STRING);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Procède au déchargement de la configuration principale.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_main_config_parameters(void)
{
    GGenConfig *config;                     /* Configuration à décharger   */

    config = get_main_configuration();

    g_object_unref(G_OBJECT(config));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = éventuelle configuration à définir comme principale.*
*                                                                             *
*  Description : Fournit un lien vers la configuration principale.            *
*                                                                             *
*  Retour      : Configuration prête à emploi ou NULL si aucune définie.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGenConfig *_get_main_configuration(GGenConfig *config)
{
    static GGenConfig *result = NULL;       /* Structure à retourner       */

    if (config != NULL)
        result = config;

    return result;

}
