
/* Chrysalide - Outil d'analyse de fichiers binaires
 * nproc.h - prototypes pour la détermination du volume de traitements parallèles idéal
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#ifndef _CORE_NPROC_H
#define _CORE_NPROC_H


#include <glib.h>



/* Indique le nombre idéal de tâches pour bien occuper le CPU. */
guint get_max_online_threads(void);


/**
 * Calcul de tranches de travaux, avec prise en compte des cas particuliers.
 */
#define compute_run_size(qty, cpus)                 \
    ({                                              \
        if (qty == 0)                               \
            *(cpus) = 0;                            \
        else                                        \
        {                                           \
            *(cpus) = get_max_online_threads();     \
            if (qty < *(cpus))                      \
                *(cpus) = qty;                      \
        }                                           \
        *(cpus) > 0 ? qty / *(cpus) : 0;            \
    })



#endif  /* _CORE_NPROC_H */
