
/* Chrysalide - Outil d'analyse de fichiers binaires
 * debugger.h - prototypes pour la gestion des différents débogueurs
 *
 * Copyright (C) 2010-2018 Cyrille Bagard
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


#ifndef _DEBUG_DEBUGGER_H
#define _DEBUG_DEBUGGER_H


#include <glib-object.h>
#include <stdint.h>


#include "misc.h"
#include "../analysis/binary.h"



/* ---------------------------- TRONC COMMUN DE DEBOGAGE ---------------------------- */


#define G_TYPE_BINARY_DEBUGGER              g_binary_debugger_get_type()
#define G_BINARY_DEBUGGER(obj)              (G_TYPE_CHECK_INSTANCE_CAST((obj), g_binary_debugger_get_type(), GBinaryDebugger))
#define G_IS_BINARY_DEBUGGER(obj)           (G_TYPE_CHECK_INSTANCE_TYPE((obj), g_binary_debugger_get_type()))
#define G_BINARY_DEBUGGER_CLASS(klass)      (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_BINARY_DEBUGGER, GBinaryDebuggerClass))
#define G_IS_BINARY_DEBUGGER_CLASS(klass)   (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_BINARY_DEBUGGER))
#define G_BINARY_DEBUGGER_GET_CLASS(obj)    (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_BINARY_DEBUGGER, GBinaryDebuggerClass))


/* Définition des fonctionnalités d'un débogueur (instance) */
typedef struct _GBinaryDebugger GBinaryDebugger;

/* Définition des fonctionnalités d'un débogueur (classe) */
typedef struct _GBinaryDebuggerClass GBinaryDebuggerClass;


/* Indique le type défini par la GLib pour le débogueur ptrace(). */
GType g_binary_debugger_get_type(void);

/* Démarre une procédure de débogage. */
bool g_binary_debugger_attach(GBinaryDebugger *);

/* Démarre une procédure de débogage. */
void g_binary_debugger_run(GBinaryDebugger *);

/* Reprend une procédure de débogage. */
//void g_binary_debugger_resume(GBinaryDebugger *);

/* Tue une procédure de débogage. */
void g_binary_debugger_kill(GBinaryDebugger *);

/* Fournit les identifiants de tous les threads actifs. */
//pid_t *g_binary_debugger_list_all_threads(GBinaryDebugger *, char ***, size_t *);

/* Fournit la liste des frames courantes d'un thread donné. */
//dbg_frame_t *g_binary_debugger_get_frames_stack(GBinaryDebugger *, pid_t, size_t *);

/* Fournit la valeur des registres de l'architecture. */
//register_value *g_binary_debugger_get_registers(GBinaryDebugger *, size_t *);














/* ---------------------------------------------------------------------------------- */
/*                     MANIPULATION DES DIFFERENTS THREADS ACTIFS                     */
/* ---------------------------------------------------------------------------------- */


/* Description humaine à représenter */
typedef struct _dbg_thread_desc
{
    dbg_thread_id_t id;                     /* Identifiant interne         */
    char *name;                             /* Dénomination humaine        */

} dbg_thread_desc;


/* Libère la mémoire d'une liste de threads actifs. */
void delete_dbg_thread_desc(dbg_thread_desc *, size_t);

/* Fournit les identifiants de tous les threads actifs. */
dbg_thread_desc *g_binary_debugger_list_all_threads(GBinaryDebugger *, size_t *);









/* --------------------------- ENTREES / SORTIES BASIQUES --------------------------- */


/* Lit une valeur de 8 bits à une adresse arbitraire. */
bool g_binary_debugger_read_memory_u8(GBinaryDebugger *, virt_t, uint8_t *);

/* Lit une valeur de 16 bits à une adresse arbitraire. */
bool g_binary_debugger_read_memory_u16(GBinaryDebugger *, virt_t, uint16_t *);

/* Lit une valeur de 32 bits à une adresse arbitraire. */
bool g_binary_debugger_read_memory_u32(GBinaryDebugger *, virt_t, uint32_t *);

/* Lit une valeur de 64 bits à une adresse arbitraire. */
bool g_binary_debugger_read_memory_u64(GBinaryDebugger *, virt_t, uint64_t *);

/* Lit une valeur de taille quelconque à une adresse arbitraire. */
bool g_binary_debugger_read_memory_data(GBinaryDebugger *, virt_t, uint8_t *, size_t);

/* Ecrit une valeur de 8 bits à une adresse arbitraire. */
bool g_binary_debugger_write_memory_u8(GBinaryDebugger *, virt_t, const uint8_t *);

/* Ecrit une valeur de 16 bits à une adresse arbitraire. */
bool g_binary_debugger_write_memory_u16(GBinaryDebugger *, virt_t, const uint16_t *);

/* Ecrit une valeur de 32 bits à une adresse arbitraire. */
bool g_binary_debugger_write_memory_u32(GBinaryDebugger *, virt_t, const uint32_t *);

/* Ecrit une valeur de 64 bits à une adresse arbitraire. */
bool g_binary_debugger_write_memory_u64(GBinaryDebugger *, virt_t, const uint64_t *);

/* Ecrit une valeur de taille quelconque à une adresse donnée. */
bool g_binary_debugger_write_memory_data(GBinaryDebugger *, virt_t, const uint8_t *, size_t);

/* Liste l'ensemble des registres appartenant à un groupe. */
char **g_binary_debugger_get_register_names(const GBinaryDebugger *, const char *, size_t *);

/* Indique la taille associée à un registre donné. */
unsigned int g_binary_debugger_get_register_size(const GBinaryDebugger *, const char *);

/* Lit une valeur de 8 bits à partir d'un registre. */
bool g_binary_debugger_read_register_u8(GBinaryDebugger *, const char *, uint8_t *);

/* Lit une valeur de 16 bits à partir d'un registre. */
bool g_binary_debugger_read_register_u16(GBinaryDebugger *, const char *, uint16_t *);

/* Lit une valeur de 32 bits à partir d'un registre. */
bool g_binary_debugger_read_register_u32(GBinaryDebugger *, const char *, uint32_t *);

/* Lit une valeur de 64 bits à partir d'un registre. */
bool g_binary_debugger_read_register_u64(GBinaryDebugger *, const char *, uint64_t *);

/* Ecrit une valeur de 8 bits dans un registre. */
bool g_binary_debugger_write_register_u8(GBinaryDebugger *, const char *, const uint8_t *);

/* Ecrit une valeur de 16 bits dans un registre. */
bool g_binary_debugger_write_register_u16(GBinaryDebugger *, const char *, const uint16_t *);

/* Ecrit une valeur de 32 bits dans un registre. */
bool g_binary_debugger_write_register_u32(GBinaryDebugger *, const char *, const uint32_t *);

/* Ecrit une valeur de 64 bits dans un registre. */
bool g_binary_debugger_write_register_u64(GBinaryDebugger *, const char *, const uint64_t *);



/* ------------------------- MANIPULATION DE L'ETAT COURANT ------------------------- */


/* Détermine le point d'exécution courant. */
bool g_binary_debugger_get_current_pc(GBinaryDebugger *, virt_t *);

/* Détermine l'adresse du premier retour d'appel. */
bool g_binary_debugger_get_return_pc(GBinaryDebugger *, virt_t *);

/* Détermine les prochaines probables instructions exécutées. */
virt_t *g_binary_debugger_get_next_pcs(GBinaryDebugger *, virt_t, bool, size_t *);

/* Remonte la pile d'appels jusqu'au point courant. */
bool g_binary_debugger_get_call_stack(GBinaryDebugger *, virt_t **, size_t *);



/* --------------------------- GESTION DES POINTS D'ARRET --------------------------- */


/* Ajoute un point d'arrêt basique en mémoire. */
bool g_binary_debugger_add_memory_breakpoint(GBinaryDebugger *, virt_t);

/* Retire un point d'arrêt basique en mémoire. */
bool g_binary_debugger_delete_memory_breakpoint(GBinaryDebugger *, virt_t);



/* -------------------------- CONTROLE DU FLOT D'EXECUTION -------------------------- */


/* Redémarre le processus de débogage. */
bool g_binary_debugger_restart(GBinaryDebugger *);

/* Remet en marche le débogueur courant. */
bool g_binary_debugger_resume(GBinaryDebugger *);

/* Relance l'exécution pour une seule instruction. */
bool g_binary_debugger_stepi(GBinaryDebugger *, bool);



#endif  /* _DEBUG_DEBUGGER_H */
