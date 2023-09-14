
/* Chrysalide - Outil d'analyse de fichiers binaires
 * v21.h - prototypes pour l'annotation des parties spécifiques à la version 2.1/2.2 de Mobicore
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


#ifndef _PLUGINS_READMC_V21_H
#define _PLUGINS_READMC_V21_H


#include <format/format.h>
#include <format/preload.h>



/* Charge les symboles d'un en-tête v2.1/2.2 de Mobicore. */
bool annotate_mobicore_v21_header(GBinFormat *, GPreloadInfo *, vmpa2t *);



#endif  /* _PLUGINS_READMC_V21_H */
