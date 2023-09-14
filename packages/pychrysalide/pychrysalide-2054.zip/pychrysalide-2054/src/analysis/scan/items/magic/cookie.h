
/* Chrysalide - Outil d'analyse de fichiers binaires
 * cookie.h - prototypes pour le chargement des motifs de reconnaissance de contenus
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_SCAN_ITEMS_MAGIC_COOKIE_H
#define _ANALYSIS_SCAN_ITEMS_MAGIC_COOKIE_H


#include <magic.h>
#include <stdbool.h>



/* Charge les motifs de reconnaissance de contenus. */
bool init_magic_cookie(void);

/* Décharge les motifs de reconnaissance de contenus. */
void exit_magic_cookie(void);

/* Fournit la référence aux mécanismes de reconnaissance. */
magic_t get_magic_cookie(int);



#endif  /* _ANALYSIS_SCAN_ITEMS_MAGIC_COOKIE_H */
