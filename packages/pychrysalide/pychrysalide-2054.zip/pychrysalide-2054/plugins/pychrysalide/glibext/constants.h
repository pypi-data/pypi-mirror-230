
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.h - prototypes pour l'ajout des constantes de base pour les extensions à la GLib
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _PLUGINS_PYCHRYSALIDE_GLIBEXT_CONSTANTS_H
#define _PLUGINS_PYCHRYSALIDE_GLIBEXT_CONSTANTS_H


#include <Python.h>
#include <stdbool.h>



/* Définit les constantes relatives aux portions de binaires. */
bool define_binary_portion_constants(PyTypeObject *);

/* Tente de convertir en constante PortionAccessRights. */
int convert_to_portion_access_rights(PyObject *, void *);

/* Définit les constantes relatives aux lignes de tampon. */
bool define_buffer_line_constants(PyTypeObject *);

/* Tente de convertir en constante BufferLineFlags. */
int convert_to_buffer_line_flags(PyObject *, void *);

/* Définit les constantes relatives aux modes de comparaison. */
bool define_comparable_item_constants(PyTypeObject *);

/* Définit les constantes relatives aux paramètres de configuration. */
bool define_config_param_constants(PyTypeObject *);

/* Tente de convertir en constante ConfigParamType. */
int convert_to_config_param_type(PyObject *, void *);

/* Définit les constantes relatives aux segments de ligne. */
bool define_line_segment_constants(PyTypeObject *);

/* Tente de convertir en constante RenderingTagType. */
int convert_to_rendering_tag_type(PyObject *, void *);

#ifdef INCLUDE_GTK_SUPPORT

/* Définit les constantes relatives aux panneaux de chargement. */
bool define_loaded_panel_constants(PyTypeObject *);

/* Tente de convertir en constante ScrollPositionTweak. */
int convert_to_scroll_position_tweak(PyObject *, void *);

#endif



#endif  /* _PLUGINS_PYCHRYSALIDE_GLIBEXT_CONSTANTS_H */
