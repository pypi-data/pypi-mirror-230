
/* Chrysalide - Outil d'analyse de fichiers binaires
 * try_n_catch.h - prototypes pour le support des exceptions chez Android
 *
 * Copyright (C) 2012-2018 Cyrille Bagard
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


#ifndef _PLUGINS_TRY_N_CATCH_H
#define _PLUGINS_TRY_N_CATCH_H


#include <analysis/binary.h>



/* Traite tous les gestionnaires d'exception trouvés. */
bool process_exception_handlers(GLoadedBinary *, bool);



#endif  /* _PLUGINS_TRY_N_CATCH_H */
