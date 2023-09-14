
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.h - prototypes pour l'intégration du répertoire gui en tant que module
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


#ifndef _PLUGINS_PYCHRYSALIDE_GUI_MODULE_H
#define _PLUGINS_PYCHRYSALIDE_GUI_MODULE_H


#include <Python.h>
#include <stdbool.h>



/* Ajoute le module 'gui' à un module Python. */
bool add_gui_module(PyObject *);

/* Intègre les objets du module 'gui'. */
bool populate_gui_module(void);



#endif  /* _PLUGINS_PYCHRYSALIDE_GUI_MODULE_H */
