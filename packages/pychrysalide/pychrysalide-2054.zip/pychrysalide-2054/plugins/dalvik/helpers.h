
/* Chrysalide - Outil d'analyse de fichiers binaires
 * helpers.h - prototypes pour l'aide à la mise en place des opérandes Dalvik
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


#ifndef _PLUGINS_DALVIK_HELPERS_H
#define _PLUGINS_DALVIK_HELPERS_H


#include "operand.h"



/**
 * Glues purement internes.
 */

#define DALVIK_OPT_POOL_STRING  DALVIK_OP_POOL(DPT_STRING)
#define DALVIK_OPT_POOL_TYPE    DALVIK_OP_POOL(DPT_TYPE)
#define DALVIK_OPT_POOL_FIELD   DALVIK_OP_POOL(DPT_FIELD)
#define DALVIK_OPT_POOL_METH    DALVIK_OP_POOL(DPT_METHOD)



#endif  /* _PLUGINS_DALVIK_HELPERS_H */
