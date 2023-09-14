
/* Chrysalide - Outil d'analyse de fichiers binaires
 * code.h - prototypes pour l'annotation des éléments de code Dalvik
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#ifndef _PLUGINS_READDEX_CODE_H
#define _PLUGINS_READDEX_CODE_H


#include <format/preload.h>
#include <plugins/dex/format.h>



/* Commente les définitions d'un corps de méthode. */
bool annotate_dex_code_item(const GDexFormat *, GPreloadInfo *, uleb128_t);



#endif  /* _PLUGINS_READDEX_CODE_H */
