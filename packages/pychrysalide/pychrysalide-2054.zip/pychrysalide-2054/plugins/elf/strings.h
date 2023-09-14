
/* Chrysalide - Outil d'analyse de fichiers binaires
 * strings.h - prototypes pour la recherche des chaînes contenues dans un ELF
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#ifndef _PLUGINS_ELF_STRINGS_H
#define _PLUGINS_ELF_STRINGS_H


#include "format.h"


#include <glibext/delayed.h>
#include <glibext/notifier.h>



/* Charge en mémoire toutes les chaînes trouvées. */
bool find_all_elf_strings(GElfFormat *, wgroup_id_t , GtkStatusStack *);



#endif  /* _PLUGINS_ELF_STRINGS_H */
