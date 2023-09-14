
/* Chrysalide - Outil d'analyse de fichiers binaires
 * processor.c - gestion générique des architectures
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


#include "processor.h"


#include <assert.h>
#include <malloc.h>
#include <stdlib.h>
#include <string.h>


#include <i18n.h>


#include "instruction-int.h"
#include "processor-int.h"
#include "../analysis/db/misc/rlestr.h"
#include "../analysis/storage/serialize-int.h"
#include "../common/sort.h"
#include "../core/logs.h"
#include "../glibext/chrysamarshal.h"


















/* Initialise la classe générique des processeurs. */
static void g_arch_processor_class_init(GArchProcessorClass *);

/* Initialise une instance de processeur d'architecture. */
static void g_arch_processor_init(GArchProcessor *);

/* Procède à l'initialisation de l'interface de sérialisation. */
static void g_arch_processor_serializable_init(GSerializableObjectInterface *);

/* Supprime toutes les références externes. */
static void g_arch_processor_dispose(GArchProcessor *);

/* Procède à la libération totale de la mémoire. */
static void g_arch_processor_finalize(GArchProcessor *);

/* Fournit un contexte générique pour l'exécution du processeur. */
static GProcContext *_g_arch_processor_get_context(const GArchProcessor *);



/* ------------------ CONSERVATION DES SOUCIS DURANT LE CHARGEMENT ------------------ */


/* Procède à la libération totale de la mémoire. */
static void g_arch_processor_finalize_errors(GArchProcessor *);

/* Charge les erreurs de chargement depuis une mémoire tampon. */
static bool g_arch_processor_load_errors(GArchProcessor *, packed_buffer_t *);

/* Sauvegarde les erreurs de chargement dans une mémoire tampon. */
static bool g_arch_processor_store_errors(GArchProcessor *, packed_buffer_t *);



/* ------------------ MANIPULATIONS DES INSTRUCTIONS DESASSEMBLEES ------------------ */


/* Procède à la libération totale de la mémoire. */
static void g_arch_processor_finalize_coverages(GArchProcessor *);

/* Démarre la définition d'un nouveau groupe d'instructions. */
static void g_arch_processor_add_new_coverage(GArchProcessor *, GArchInstruction *, size_t);

/* Termine la définition d'un nouveau groupe d'instructions. */
static void g_arch_processor_finish_last_coverage(GArchProcessor *, GArchInstruction *, size_t);

/* Coupe un groupe d'instructions en deux. */
static instr_coverage *g_arch_processor_split_coverages(GArchProcessor *, instr_coverage *, GArchInstruction *, size_t);

/* Fusionne deux groupes d'instructions. */
static void g_arch_processor_merge_coverages(GArchProcessor *, instr_coverage *, instr_coverage *);

/* Met à jour une série de groupes d'instructions. */
static void g_arch_processor_update_coverages(GArchProcessor *, instr_coverage *, bool);

/* Charge les plages de couvertures depuis une mémoire tampon. */
static bool g_arch_processor_load_coverages(GArchProcessor *, packed_buffer_t *);

/* Sauvegarde les plages de couvertures dans une mémoire tampon. */
static bool g_arch_processor_store_coverages(GArchProcessor *, packed_buffer_t *);

/* Recherche rapidement un indice d'instruction via une adresse. */
static bool g_arch_processor_find_covered_index_by_address(const GArchProcessor *, const instr_coverage *, const vmpa2t *, bool, size_t *);



/* -------------------- CONSERVATION ET RECHARGEMENT DES DONNEES -------------------- */


/* Charge un contenu depuis une mémoire tampon. */
static bool g_arch_processor_load(GArchProcessor *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_arch_processor_store(GArchProcessor *, GObjectStorage *, packed_buffer_t *);






/* Indique le type défini pour un processeur d'architecture. */
G_DEFINE_TYPE_WITH_CODE(GArchProcessor, g_arch_processor, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_SERIALIZABLE_OBJECT, g_arch_processor_serializable_init));



/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe générique des processeurs.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_processor_class_init(GArchProcessorClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_arch_processor_dispose;
    object->finalize = (GObjectFinalizeFunc)g_arch_processor_finalize;

    klass->get_ctx = _g_arch_processor_get_context;

    g_signal_new("changed",
                 G_TYPE_ARCH_PROCESSOR,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GArchProcessorClass, changed),
                 NULL, NULL,
                 g_cclosure_user_marshal_VOID__OBJECT_BOOLEAN,
                 G_TYPE_NONE, 2, G_TYPE_ARCH_INSTRUCTION, G_TYPE_BOOLEAN);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de processeur d'architecture.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_processor_init(GArchProcessor *proc)
{
    g_mutex_init(&proc->mutex);
#ifndef NDEBUG
    g_atomic_int_set(&proc->locked, 0);
#endif

    proc->errors = NULL;
    proc->error_count = 0;
    g_mutex_init(&proc->error_mutex);
#ifndef NDEBUG
    g_atomic_int_set(&proc->error_locked, 0);
#endif

    proc->coverages = NULL;
    proc->cov_allocated = 0;
    proc->cov_count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de sérialisation.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_processor_serializable_init(GSerializableObjectInterface *iface)
{
    iface->load = (load_serializable_object_cb)g_arch_processor_load;
    iface->store = (store_serializable_object_cb)g_arch_processor_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_processor_dispose(GArchProcessor *proc)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < proc->instr_count; i++)
    {
        /**
         * Pour éviter un cycle de maintien des références, on détruit tous
         * les liens depuis l'extérieur !
         */
        if (proc->instructions[i] != NULL)
            g_arch_instruction_delete_all_links(proc->instructions[i]);

        g_clear_object(&proc->instructions[i]);

    }

    g_mutex_clear(&proc->mutex);

    g_mutex_clear(&proc->error_mutex);

    G_OBJECT_CLASS(g_arch_processor_parent_class)->dispose(G_OBJECT(proc));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_processor_finalize(GArchProcessor *proc)
{
    if (proc->instructions != NULL)
        free(proc->instructions);

    g_arch_processor_finalize_errors(proc);

    g_arch_processor_finalize_coverages(proc);

    G_OBJECT_CLASS(g_arch_processor_parent_class)->finalize(G_OBJECT(proc));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture, spectatrice ici.                        *
*                                                                             *
*  Description : Fournit un contexte générique pour l'exécution du processeur.*
*                                                                             *
*  Retour      : Contexte mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GProcContext *_g_arch_processor_get_context(const GArchProcessor *proc)
{
    GProcContext *result;                   /* Instance à retourner        */

    result = g_object_new(G_TYPE_PROC_CONTEXT, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit la désignation interne du processeur d'architecture. *
*                                                                             *
*  Retour      : Simple chaîne de caractères.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_arch_processor_get_key(const GArchProcessor *proc)
{
    char *result;                           /* Désignation à renvoyer      */
    GArchProcessorClass *class;             /* Classe de l'instance        */

    class = G_ARCH_PROCESSOR_GET_CLASS(proc);

    if (class->get_key == NULL)
    {
        assert(false);
        result = NULL;
    }

    else
        result = class->get_key(proc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit le nom humain de l'architecture visée.               *
*                                                                             *
*  Retour      : Désignation humaine associée au processeur.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_arch_processor_get_desc(const GArchProcessor *proc)
{
    char *result;                           /* Désignation à renvoyer      */
    GArchProcessorClass *class;             /* Classe de l'instance        */

    class = G_ARCH_PROCESSOR_GET_CLASS(proc);

    if (class->get_desc == NULL)
    {
        assert(false);
        result = NULL;
    }

    else
        result = class->get_desc(proc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit le boustime du processeur d'une architecture.        *
*                                                                             *
*  Retour      : Boutisme associé au processeur.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

SourceEndian g_arch_processor_get_endianness(const GArchProcessor *proc)
{
    SourceEndian result;                    /* Boutisme à retourner        */

    result = proc->endianness;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit la taille de l'espace mémoire d'une architecture.    *
*                                                                             *
*  Retour      : Taille de l'espace mémoire.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

MemoryDataSize g_arch_processor_get_memory_size(const GArchProcessor *proc)
{
    MemoryDataSize result;                  /* Taille  à retourner         */
    GArchProcessorClass *class;             /* Classe de l'instance        */

    class = G_ARCH_PROCESSOR_GET_CLASS(proc);

    if (class->get_memsize == NULL)
    {
        assert(false);
        result = MDS_UNDEFINED;
    }

    else
        result = class->get_memsize(proc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Fournit la taille min. des instructions d'une architecture.  *
*                                                                             *
*  Retour      : Taille d'encodage des instructions.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

MemoryDataSize g_arch_processor_get_instruction_min_size(const GArchProcessor *proc)
{
    MemoryDataSize result;                  /* Taille  à retourner         */
    GArchProcessorClass *class;             /* Classe de l'instance        */

    class = G_ARCH_PROCESSOR_GET_CLASS(proc);

    if (class->get_inssize == NULL)
    {
        assert(false);
        result = MDS_UNDEFINED;
    }

    else
        result = class->get_inssize(proc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = processeur d'architecture à consulter.                *
*                                                                             *
*  Description : Indique si l'architecture possède un espace virtuel ou non.  *
*                                                                             *
*  Retour      : true si un espace virtuel existe, false sinon.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_processor_has_virtual_space(const GArchProcessor *proc)
{
    bool result;                            /* Indication à retourner      */
    GArchProcessorClass *class;             /* Classe de l'instance        */

    class = G_ARCH_PROCESSOR_GET_CLASS(proc);

    if (class->has_vspace == NULL)
    {
        assert(false);
        result = false;
    }

    else
        result = class->has_vspace(proc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture visée par la procédure.                  *
*                                                                             *
*  Description : Fournit un contexte propre au processeur d'une architecture. *
*                                                                             *
*  Retour      : Nouveau contexte mis à disposition.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GProcContext *g_arch_processor_get_context(const GArchProcessor *proc)
{
    GProcContext *result;                   /* Contexte à retourner        */
    GArchProcessorClass *class;             /* Classe de l'instance active */

    class = G_ARCH_PROCESSOR_GET_CLASS(proc);

    result = class->get_ctx(proc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc    = architecture visée par la procédure.               *
*                ctx     = contexte lié à l'exécution du processeur.          *
*                content = flux de données à analyser.                        *
*                pos     = position courante dans ce flux. [OUT]              *
*                format  = format du fichier contenant le code.               *
*                                                                             *
*  Description : Désassemble une instruction dans un flux de données.         *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_arch_processor_disassemble(const GArchProcessor *proc, GProcContext *ctx, const GBinContent *content, vmpa2t *pos, GExeFormat *format)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    vmpa2t back;                            /* Position sauvegardée        */

    assert(has_phys_addr(pos));

    copy_vmpa(&back, pos);

    result = G_ARCH_PROCESSOR_GET_CLASS(proc)->disassemble(proc, ctx, content, pos, format);

    if (result == NULL)
        copy_vmpa(pos, &back);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                    RASSEMBLEMENT DES INSTRUCTIONS DESASSEMBLEES                    */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : proc  = architecture à manipuler.                            *
*                state = nouvel état de l'accès aux instructions.             *
*                                                                             *
*  Description : Protège ou lève la protection de l'accès aux instructions.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_processor_lock_unlock(GArchProcessor *proc, bool state)
{
    if (state)
    {
        g_mutex_lock(&proc->mutex);
#ifndef NDEBUG
        g_atomic_int_set(&proc->locked, 1);
#endif
    }
    else
    {
#ifndef NDEBUG
        g_atomic_int_set(&proc->locked, 0);
#endif
        g_mutex_unlock(&proc->mutex);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture à consulter via la procédure.            *
*                                                                             *
*  Description : Fournit la marque de dernière modification des instructions. *
*                                                                             *
*  Retour      : Marque de la dernière modification de la liste d'instruct°.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unsigned int g_arch_processor_get_stamp(const GArchProcessor *proc)
{
    return proc->stamp;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture visée par la procédure.                  *
*                                                                             *
*  Description : Compte le nombre d'instructions représentées.                *
*                                                                             *
*  Retour      : Nombre d'instructions présentes.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_arch_processor_count_instructions(const GArchProcessor *proc)
{
    assert(g_atomic_int_get(&proc->locked) == 1);

    return proc->instr_count;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc  = architecture visée par la procédure.                 *
*                list  = liste des instructions désassemblées.                *
*                count = taille de cette liste.                               *
*                                                                             *
*  Description : Note les instructions désassemblées avec une architecture.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_processor_set_instructions(GArchProcessor *proc, GArchInstruction **list, size_t count)
{
    GArchInstruction *last;                 /* Dernière instruction traitée*/
    size_t i;                               /* Boucle de parcours          */
    GArchInstruction *instr;                /* Instruction à analyser      */

    g_arch_processor_lock(proc);

    proc->instructions = list;
    proc->instr_count = count;
    proc->stamp++;

    last = NULL;

    for (i = 0; i < count; i++)
    {
        instr = list[i];

        /* Constitution des groupes */

        if (last == NULL || g_arch_instruction_get_flags(instr) & AIF_ROUTINE_START)
        {
            if (last != NULL)
                g_arch_processor_finish_last_coverage(proc, last, i - 1);

            g_arch_processor_add_new_coverage(proc, instr, i);

        }

        last = instr;

    }

    if (last != NULL)
        g_arch_processor_finish_last_coverage(proc, last, proc->instr_count - 1);

    g_arch_processor_unlock(proc);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc  = architecture visée par la procédure.                 *
*                instr = instruction à ajouter à l'ensemble.                  *
*                                                                             *
*  Description : Ajoute une instruction désassemblée à la liste.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_processor_add_instruction(GArchProcessor *proc, GArchInstruction *instr)
{
    const mrange_t *range;                  /* Couverture de l'instruction */
    size_t ins_index;                       /* Indice de l'instruction     */
#ifndef NDEBUG
    bool found;                             /* Présence d'un élément       */
#endif
    instr_coverage *coverage;               /* Couverture fine impactée    */
    instr_coverage new;                     /* Nouveau groupe à insérer    */

    g_arch_processor_lock(proc);

    /**
     * Ajout de l'instruction.
     */

    int compare_instructions(const GArchInstruction **a, const GArchInstruction **b)
    {
        const mrange_t *range_a;            /* Couverture d'instruction A  */
        const mrange_t *range_b;            /* Couverture d'instruction B  */

        range_a = g_arch_instruction_get_range(*a);
        range_b = g_arch_instruction_get_range(*b);

        return cmp_mrange(range_a, range_b);

    }

#ifndef NDEBUG
    found = bsearch_index(&instr, proc->instructions, proc->instr_count,
                          sizeof(GArchInstruction *), (__compar_fn_t)compare_instructions, &ins_index);
    assert(!found);
#else
    bsearch_index(&instr, proc->instructions, proc->instr_count,
                  sizeof(GArchInstruction *), (__compar_fn_t)compare_instructions, &ins_index);
#endif

    proc->instructions = _qinsert(proc->instructions, &proc->instr_count,
                                  sizeof(GArchInstruction *), &instr, ins_index);

    /**
     * Actualisation des couvertures de code.
     */

    range = g_arch_instruction_get_range(instr);

    coverage = (instr_coverage *)g_arch_processor_find_coverage_by_address(proc, get_mrange_addr(range));

    if (coverage)
    {
        if (g_arch_instruction_get_flags(instr) & AIF_ROUTINE_START)
        {
            coverage = g_arch_processor_split_coverages(proc, coverage, instr, ins_index);

            if (coverage != NULL)
                g_arch_processor_update_coverages(proc, coverage, true);

        }

        else
            g_arch_processor_update_coverages(proc, coverage, true);

    }

    else
    {
        /**
         * Il n'existe pas de couverture pour l'instruction ajoutée.
         *
         * Donc on en crée une dédiée, et on l'insère au bon endroit.
         */

        copy_mrange(&new.range, range);

        new.start = ins_index;
        new.count = 1;


        int compare_coverages(const instr_coverage *a, const instr_coverage *b)
        {
            return cmp_mrange(&a->range, &b->range);
        }


        proc->coverages = qinsert(proc->coverages, &proc->cov_count,
                                  sizeof(instr_coverage), (__compar_fn_t)compare_coverages, &new);

    }

    proc->stamp++;

    g_arch_processor_unlock(proc);

    g_signal_emit_by_name(proc, "changed", instr, true);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc  = architecture visée par la procédure.                 *
*                instr = instruction à retirer de l'ensemble.                 *
*                                                                             *
*  Description : Retire une instruction désassemblée de la liste.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_processor_remove_instruction(GArchProcessor *proc, GArchInstruction *instr)
{
    bool emit;                              /* Ordre d'émission de signal  */
    const mrange_t *irange;                 /* Couverture de l'instruction */
    instr_coverage *coverage;               /* Couverture fine impactée    */
    VMPA_BUFFER(pos);                       /* Traduction de position      */
    size_t index;                           /* Indice de l'instruction     */
    bool status;                            /* Bilan d'une recherche       */

    emit = false;

    g_arch_instruction_delete_all_links(instr);

    irange = g_arch_instruction_get_range(instr);

    g_arch_processor_lock(proc);

    coverage = (instr_coverage *)g_arch_processor_find_coverage_by_address(proc, get_mrange_addr(irange));

    /**
     * L'instruction doit se trouve dans l'ensemble des instructions enregistrées.
     * Donc une couverture associée doit exister.
     */

    assert(coverage != NULL);

    if (coverage == NULL)
    {
        vmpa2_phys_to_string(get_mrange_addr(irange), MDS_UNDEFINED, pos, NULL);
        log_variadic_message(LMT_ERROR, _("Can not find coverage for instruction @ %s"), pos);
        goto done;
    }

    /**
     * Mises à jour des groupes d'instructions.
     */

    /* Si l'instruction est en début de couverture */
    if (cmp_vmpa(get_mrange_addr(&coverage->range), get_mrange_addr(irange)) == 0)
    {
        if (coverage == proc->coverages)
            copy_vmpa(get_mrange_addr(&coverage->range), get_mrange_addr(irange));

        else
        {
            assert(g_arch_instruction_get_flags(instr) & AIF_ROUTINE_START);

            g_arch_processor_merge_coverages(proc, coverage - 1, coverage);

            coverage = (instr_coverage *)g_arch_processor_find_coverage_by_address(proc, get_mrange_addr(irange));
            assert(coverage != NULL);

        }

    }

    set_mrange_length(&coverage->range, get_mrange_length(&coverage->range) - get_mrange_length(irange));

    g_arch_processor_update_coverages(proc, coverage, false);

    /**
     * Retrait effectif de l'instruction.
     */

    status = g_arch_processor_find_covered_index_by_address(proc, coverage, get_mrange_addr(irange), false, &index);

    assert(status);

    if (!status)
    {
        vmpa2_phys_to_string(get_mrange_addr(irange), MDS_UNDEFINED, pos, NULL);
        log_variadic_message(LMT_ERROR, _("Can not find instruction @ %s"), pos);
        goto done;
    }

    if ((index + 1) < proc->instr_count)
        memmove(&proc->instructions[index], &proc->instructions[index + 1],
                (proc->instr_count - index - 1) * sizeof(GArchInstruction *));

    proc->instr_count--;

    proc->instructions = (GArchInstruction **)realloc(proc->instructions,
                                                      proc->instr_count * sizeof(GArchInstruction *));

    proc->stamp++;

    emit = true;

 done:

    g_arch_processor_unlock(proc);

    if (emit)
        g_signal_emit_by_name(proc, "changed", instr, false);

    g_object_unref(G_OBJECT(instr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture visée par la procédure.                  *
*                index = indice de l'instruction visée.                       *
*                                                                             *
*  Description : Fournit une instruction désassemblée pour une architecture.  *
*                                                                             *
*  Retour      : Instructions désassemblée trouvée ou NULL si aucune.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_arch_processor_get_instruction(const GArchProcessor *proc, size_t index)
{
    GArchInstruction *result;               /* Instruction à retourner     */

    assert(g_atomic_int_get(&proc->locked) == 1);

    if (proc->instr_count == 0)
        result = NULL;

    else
    {
        assert(index < proc->instr_count);

        result = proc->instructions[index];
        assert(result != NULL);

        g_object_ref(G_OBJECT(result));

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                    CONSERVATION DES SOUCIS DURANT LE CHARGEMENT                    */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture à manipuler.                             *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_processor_finalize_errors(GArchProcessor *proc)
{
    size_t i;                               /* Boucle de parcours          */
    proc_error *error;                      /* Raccourci de confort        */

    if (proc->errors != NULL)
    {
        for (i = 0; i < proc->error_count; i++)
        {
            error = &proc->errors[i];

            if (error->desc != NULL)
                free(error->desc);

        }

        free(proc->errors);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc  = architecture à manipuler.                            *
*                state = nouvel état de l'accès aux erreurs relevées.         *
*                                                                             *
*  Description : Protège ou lève la protection de l'accès aux erreurs.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_processor_lock_unlock_errors(GArchProcessor *proc, bool state)
{
    if (state)
    {
        g_mutex_lock(&proc->error_mutex);
#ifndef NDEBUG
        g_atomic_int_set(&proc->error_locked, 1);
#endif
    }
    else
    {
#ifndef NDEBUG
        g_atomic_int_set(&proc->error_locked, 0);
#endif
        g_mutex_unlock(&proc->error_mutex);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc  = architecture concernée par la procédure.             *
*                index = indice du problème visé.                             *
*                type  = type d'erreur retrouvée.                             *
*                addr  = localisation associée.                               *
*                desc  = éventuelle description humaine de description.       *
*                                                                             *
*  Description : Etend la liste des soucis détectés avec de nouvelles infos.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_arch_processor_add_error(GArchProcessor *proc, ArchProcessingError type, const vmpa2t *addr, const char *desc)
{
    proc_error *error;                      /* Raccourci de confort        */

    g_arch_processor_lock_errors(proc);

    proc->errors = realloc(proc->errors, ++proc->error_count * sizeof(proc_error));

    error = &proc->errors[proc->error_count - 1];

    error->type = type;

    copy_vmpa(&error->addr, addr);

    if (desc != NULL)
        error->desc = strdup(desc);
    else
        error->desc = NULL;

    g_arch_processor_unlock_errors(proc);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture à consulter durant la procédure.         *
*                                                                             *
*  Description : Indique le nombre d'erreurs relevées au niveau assembleur.   *
*                                                                             *
*  Retour      : Nombre d'erreurs en stock.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_arch_processor_count_errors(GArchProcessor *proc)
{
    size_t result;                          /* Quantité à retourner        */

    assert(g_atomic_int_get(&proc->error_locked) == 1);

    result = proc->error_count;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc  = architecture concernée par la procédure.             *
*                index = indice du problème visé.                             *
*                type  = type d'erreur retrouvée. [OUT]                       *
*                addr  = localisation associée. [OUT]                         *
*                desc  = éventuelle description humaine de description. [OUT] *
*                                                                             *
*  Description : Fournit les éléments concernant un soucis détecté.           *
*                                                                             *
*  Retour      : Validité des informations renseignées.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_processor_get_error(GArchProcessor *proc, size_t index, ArchProcessingError *type, vmpa2t *addr, char **desc)
{
    bool result;                            /* Bilan à retourner           */
    proc_error *error;                      /* Raccourci de confort        */

    assert(g_atomic_int_get(&proc->error_locked) == 1);

    result = (index < proc->error_count);

    assert(result);

    if (result)
    {
        error = &proc->errors[index];

        *type = error->type;

        copy_vmpa(addr, &error->addr);

        if (error->desc != NULL)
            *desc = strdup(error->desc);
        else
            *desc = NULL;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture concernée par la procédure.              *
*                pbuf = zone tampon à vider.                                  *
*                                                                             *
*  Description : Charge les erreurs de chargement depuis une mémoire tampon.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_arch_processor_load_errors(GArchProcessor *proc, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */
    size_t i;                               /* Boucle de parcours          */
    proc_error *error;                      /* Raccourci de confort        */
    rle_string str;                         /* Chaîne à charger            */

    g_arch_processor_lock_errors(proc);

    result = unpack_uleb128(&value, pbuf);
    if (!result) goto exit;

    proc->error_count = value;

    proc->errors = calloc(proc->error_count, sizeof(proc_error));

    for (i = 0; i < proc->error_count && result; i++)
    {
        error = &proc->errors[i];

        result = unpack_uleb128(&value, pbuf);
        if (!result) break;

        error->type = value;

        result = unpack_vmpa(&error->addr, pbuf);
        if (!result) break;

        setup_empty_rle_string(&str);

        result = unpack_rle_string(&str, pbuf);
        if (!result) break;

        if (get_rle_string(&str) != NULL)
            error->desc = strdup(get_rle_string(&str));

        exit_rle_string(&str);

    }

 exit:

    g_arch_processor_unlock_errors(proc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture concernée par la procédure.              *
*                pbuf = zone tampon à remplir.                                *
*                                                                             *
*  Description : Sauvegarde les erreurs de chargement dans une mémoire tampon.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_arch_processor_store_errors(GArchProcessor *proc, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    proc_error *error;                      /* Raccourci de confort        */
    rle_string str;                         /* Chaîne à conserver          */

    g_arch_processor_lock_errors(proc);

    result = pack_uleb128((uleb128_t []){ proc->error_count }, pbuf);

    for (i = 0; i < proc->error_count && result; i++)
    {
        error = &proc->errors[i];

        result = pack_uleb128((uleb128_t []){ error->type }, pbuf);
        if (!result) break;

        result = pack_vmpa(&error->addr, pbuf);
        if (!result) break;

        init_static_rle_string(&str, error->desc);

        result = pack_rle_string(&str, pbuf);

        exit_rle_string(&str);

    }

    g_arch_processor_unlock_errors(proc);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                    MANIPULATIONS DES INSTRUCTIONS DESASSEMBLEES                    */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture à manipuler.                             *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_processor_finalize_coverages(GArchProcessor *proc)
{
    if (proc->coverages != NULL)
        free(proc->coverages);

}
/******************************************************************************
*                                                                             *
*  Paramètres  : proc  = architecture à comléter par la procédure.            *
*                first = première instruction d'un nouveau groupe.            *
*                start = indice de cette instruction dans l'ensemble global.  *
*                                                                             *
*  Description : Démarre la définition d'un nouveau groupe d'instructions.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_processor_add_new_coverage(GArchProcessor *proc, GArchInstruction *first, size_t start)
{
    instr_coverage *coverage;               /* Couverture à définir        */
    const mrange_t *irange;                 /* Couverture de l'instruction */

    assert(g_atomic_int_get(&proc->locked) == 1);

    /* Mise à disposition de d'avantage d'espace */
    if (proc->cov_allocated == proc->cov_count)
    {
        proc->cov_allocated += COV_ALLOC_BLOCK;

        proc->coverages = realloc(proc->coverages, proc->cov_allocated * sizeof(instr_coverage));

    }

    coverage = &proc->coverages[proc->cov_count++];

    irange = g_arch_instruction_get_range(first);

    init_mrange(&coverage->range, get_mrange_addr(irange), 0);

    coverage->start = start;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture à comléter par la procédure.             *
*                last = dernière instruction d'un nouveau groupe.             *
*                end  = indice de cette instruction dans l'ensemble global.   *
*                                                                             *
*  Description : Termine la définition d'un nouveau groupe d'instructions.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_processor_finish_last_coverage(GArchProcessor *proc, GArchInstruction *last, size_t end)
{
    instr_coverage *coverage;               /* Couverture à définir        */
    const mrange_t *irange;                 /* Couverture de l'instruction */
    phys_t diff;                            /* Ecart entre les extrémités  */

    assert(g_atomic_int_get(&proc->locked) == 1);

    coverage = &proc->coverages[proc->cov_count - 1];

    irange = g_arch_instruction_get_range(last);

    diff = compute_vmpa_diff(get_mrange_addr(&coverage->range), get_mrange_addr(irange));
    diff += get_mrange_length(irange);

    set_mrange_length(&coverage->range, diff);

    coverage->count = end - coverage->start + 1;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc      = architecture à modifier via la procédure.        *
*                coverage  = couverture comprenant l'instruction fournie.     *
*                instr     = point de coupure du groupe en question.          *
*                ins_index = indice de l'instruction dans la liste.           *
*                                                                             *
*  Description : Coupe un groupe d'instructions en deux.                      *
*                                                                             *
*  Retour      : Première couverture avec les indices décalés.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static instr_coverage *g_arch_processor_split_coverages(GArchProcessor *proc, instr_coverage *coverage, GArchInstruction *instr, size_t ins_index)
{
    instr_coverage *result;                 /* Groupe suivant à renvoyer   */
    const mrange_t *range;                  /* Emplacement de l'instruction*/
    size_t cov_index;                       /* Indice du groupe indiqué    */
    bool first;                             /* Première instruction ?      */
    size_t remaining;                       /* Qté d'instructions restantes*/
    vmpa2t end;                             /* Position finale d'un groupe */
    phys_t diff;                            /* Taille d'un groupe          */

    /* Tour de situation */

    range = g_arch_instruction_get_range(instr);

    cov_index = coverage - proc->coverages;

    first = (ins_index == coverage->start);

    /* Mise en place d'une zone supplémentaire */

    if (proc->cov_allocated == proc->cov_count)
    {
        proc->cov_allocated += COV_ALLOC_BLOCK;

        proc->coverages = (instr_coverage *)realloc(proc->coverages,
                                                    proc->cov_allocated * sizeof(instr_coverage));

    }

    assert(cov_index < proc->cov_count);

    memmove(&proc->coverages[cov_index + 1], &proc->coverages[cov_index],
            (proc->cov_count - cov_index) * sizeof(instr_coverage));

    proc->cov_count++;

    /* Actualisation des informations */

    if (first)
    {
        /* Première zone */

        coverage = &proc->coverages[cov_index];

        copy_mrange(&coverage->range, range);
        coverage->start = ins_index;
        coverage->count = 1;

        /* Seconde zone et zones suivantes */

        result = &proc->coverages[cov_index + 1];

    }

    else
    {
        /* Première zone */

        coverage = &proc->coverages[cov_index];

        remaining = coverage->count;

        compute_mrange_end_addr(&coverage->range, &end);

        diff = compute_vmpa_diff(get_mrange_addr(&coverage->range), get_mrange_addr(range));

        set_mrange_length(&coverage->range, diff);
        coverage->count = ins_index - coverage->start;

        assert(coverage->count > 0);

        remaining -= coverage->count;

        /* Seconde zone */

        coverage = &proc->coverages[cov_index + 1];

        diff = compute_vmpa_diff(get_mrange_addr(range), &end);

        init_mrange(&coverage->range, get_mrange_addr(range), diff);

        coverage->start = ins_index;
        coverage->count = 1 + remaining;

        /* Zones suivantes */

        if ((cov_index + 2) < proc->cov_count)
            result = &proc->coverages[cov_index + 2];
        else
            result = NULL;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture à modifier via la procédure.             *
*                a    = premier groupe d'instructions à traiter.              *
*                b    = second groupe d'instructions à traiter.               *
*                                                                             *
*  Description : Fusionne deux groupes d'instructions.                        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_processor_merge_coverages(GArchProcessor *proc, instr_coverage *a, instr_coverage *b)
{
    vmpa2t end;                             /* Limite de la couverture B   */
    phys_t diff;                            /* Ecart entre les extrémités  */
    size_t b_idx;                           /* Indice de la couverture B   */

    assert(g_atomic_int_get(&proc->locked) == 1);

    assert(a < b);

    compute_mrange_end_addr(&b->range, &end);

    diff = compute_vmpa_diff(get_mrange_addr(&a->range), &end);

    set_mrange_length(&a->range, diff);

    a->count += b->count;

    b_idx = (b - proc->coverages);

    assert(b_idx < proc->cov_count);

    if ((b_idx + 1) < proc->cov_count)
        memmove(b, b + 1, (proc->cov_count - b_idx - 1) * sizeof(instr_coverage));

    proc->cov_count--;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc  = architecture à modifier via la procédure.            *
*                first = premier groupe d'instructions à traiter.             *
*                add   = nature de la modification.                           *
*                                                                             *
*  Description : Met à jour une série de groupes d'instructions.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_arch_processor_update_coverages(GArchProcessor *proc, instr_coverage *first, bool add)
{
    size_t index;                           /* Indice de la couverture     */
    size_t i;                               /* Boucle de parcours          */

    assert(g_atomic_int_get(&proc->locked) == 1);

    index = first - proc->coverages;

    for (i = index; i < proc->cov_count; i++)
    {
        if (add)
            proc->coverages[i].count++;
        else
            proc->coverages[i].count--;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture concernée par la procédure.              *
*                pbuf = zone tampon à vider.                                  *
*                                                                             *
*  Description : Charge les plages de couvertures depuis une mémoire tampon.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_arch_processor_load_coverages(GArchProcessor *proc, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */
    size_t i;                               /* Boucle de parcours          */
    instr_coverage *coverage;               /* Raccourci de confort        */

    result = unpack_uleb128(&value, pbuf);
    if (!result) goto exit;

    proc->cov_allocated = value;
    proc->cov_count = value;

    proc->coverages = calloc(proc->cov_count, sizeof(instr_coverage));

    for (i = 0; i < proc->cov_count && result; i++)
    {
        coverage = &proc->coverages[i];

        result = unpack_mrange(&coverage->range, pbuf);
        if (!result) break;

        result = unpack_uleb128(&value, pbuf);
        if (!result) break;

        coverage->start = value;

        result = unpack_uleb128(&value, pbuf);
        if (!result) break;

        coverage->count = value;

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = architecture concernée par la procédure.              *
*                pbuf = zone tampon à remplir.                                *
*                                                                             *
*  Description : Sauvegarde les plages de couvertures dans une mémoire tampon.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_arch_processor_store_coverages(GArchProcessor *proc, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */
    instr_coverage *coverage;               /* Raccourci de confort        */

    result = pack_uleb128((uleb128_t []){ proc->cov_count }, pbuf);

    for (i = 0; i < proc->error_count && result; i++)
    {
        coverage = &proc->coverages[i];

        result = pack_mrange(&coverage->range, pbuf);
        if (!result) break;

        result = pack_uleb128((uleb128_t []){ coverage->start }, pbuf);
        if (!result) break;

        result = pack_uleb128((uleb128_t []){ coverage->count }, pbuf);
        if (!result) break;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc  = processeur recensant diverses instructions.          *
*                addr  = position en mémoire ou physique à chercher.          *
*                                                                             *
*  Description : Recherche un groupe d'instruction d'après son adresse.       *
*                                                                             *
*  Retour      : Couverture trouvée ou NULL si aucune.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const instr_coverage *g_arch_processor_find_coverage_by_address(const GArchProcessor *proc, const vmpa2t *addr)
{
    instr_coverage *result;                 /* Trouvaille à retourner      */
    void *ptr;                              /* Résultat des recherches     */

    //assert(g_atomic_int_get(&proc->locked) == 1);

    int search_for_coverage_by_addr(const vmpa2t *a, const instr_coverage *c)
    {
        int status;                         /* Bilan d'une comparaison     */

        status = cmp_mrange_with_vmpa(&c->range, a);

        return status;

    }

    ptr = bsearch(addr, proc->coverages, proc->cov_count,
                  sizeof(instr_coverage), (__compar_fn_t)search_for_coverage_by_addr);

    result = ((instr_coverage *)ptr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc     = processeur recensant diverses instructions.       *
*                coverage = zone de couverture fine à fouiller.               *
*                addr     = position en mémoire ou physique à chercher.       *
*                nearby   = la recherche s'effectue-t-elle de façon stricte ? *
*                index    = indice de l'instruction trouvée. [OUT]            *
*                                                                             *
*  Description : Recherche rapidement un indice d'instruction via une adresse.*
*                                                                             *
*  Retour      : Validité de l'indice fourni.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_arch_processor_find_covered_index_by_address(const GArchProcessor *proc, const instr_coverage *coverage, const vmpa2t *addr, bool nearby, size_t *index)
{
    bool result;                            /* Bilan à faire remonter      */
    void *ptr;                              /* Résultat des recherches     */
    __compar_fn_t fn;                       /* Fonction auxiliaire adaptée */

    //assert(g_atomic_int_get(&proc->locked) == 1);

    int search_for_instr_by_addr(const vmpa2t *a, const GArchInstruction **b)
    {
        const mrange_t *range_b;            /* Emplacement pour l'instr. B */

        range_b = g_arch_instruction_get_range(*b);

        return cmp_vmpa(a, get_mrange_addr(range_b));

    }

    int search_for_instr_by_nearby_addr(const vmpa2t *a, const GArchInstruction **b)
    {
        const mrange_t *range_b;            /* Emplacement pour l'instr. B */

        range_b = g_arch_instruction_get_range(*b);

        return cmp_mrange_with_vmpa(range_b, a);

    }

    if (nearby)
        fn = (__compar_fn_t)search_for_instr_by_nearby_addr;
    else
        fn = (__compar_fn_t)search_for_instr_by_addr;

    ptr = bsearch(addr, &proc->instructions[coverage->start], coverage->count,
                  sizeof(GArchInstruction *), fn);

    if (ptr == NULL)
        result = false;

    else
    {
        result = true;
        *index = ((GArchInstruction **)ptr) - proc->instructions;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc   = processeur recensant diverses instructions.         *
*                addr   = position en mémoire ou physique à chercher.         *
*                nearby = la recherche s'effectue-t-elle de façon stricte ?   *
*                                                                             *
*  Description : Recherche une instruction d'après son adresse.               *
*                                                                             *
*  Retour      : Instruction trouvée à l'adresse donnée, NULL si aucune.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *_g_arch_processor_find_instr_by_address(GArchProcessor *proc, const vmpa2t *addr, bool nearby)
{
    GArchInstruction *result;               /* Trouvaille à retourner      */
    const instr_coverage *coverage;         /* Couverture fine à fouiller  */

    g_arch_processor_lock(proc);

    coverage = g_arch_processor_find_coverage_by_address(proc, addr);

    if (coverage != NULL)
        result = _g_arch_processor_find_covered_instr_by_address(proc, coverage, addr, nearby);
    else
        result = NULL;

    g_arch_processor_unlock(proc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc     = processeur recensant diverses instructions.       *
*                coverage = zone de couverture fine à fouiller.               *
*                addr     = position en mémoire ou physique à chercher.       *
*                nearby   = la recherche s'effectue-t-elle de façon stricte ? *
*                                                                             *
*  Description : Recherche rapidement une instruction d'après son adresse.    *
*                                                                             *
*  Retour      : Instruction trouvée à l'adresse donnée, NULL si aucune.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *_g_arch_processor_find_covered_instr_by_address(const GArchProcessor *proc, const instr_coverage *coverage, const vmpa2t *addr, bool nearby)
{
    GArchInstruction *result;               /* Trouvaille à retourner      */
    size_t index;                           /* Indice d'instruction visée  */
    bool valid;                             /* Validité de l'indice        */

    valid = g_arch_processor_find_covered_index_by_address(proc, coverage, addr, nearby, &index);

    if (valid)
        result = g_arch_processor_get_instruction(proc, index);
    else
        result = NULL;

    return result;

}

 
/******************************************************************************
*                                                                             *
*  Paramètres  : proc   = processeur recensant diverses instructions.         *
*                addr   = position en mémoire ou physique à chercher.         *
*                nearby = la recherche s'effectue-t-elle de façon stricte ?   *
*                                                                             *
*  Description : Met en place un itérateur d'instruction selon une adresse.   *
*                                                                             *
*  Retour      : Itérateur mis en place, ou NULL si l'opération est un échec. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

instr_iter_t *_g_arch_processor_get_iter_from_address(GArchProcessor *proc, const vmpa2t *addr, bool nearby)
{
    instr_iter_t *result;                   /* Itérateur à retourner       */
    const instr_coverage *coverage;         /* Couverture fine à fouiller  */

    g_arch_processor_lock(proc);

    coverage = g_arch_processor_find_coverage_by_address(proc, addr);

    if (coverage != NULL)
        result = _g_arch_processor_get_covered_iter_from_address(proc, coverage, addr, nearby);
    else
        result = NULL;

    g_arch_processor_unlock(proc);

    return result;

}

 
/******************************************************************************
*                                                                             *
*  Paramètres  : proc     = processeur recensant diverses instructions.       *
*                coverage = zone de couverture fine à fouiller.               *
*                addr     = position en mémoire ou physique à chercher.       *
*                nearby   = la recherche s'effectue-t-elle de façon stricte ? *
*                                                                             *
*  Description : Met en place un itérateur d'instruction selon une adresse.   *
*                                                                             *
*  Retour      : Itérateur mis en place, ou NULL si l'opération est un échec. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

instr_iter_t *_g_arch_processor_get_covered_iter_from_address(GArchProcessor *proc, const instr_coverage *coverage, const vmpa2t *addr, bool nearby)
{
    instr_iter_t *result;                   /* Itérateur à retourner       */
    size_t index;                           /* Indice d'instruction visée  */
    bool valid;                             /* Validité de l'indice        */

    valid = g_arch_processor_find_covered_index_by_address(proc, coverage, addr, nearby, &index);

    if (valid)
        result = create_instruction_iterator(proc, index);
    else
        result = NULL;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                      CONSERVATION ET RECHARGEMENT DES DONNEES                      */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : proc    = élément GLib à constuire.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à lire.                                *
*                                                                             *
*  Description : Charge un contenu depuis une mémoire tampon.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_arch_processor_load(GArchProcessor *proc, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */

    result = unpack_uleb128(&value, pbuf);
    if (!result) goto exit;

    proc->endianness = value;






    if (result)
        result = g_arch_processor_load_errors(proc, pbuf);

    if (result)
        result = g_arch_processor_load_coverages(proc, pbuf);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc    = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde un contenu dans une mémoire tampon.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_arch_processor_store(GArchProcessor *proc, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = pack_uleb128((uleb128_t []){ proc->endianness }, pbuf);





    if (result)
        result = g_arch_processor_store_coverages(proc, pbuf);

    if (result)
        result = g_arch_processor_store_errors(proc, pbuf);

    return result;

}
