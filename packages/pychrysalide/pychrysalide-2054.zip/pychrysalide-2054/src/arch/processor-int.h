
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.h - prototypes pour la définition générique interne des architectures
 *
 * Copyright (C) 2008-2019 Cyrille Bagard
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


#ifndef _ARCH_PROCESSOR_INT_H
#define _ARCH_PROCESSOR_INT_H


#include "processor.h"



/* Taille des pré-allocations pour les instructions */
#define COV_ALLOC_BLOCK 100


/* Fournit la désignation interne du processeur d'architecture. */
typedef char * (* get_processor_key_fc) (const GArchProcessor *);

/* Fournit le nom humain de l'architecture visée. */
typedef char * (* get_processor_desc_fc) (const GArchProcessor *);

/* Fournit la taille de l'espace mémoire d'une architecture. */
typedef MemoryDataSize (* get_processor_memsize_fc) (const GArchProcessor *);

/* Fournit la taille min. des instructions d'une architecture. */
typedef MemoryDataSize (* get_processor_inssize_fc) (const GArchProcessor *);

/* Indique si l'architecture possède un espace virtuel ou non. */
typedef bool (* has_processor_vspace_fc) (const GArchProcessor *);

/* Fournit un contexte propre au processeur d'une architecture. */
typedef GProcContext * (* get_processor_context_fc) (const GArchProcessor *);

/* Désassemble une instruction dans un flux de données. */
typedef GArchInstruction * (* disass_instr_fc) (const GArchProcessor *, GProcContext *, const GBinContent *, vmpa2t *, GExeFormat *);


/* Description d'une erreur */
typedef struct _proc_error
{
    ArchProcessingError type;               /* Type d'erreur               */

    vmpa2t addr;                            /* Localisation du problème    */
    char *desc;                             /* Description du soucis       */

} proc_error;

/* Couverture d'un groupe d'instructions */
struct _instr_coverage
{
    mrange_t range;                         /* Couverture du groupement    */

    size_t start;                           /* Indice de départ            */
    size_t count;                           /* Quantité d'inclusions       */

};


/* Définition générique d'un processeur d'architecture (instance) */
struct _GArchProcessor
{
    GObject parent;                         /* A laisser en premier        */

    SourceEndian endianness;                /* Boutisme de l'architecture  */

    GArchInstruction **instructions;        /* Instructions désassemblées  */
    size_t instr_count;                     /* Taille de la liste aplatie  */
    unsigned int stamp;                     /* Marque de suivi des modifs  */
    GMutex mutex;                           /* Verrou pour l'accès         */
#ifndef NDEBUG
    gint locked;                            /* Statut d'accès à la liste   */
#endif

    proc_error *errors;                     /* Liste d'erreurs rencontrées */
    size_t error_count;                     /* Taille de cette liste       */
    GMutex error_mutex;                     /* Verrou pour l'accès         */
#ifndef NDEBUG
    gint error_locked;                      /* Statut d'accès à la liste   */
#endif

    instr_coverage *coverages;              /* Liste de couvertures        */
    size_t cov_allocated;                   /* Taille de la liste allouée  */
    size_t cov_count;                       /* Taille de la liste utilisée */

};

/* Définition générique d'un processeur d'architecture (classe) */
struct _GArchProcessorClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    get_processor_key_fc get_key;           /* Code représentant la classe */
    get_processor_desc_fc get_desc;         /* Description humaine         */
    get_processor_memsize_fc get_memsize;   /* Taille d'un mot classique   */
    get_processor_inssize_fc get_inssize;   /* Taille minimale d'instruct° */
    has_processor_vspace_fc has_vspace;     /* Présence d'un espace virtuel*/

    get_processor_context_fc get_ctx;       /* Obtention d'un contexte     */
    disass_instr_fc disassemble;            /* Traduction en instructions  */

    /* Signaux */

    void (* changed) (GArchProcessor *, GArchInstruction *, gboolean);

};



#endif  /* _ARCH_PROCESSOR_INT_H */
