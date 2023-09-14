
/* Chrysalide - Outil d'analyse de fichiers binaires
 * xdg.h - prototypes pour des compléments mineurs au support Freedesktop
 *
 * Copyright (C) 2014-2018 Cyrille Bagard
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


#ifndef _COMMON_XDG_H
#define _COMMON_XDG_H



/* Détermine le chemin d'un répertoire selon les specs. XDG. */
char *get_xdg_config_dir(const char *);



#endif  /* _COMMON_XDG_H */
