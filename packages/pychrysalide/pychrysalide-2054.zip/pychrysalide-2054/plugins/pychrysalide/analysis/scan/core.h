
/* Chrysalide - Outil d'analyse de fichiers binaires
 * core.h - prototypes pour l'équivalent Python du fichier "analysis/scan/core.h"
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#ifndef _PLUGINS_PYCHRYSALIDE_CORE_CORE_H
#define _PLUGINS_PYCHRYSALIDE_CORE_CORE_H


#include <Python.h>
#include <stdbool.h>



/* Définit une extension du module 'scan' à compléter. */
bool populate_scan_module_with_core_methods(void);



#endif  /* _PLUGINS_PYCHRYSALIDE_CORE_CORE_H */
