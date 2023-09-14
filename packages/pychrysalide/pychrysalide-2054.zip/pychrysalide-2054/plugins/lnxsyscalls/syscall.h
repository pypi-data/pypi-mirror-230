
/* Chrysalide - Outil d'analyse de fichiers binaires
 * syscall.h - prototypes pour la définition d'appels système Linux
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


#ifndef _PLUGINS_LNXSYSCALLS_SYSCALL_H
#define _PLUGINS_LNXSYSCALLS_SYSCALL_H


#include <sys/types.h>



/* Information quant à un appel */
typedef struct _syscall_info_t
{
    unsigned int nr;                        /* Numéro de l'appel           */
    char *name;                             /* Désignation de l'appel      */

    size_t argc;                            /* Nombre d'arguments utilisés */
    char *argv[6];                          /* Argument possibles          */

    char *filename;                         /* Origine dans le code source */
    unsigned int line;                      /* Numéro de ligne dans ce code*/

} syscall_info_t ;


/* Crée un début de description d'appel système. */
syscall_info_t *create_syscall_info(unsigned int, const char *);

/* Efface de la mémoire une description d'appel système. */
void delete_syscall_info(syscall_info_t *);

/* Ajoute un argument à une description d'appel système. */
void append_arg_to_syscall_info(syscall_info_t *, const char *);



#endif  /* _PLUGINS_LNXSYSCALLS_SYSCALL_H */
