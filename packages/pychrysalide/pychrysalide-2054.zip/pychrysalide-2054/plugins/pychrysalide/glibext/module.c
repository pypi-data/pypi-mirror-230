
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire glibext en tant que module
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "module.h"


#include <assert.h>


#include "binarycursor.h"
#include "binportion.h"
#include "buffercache.h"
#include "bufferline.h"
#include "bufferview.h"
#include "comparison.h"
#include "configuration.h"
#include "linecursor.h"
#include "linegen.h"
#include "loadedpanel.h"
#include "named.h"
#include "singleton.h"
#include "../helpers.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Ajoute le module 'glibext' à un module Python.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_glibext_module(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *module;                       /* Sous-module mis en place    */

#define PYCHRYSALIDE_GLIBEXT_DOC                                        \
    "This module contains the definition of some objects derived from"  \
    " the GObject structure.\n"                                         \
    "\n"                                                                \
    "These common objects are used in several places inside Chrysalide" \
    " and could be seen as extensions to the GLib API."

    static PyModuleDef py_chrysalide_glibext_module = {

        .m_base = PyModuleDef_HEAD_INIT,

        .m_name = "pychrysalide.glibext",
        .m_doc  = PYCHRYSALIDE_GLIBEXT_DOC,

        .m_size = -1,

    };

    module = build_python_module(super, &py_chrysalide_glibext_module);

    result = (module != NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Intègre les objets du module 'glibext'.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_glibext_module(void)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (result) result = ensure_python_singleton_candidate_is_registered();

    if (result) result = ensure_python_binary_cursor_is_registered();
    if (result) result = ensure_python_binary_portion_is_registered();
    if (result) result = ensure_python_buffer_cache_is_registered();
    if (result) result = ensure_python_buffer_line_is_registered();
#ifdef INCLUDE_GTK_SUPPORT
    if (result) result = ensure_python_buffer_view_is_registered();
#endif
    if (result) result = ensure_python_comparable_item_is_registered();
    if (result) result = ensure_python_config_param_is_registered();
    if (result) result = ensure_python_config_param_iterator_is_registered();
    if (result) result = ensure_python_generic_config_is_registered();
    if (result) result = ensure_python_line_cursor_is_registered();
    if (result) result = ensure_python_line_generator_is_registered();
#ifdef INCLUDE_GTK_SUPPORT
    if (result) result = ensure_python_loaded_panel_is_registered();
    if (result) result = ensure_python_named_widget_is_registered();
#endif
    if (result) result = ensure_python_singleton_factory_is_registered();

    assert(result);

    return result;

}
