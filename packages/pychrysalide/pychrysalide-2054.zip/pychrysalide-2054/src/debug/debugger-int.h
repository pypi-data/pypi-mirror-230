
/* Chrysalide - Outil d'analyse de fichiers binaires
 * debugger-int.h - prototypes pour l'interface des débogueurs
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#ifndef _DEBUG_DEBUGGER_INT_H
#define _DEBUG_DEBUGGER_INT_H


#include "debugger.h"


#include "break.h"



//#include <gtk/gtk.h>////////////////////////////////////////////







/* Procède au démarrage effectif de la session de débogage. */
typedef bool (* attach_debugger_fc) (GBinaryDebugger *);

/* Démarre, met en pause ou tue une procédure de débogage. */
typedef bool (* basic_debugger_fc) (GBinaryDebugger *);

/* Reprend une procédure de débogage. */
//typedef bool (* resume_debugger_fc) (GBinaryDebugger *);

/* Fournit les identifiants de tous les threads actifs. */
//typedef pid_t * (* dbg_list_all_threads_fc) (GBinaryDebugger *, char ***, size_t *);

/* Fournit la liste des frames courantes d'un thread donné. */
//typedef dbg_frame_t * (* dbg_get_frames_stack_fc) (GBinaryDebugger *, pid_t, size_t *);

/* Fournit la valeur des registres de l'architecture. */
//typedef register_value * (* get_register_values_fc) (GBinaryDebugger *, size_t *);






/* Fournit les identifiants de tous les threads actifs. */
typedef dbg_thread_desc * (* list_all_threads_fc) (GBinaryDebugger *, size_t *);




/* Lit une valeur quelconque à une adresse arbitraire. */
typedef bool (* read_mem_any_fc) (GBinaryDebugger *, virt_t, size_t, ...);

/* Ecrit une valeur quelconque à une adresse arbitraire. */
typedef bool (* write_mem_any_fc) (GBinaryDebugger *, virt_t, size_t, ...);

/* Liste l'ensemble des registres appartenant à un groupe. */
typedef char ** (* get_reg_names_fc) (const GBinaryDebugger *, const char *, size_t *);

/* Indique la taille associée à un registre donné. */
typedef unsigned int (* get_reg_size_fc) (const GBinaryDebugger *, const char *);

/* Lit une valeur quelconque à partir d'un registre. */
typedef bool (* read_write_reg_any_fc) (GBinaryDebugger *, const char *, size_t, ...);



/* Détermine le point d'exécution courant. */
typedef bool (* get_current_pc_fc) (GBinaryDebugger *, virt_t *);

/* Remonte la pile d'appels jusqu'au point courant. */
typedef bool (* get_call_stack_fc) (GBinaryDebugger *, virt_t **, size_t *);



/* Ajoute un point d'arrêt basique en mémoire. */
typedef raw_breakpoint * (* enable_mem_bp_fc) (GBinaryDebugger *, virt_t);

/* Retire un point d'arrêt basique en mémoire. */
typedef bool (* disable_mem_bp_fc) (GBinaryDebugger *, raw_breakpoint *);

/* Redémarre le processus de débogage lié à un serveur GDB. */
typedef bool (* restart_debugger_fc) (GBinaryDebugger *);

/* Remet en marche le débogueur courant. */
typedef bool (* resume_debugger_fc) (GBinaryDebugger *);









/* Définition des fonctionnalités d'un débogueur (instance) */
struct _GBinaryDebugger
{
    GObject parent;                         /* A laisser en premier        */

    GLoadedBinary *binary;                  /* Cible à traiter             */

    attach_debugger_fc attach;              /* Démarre le débogueur        */

    basic_debugger_fc run;                  /* Démarre le débogueur        */
    basic_debugger_fc pause;                /* Met en pause le débogueur   */
    basic_debugger_fc kill;                 /* Tue le débogueur            */



    raw_breakpoint **bpoints;               /* Points d'arrêt posés        */
    size_t bp_count;                        /* Quantité de ces points posés*/
    GRWLock bp_lock;                        /* Verrou d'accès à la liste   */

};


/* Définition des fonctionnalités d'un débogueur (classe) */
struct _GBinaryDebuggerClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    list_all_threads_fc all_threads;        /* Liste des threads actifs    */

    read_mem_any_fc read_mem;               /* Lecture d'une valeur XX bits*/
    read_mem_any_fc write_mem;              /* Ecriture d'une valeur X bits*/
    get_reg_names_fc get_reg_names;         /* Liste des registres         */
    get_reg_size_fc get_reg_size;           /* Taille d'un registre donné  */
    read_write_reg_any_fc read_reg;         /* Lecture de registre XX bits */
    read_write_reg_any_fc write_reg;        /* Ecriture de registre XX bits*/

    get_current_pc_fc get_current_pc;       /* Obtention du point d'exéc.  */
    get_call_stack_fc get_call_stack;       /* Obtention de pile d'appels  */

    enable_mem_bp_fc enable_bp;             /* Mise en place d'un arrêt    */
    disable_mem_bp_fc disable_bp;           /* Retrait d'un point d'arrêt  */

    restart_debugger_fc restart;            /* Redémarre le débogueur      */
    resume_debugger_fc resume;              /* Relance le débogueur        */

    /* Signaux */

    void (* signaled) (GBinaryDebugger *, int);
    void (* exited) (GBinaryDebugger *, int, pid_t);
    void (* terminated) (GBinaryDebugger *, int, pid_t);

    void (* stopped) (GBinaryDebugger *, virt_t);




    /* Signaux */

    void (* debugger_halted) (GBinaryDebugger *, int, vmpa_t, pid_t);





    void (* mem_bp_handled) (GBinaryDebugger *, bool, virt_t);

};



/* ------------------------- MANIPULATION DE L'ETAT COURANT ------------------------- */


/* Réagit à un arrêt du flot d'exécution. */
void on_binary_debugger_stopped(GBinaryDebugger *, virt_t);

/* Réagit à la fin de l'opération de débogage. */
void on_binary_debugger_finished(GBinaryDebugger *, pid_t);



#endif  /* _DEBUG_DEBUGGER_INT_H */
