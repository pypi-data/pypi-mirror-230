
/* Chrysalide - Outil d'analyse de fichiers binaires
 * constants.h - prototypes pour l'équivalent Python partiel du fichier "plugins/dex/dex_def.h"
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#ifndef _PLUGINS_DEX_PYTHON_CONSTANTS_H
#define _PLUGINS_DEX_PYTHON_CONSTANTS_H


#include <Python.h>
#include <stdbool.h>



/* Définit les constantes communes pour le format Dex. */
bool define_python_dex_format_common_constants(PyTypeObject *);



#endif  /* _PLUGINS_DEX_PYTHON_CONSTANTS_H */
