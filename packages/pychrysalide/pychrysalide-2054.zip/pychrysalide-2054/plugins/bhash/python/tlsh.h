
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tlsh.h - équivalent Python du fichier "plugins/bhash/tlsh.h"
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#ifndef _PLUGINS_BHASH_PYTHON_TLSH_H
#define _PLUGINS_BHASH_PYTHON_TLSH_H


#include <Python.h>
#include <stdbool.h>



/* Définit une extension du module 'bhash' à compléter. */
bool populate_bhash_module_with_tlsh(PyObject *);



#endif  /* _PLUGINS_BHASH_PYTHON_TLSH_H */
