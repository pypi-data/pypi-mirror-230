
/* Chrysalide - Outil d'analyse de fichiers binaires
 * hops.h - prototypes pour les particularités de chasse propres à une architecture
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


#ifndef _PLUGINS_LNXSYSCALLS_HOPS_H
#define _PLUGINS_LNXSYSCALLS_HOPS_H


#include <stdbool.h>


#include <arch/processor.h>


#include "collect.h"
#include "syscall.h"
#include "writer.h"



/* Détermine si l'instruction lance un appel syystème. */
typedef bool (* is_lsyscall_fc) (GArchInstruction *);

/* Identifie le numéro d'appel système en cours de manipulation. */
typedef bool (* resolve_lsyscall_nr_fc) (tracked_path *, GArchProcessor *, const hunting_ops *, unsigned int *);

/* Marque les registres associés aux n premiers arguments. */
typedef bool (* look_for_lsyscall_args_fc) (tracked_path *, size_t, size_t);

/* Commente autant que possible un appel système brut. */
typedef void (* comment_lsyscall_fc) (tracked_path *, size_t, syscall_info_t *, comment_writer *);


/* Opérations adaptées pour une chasse donnée */
typedef struct _hunting_ops
{
    const char *arch;                       /* Rappel de l'architecture    */

    is_lsyscall_fc is_syscall;              /* Identification d'un appel   */
    resolve_lsyscall_nr_fc resolve_nr;      /* Récupération d'un numéro    */
    look_for_lsyscall_args_fc look_for_args;/* Mise à prix de N arguments  */
    comment_lsyscall_fc comment;            /* Inscription de commentaires */

} hunting_ops;



#endif  /* _PLUGINS_LNXSYSCALLS_HOPS_H */
