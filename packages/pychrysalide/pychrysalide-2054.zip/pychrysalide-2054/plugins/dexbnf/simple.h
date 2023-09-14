
/* Chrysalide - Outil d'analyse de fichiers binaires
 * simple.h - prototypes pour le décodage de simples chaînes de caractères Dex
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _PLUGINS_DEXBNF_SIMPLE_H
#define _PLUGINS_DEXBNF_SIMPLE_H


#include <common/ibuf.h>



/* Extrait une simple chaîne de caractères depuis un codage Dex. */
char *dcd_simple_name(input_buffer *);



#endif  /* _PLUGINS_DEXBNF_SIMPLE_H */
