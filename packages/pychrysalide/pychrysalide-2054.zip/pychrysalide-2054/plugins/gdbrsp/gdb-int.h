
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gdb.h - prototypes pour le débogage à l'aide de gdb.
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


#ifndef _DEBUG_GDBRSP_GDB_INT_H
#define _DEBUG_GDBRSP_GDB_INT_H


#include "aops.h"
#include "gdb.h"
#include "stream.h"
#include "support.h"
#include "target.h"
#include "../break-int.h"
#include "../debugger-int.h"










/* Définition d'un point d'arrêt appliqué */
typedef struct _gdb_breakpoint
{
    raw_breakpoint raw;                     /* A laisser en premier        */

    bool is_z;                              /* Usage de commande dédiée ?  */

    union
    {
        const char *kind;                   /* Précision de taille         */

        struct
        {
            uint8_t memory[16];             /* Données d'origine remplacées*/
            size_t len;                     /* Quantité de ces données     */
        };

    };

} gdb_breakpoint;














/* Débogueur utilisant un serveur GDB (instance) */
struct _GGdbDebugger
{
    GBinaryDebugger parent;                 /* A laisser en premier        */

    SourceEndian endian;                    /* Boutisme du format          */
    MemoryDataSize msize;                   /* Taille des adresses         */

    const gdb_arch_ops *ops;                /* Opérations spécifiques      */

    GGdbStream *stream;                     /* Flux de communication       */
    GGdbSupport *support;                   /* Configuration à adopter     */
    GGdbTarget *target;                     /* Architecture ciblée par GDB */

};


/* Débogueur utilisant un serveur GDB (classe) */
struct _GGdbDebuggerClass
{
    GBinaryDebuggerClass parent;            /* A laisser en premier        */

};



/* ------------------------ ACCUEIL D'EVENEMENTS ASYNCHRONES ------------------------ */


/* Réagit à la réception d'un signal par le programme étudié. */
void g_gdb_debugger_receive_signal_reply(GGdbDebugger *, int);

/* Réagit à la sortie d'exécution d'un programme étudié. */
void g_gdb_debugger_receive_exit_reply(GGdbDebugger *, int, pid_t);



#endif  /* _DEBUG_GDBRSP_GDB_INT_H */
