
/* Chrysalide - Outil d'analyse de fichiers binaires
 * params.h - prototypes pour les éléments de la configuration principale
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


#ifndef _CORE_PARAMS_H
#define _CORE_PARAMS_H


#include "../glibext/configuration.h"



/**
 * Clefs de paramètres de configuration principale.
 */

#define MPK_FORMAT_NO_NAME      "format.symbols.use_phy_instead_of_virt"
#define MPK_INTERNAL_THEME      "gui.editor.theme"
#define MPK_TITLE_BAR           "gui.editor.hide_titlebar"
#define MPK_LAST_PROJECT        "gui.editor.last_project"
#define MPK_SKIP_EXIT_MSG       "gui.editor.skip_exit_msg"
#define MPK_MAXIMIZED           "gui.editor.start_maximized"
#define MPK_ELLIPSIS_HEADER     "gui.editor.panels.ellipsis_header"
#define MPK_ELLIPSIS_TAB        "gui.editor.panels.ellipsis_tab"
#define MPK_WELCOME_STARTUP     "gui.editor.panels.welcome.show_at_startup"
#define MPK_WELCOME_CHECK       "gui.editor.panels.welcome.check_version"
#define MPK_LABEL_OFFSET        "gui.editor.views.label_offset"
#define MPK_HEX_PADDING         "gui.editor.views.hex_padding"
#define MPK_SELECTION_LINE      "gui.editor.views.selection_line"
#define MPK_TOOLTIP_MAX_CALLS   "gui.editor.views.tooltip_max_calls"
#define MPK_TOOLTIP_MAX_STRINGS "gui.editor.views.tooltip_max_strings"
#define MPK_HEX_UPPER_CASE      "gui.editor.views.hex.upper_case"
#define MPK_LINK_DEFAULT        "gui.editor.graph.link.default"
#define MPK_LINK_BRANCH_TRUE    "gui.editor.graph.link.branch_true"
#define MPK_LINK_BRANCH_FALSE   "gui.editor.graph.link.branch_false"
#define MPK_LINK_LOOP           "gui.editor.graph.link.loop"
#define MPK_KEYBINDINGS_EDIT    "gui.key_bindings.global.edit"
#define MPK_TMPDIR              "misc.tmpdir"
#define MPK_AUTO_SAVE           "project.autosave"



/* Procède au chargement de la configuration principale. */
bool load_main_config_parameters(void);

/* Procède au déchargement de la configuration principale. */
void unload_main_config_parameters(void);

#define set_main_configuration(cfg) _get_main_configuration(cfg)
#define get_main_configuration() _get_main_configuration(NULL)

/* Fournit un lien vers la configuration principale. */
GGenConfig *_get_main_configuration(GGenConfig *);



#endif  /* _CORE_PARAMS_H */
