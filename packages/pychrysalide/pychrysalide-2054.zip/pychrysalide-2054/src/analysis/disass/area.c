
/* Chrysalide - Outil d'analyse de fichiers binaires
 * area.c - définition et manipulation des aires à désassembler
 *
 * Copyright (C) 2014-2019 Cyrille Bagard
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


#include "area.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include <i18n.h>


#include "../routine.h"
#include "../contents/restricted.h"
#include "../../arch/instructions/raw.h"
#include "../../common/bits.h"
#include "../../common/sort.h"
#include "../../core/global.h"
#include "../../core/logs.h"
#include "../../core/nproc.h"
#include "../../format/known.h"
#include "../../format/format.h"
#include "../../glibext/delayed-int.h"



/* ------------------------- TRAITEMENT DES ZONES DE DONNES ------------------------- */


/* Zone mémoire bien bornée */
typedef struct _mem_area
{
    GBinFormat *format;                     /* Format du fichier binaire   */
    GBinContent *content;                   /* Données binaires à lire     */
    GArchProcessor *proc;                   /* Architecture du binaire     */
    SourceEndian endianness;                /* Boutisme de cette machine   */

    mrange_t range;                         /* Couverture de la zone       */

    phys_t packing_size;                    /* Granularité des découpages  */

    bitfield_t *processed;                  /* Octets traités dans la zone */
    GArchInstruction **instructions;        /* Instructions en place       */
    size_t count;                           /* Quantité d'instructions     */
    GMutex mutex;                           /* Garantie d'atomicité        */
    GMutex *global;                         /* Atomicité sur zones multi.  */

    bool is_exec;                           /* Zone exécutable ?           */

} mem_area;


/* Initialise une aire de données à partir d'une adresse donnée. */
static void init_mem_area_from_addr(mem_area *, const vmpa2t *, phys_t, const GLoadedBinary *, GMutex *);

/* Libère d'une aire de données les ressources allouées. */
static void fini_mem_area(mem_area *);

/* Indique si une zone donnée est intégralement vierge. */
static bool _is_range_empty_in_mem_area(mem_area *, phys_t, phys_t);

/* Indique si une zone donnée est intégralement vierge. */
static bool is_range_empty_in_mem_area(mem_area *, phys_t, phys_t);

/* Indique si une zone donnée est intégralement occupée. */
static bool is_range_busy_in_mem_area(mem_area *, phys_t, phys_t);

/* Marque une série d'octets comme ayant été traités. */
static void mark_range_in_mem_area_as_processed(mem_area *area, GArchInstruction *, phys_t, phys_t);

/* Marque une série d'octets comme non traités. */
static void unmark_range_in_mem_area_as_processed(mem_area *, phys_t, phys_t);

/* Crée une instruction issue d'un désassemblage brut. */
static GArchInstruction *load_raw_instruction_from_mem_area(mem_area *, phys_t, vmpa2t *, phys_t *);

/* S'assure de la présence d'un début de routine à un point. */
static void update_address_as_routine(GBinFormat *, const vmpa2t *);

/* Procède au désassemblage d'un contenu binaire non exécutable. */
static void load_data_from_mem_area(mem_area *, const vmpa2t *, GtkStatusStack *, activity_id_t);

/* S'assure qu'une aire contient toutes ses instructions. */
static void fill_mem_area_with_code(mem_area *, mem_area *, size_t, GProcContext *, GtkStatusStack *, activity_id_t);

/* S'assure qu'une aire contient toutes ses instructions. */
static void fill_mem_area_with_data(mem_area *, mem_area *, size_t, GtkStatusStack *, activity_id_t);

/* Rassemble les instructions conservées dans une zone donnée. */
static GArchInstruction **get_instructions_from_mem_area(const mem_area *, GArchInstruction **, size_t *);



/* -------------------------- TRAITEMENT DE ZONES PAR LOTS -------------------------- */


/* Insère une instruction dans un ensemble d'aires. */
static bool insert_instr_into_mem_areas(mem_area *, size_t, GArchInstruction *, mem_area **);

/* Force l'insertion d'une instruction dans un ensemble d'aires. */
static void insert_instr_into_mem_areas_forced(mem_area *, size_t, GArchInstruction *);



/* ----------------------- MANIPULATIONS PARALLELES DES ZONES ----------------------- */


#define G_TYPE_AREA_COLLECTOR            g_area_collector_get_type()
#define G_AREA_COLLECTOR(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_AREA_COLLECTOR, GAreaCollector))
#define G_IS_AREA_COLLECTOR(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_AREA_COLLECTOR))
#define G_AREA_COLLECTOR_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_AREA_COLLECTOR, GAreaCollectorClass))
#define G_IS_AREA_COLLECTOR_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_AREA_COLLECTOR))
#define G_AREA_COLLECTOR_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_AREA_COLLECTOR, GAreaCollectorClass))


/* Ensembles binaires à désassembler (instance) */
typedef struct _GAreaCollector
{
    GDelayedWork parent;                    /* A laisser en premier        */

    activity_id_t id;                       /* Groupe de progression       */
    run_task_fc run;                        /* Activité dans la pratique   */

    mem_area *areas;                        /* Zone de productions         */

    union
    {
        struct
        {
            size_t created;                 /* Nombre de zones créées      */

            GLoadedBinary *binary;          /* Binaire à associer aux zones*/
            GMutex *global;                 /* Verrou pour zones multi.    */

            phys_t first;                   /* Début de traitement         */
            phys_t last;                    /* Fin de traitement           */

            bool closing;                   /* Tâche clôturant le parcours */

        };

        struct
        {
            size_t available;               /* Nombre de zones créées      */

            GPreloadInfo *info;             /* Préchargements à intégrer   */

            size_t start;                   /* Départ des intégrations     */
            size_t stop;                    /* Fin des intégrations        */

        };

        struct
        {
            size_t count;                   /* Nombre de zones présentes   */

            GProcContext *ctx;              /* Contexte de désassemblage   */

            size_t fill_start;              /* Première zone à remplir     */
            size_t fill_stop;               /* Première zone à écarter     */

        };

        struct
        {
            size_t begin;                   /* Début du parcours à mener   */
            size_t end;                     /* Fin de ce même parcours     */

            GArchInstruction **collected;   /* Instructions collectées     */
            size_t ccount;                  /* Quantité de ces instructions*/

        };

    };

} GAreaCollector;

/* Ensembles binaires à désassembler (classe) */
typedef struct _GAreaCollectorClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

} GAreaCollectorClass;


/* Indique le type défini pour les tâches de traitement des zones. */
GType g_area_collector_get_type(void);

/* Initialise la classe des manipulations parallèles de zones. */
static void g_area_collector_class_init(GAreaCollectorClass *);

/* Initialise des manipulations parallèles de zones. */
static void g_area_collector_init(GAreaCollector *);

/* Supprime toutes les références externes. */
static void g_area_collector_dispose(GAreaCollector *);

/* Procède à la libération totale de la mémoire. */
static void g_area_collector_finalize(GAreaCollector *);

/* Assure un traitement particulier concernant les zones. */
static void g_area_collector_process(GAreaCollector *, GtkStatusStack *);

/* Crée une tâche de calcul des zones binaires à désassembler. */
static GAreaCollector *g_area_collector_new_intro(activity_id_t, GLoadedBinary *, GMutex *, phys_t, phys_t, bool);

/* Construit une liste bornée de zones contigües. */
static void g_area_collector_do_compute(GAreaCollector *, GtkStatusStack *);

/* Crée une tâche de calcul des zones binaires à remplir. */
static GAreaCollector *g_area_collector_new_insert(activity_id_t, mem_area *, size_t, GPreloadInfo *, size_t, size_t);

/* Insère dans les zones contigües les instructions préchargées. */
static void g_area_collector_do_insert(GAreaCollector *, GtkStatusStack *);

/* Crée une tâche de fin de désassemblage pour zones binaires. */
static GAreaCollector *g_area_collector_new_filling(activity_id_t, mem_area *, size_t, GProcContext *, size_t, size_t);

/* Remplit de code ou de données une série de zones. */
static void g_area_collector_do_fill(GAreaCollector *, GtkStatusStack *);

/* Crée une tâche de récupération d'instructions différée. */
static GAreaCollector *g_area_collector_new_outro(activity_id_t, mem_area *, size_t, size_t);

/* Assure la récupération d'instructions en différé. */
static void g_area_collector_do_collect(GAreaCollector *, GtkStatusStack *);



/* ---------------------------------------------------------------------------------- */
/*                            RAITEMENT DES ZONES DE DONNES                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : area   = aire représentant à contenu à initialiser.          *
*                addr   = adresse de départ de l'espace à mettre en place.    *
*                len    = longueur de l'espace à créer.                       *
*                binary = binaire analysé content quantités d'informations.   *
*                global = verrou pour les accès sur plusieurs zones.          *
*                                                                             *
*  Description : Initialise une aire de données à partir d'une adresse donnée.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void init_mem_area_from_addr(mem_area *area, const vmpa2t *addr, phys_t len, const GLoadedBinary *binary, GMutex *global)
{
    GBinContent *content;                   /* Données binaires à lire     */

    assert(len > 0);

    area->format = G_BIN_FORMAT(g_loaded_binary_get_format(binary));

    area->proc = g_loaded_binary_get_processor(binary);
    area->endianness = g_arch_processor_get_endianness(area->proc);

    init_mrange(&area->range, addr, len);

    content = g_known_format_get_content(G_KNOWN_FORMAT(area->format));

    area->content = g_restricted_content_new(content, &area->range);

    g_object_unref(G_OBJECT(content));

    switch (g_arch_processor_get_instruction_min_size(area->proc))
    {
        case MDS_4_BITS:
        case MDS_8_BITS:
            area->packing_size = 1;
            break;

        case MDS_16_BITS:
            area->packing_size = 2;
            break;

        case MDS_32_BITS:
            area->packing_size = 4;
            break;

        case MDS_64_BITS:
            area->packing_size = 8;
            break;

        default:
            assert(false);
            area->packing_size = 1;
            break;

    }

    area->processed = create_bit_field(len, false);
    area->instructions = (GArchInstruction **)calloc(len, sizeof(GArchInstruction *));
    area->count = 0;
    g_mutex_init(&area->mutex);

    area->global = global;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : area = aire représentant à contenu à nettoyer en mémoire.    *
*                                                                             *
*  Description : Libère d'une aire de données les ressources allouées.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void fini_mem_area(mem_area *area)
{
    phys_t len;                             /* Etendue du parcours total   */
    phys_t i;                               /* Boucle de parcours          */

    g_object_unref(area->format);
    g_object_unref(area->content);
    g_object_unref(area->proc);

    delete_bit_field(area->processed);

    len = get_mrange_length(&area->range);

    for (i = 0; i < len; i++)
        g_clear_object(&area->instructions[i]);

    free(area->instructions);

    g_mutex_clear(&area->mutex);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : area  = aire représentant à contenu à parcourir.             *
*                start = début de la zone à manipuler.                        *
*                len   = taille de cette même aire de données.                *
*                                                                             *
*  Description : Indique si une zone donnée est intégralement vierge.         *
*                                                                             *
*  Retour      : true si l'aire visée n'a jamais été traitée, false sinon.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _is_range_empty_in_mem_area(mem_area *area, phys_t start, phys_t len)
{
    bool result;                            /* Résultat à renvoyer         */

    assert(!g_mutex_trylock(&area->mutex));

    assert((start + len) <= get_mrange_length(&area->range));

    result = test_none_in_bit_field(area->processed, start, len);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : area  = aire représentant à contenu à parcourir.             *
*                start = début de la zone à manipuler.                        *
*                len   = taille de cette même aire de données.                *
*                                                                             *
*  Description : Indique si une zone donnée est intégralement vierge.         *
*                                                                             *
*  Retour      : true si l'aire visée n'a jamais été traitée, false sinon.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_range_empty_in_mem_area(mem_area *area, phys_t start, phys_t len)
{
    bool result;                            /* Résultat à renvoyer         */

    /**
     * Les accès au champ de bits sont atomiques, mais la fonction
     * (un)mark_range_in_mem_area_as_processed() peut y accéder en deux temps
     * (réinitialisation, puis définition).
     *
     * On protège donc les accès de façon constante.
     */

    g_mutex_lock(&area->mutex);

    result = _is_range_empty_in_mem_area(area, start, len);

    g_mutex_unlock(&area->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : area  = aire représentant à contenu à parcourir.             *
*                start = début de la zone à manipuler.                        *
*                len   = taille de cette même aire de données.                *
*                                                                             *
*  Description : Indique si une zone donnée est intégralement vierge ou non.  *
*                                                                             *
*  Retour      : true si l'aire visée n'a jamais été traitée, false sinon.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool is_range_busy_in_mem_area(mem_area *area, phys_t start, phys_t len)
{
    bool result;                            /* Résultat à renvoyer         */

    assert((start + len) <= get_mrange_length(&area->range));

    /**
     * Les accès au champ de bits sont atomiques, mais la fonction
     * (un)mark_range_in_mem_area_as_processed() peut y accéder en deux temps
     * (réinitialisation, puis définition).
     *
     * On protège donc les accès de façon constante.
     */

    g_mutex_lock(&area->mutex);

    result = test_all_in_bit_field(area->processed, start, len);

    g_mutex_unlock(&area->mutex);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : area  = aire représentant à contenu à parcourir.             *
*                instr = instruction à mémoriser pour la suite ou NULL.       *
*                start = début de la zone à manipuler.                        *
*                len   = taille de cette même aire de données.                *
*                                                                             *
*  Description : Marque une série d'octets comme ayant été traités.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void mark_range_in_mem_area_as_processed(mem_area *area, GArchInstruction *instr, phys_t start, phys_t len)
{
#ifndef NDEBUG
    bool status;                            /* Validation de disponibilité */
    phys_t i;                               /* Boucle de parcours          */
#endif

    assert(!g_mutex_trylock(&area->mutex));

    assert((start + len) <= get_mrange_length(&area->range));

    assert(instr != NULL || start == 0);

    /* Application dans le registre des bits */

#ifndef NDEBUG

    status = test_none_in_bit_field(area->processed, start, len);

    assert(status);

#endif

    set_in_bit_field(area->processed, start, len);

    /* Inscription de l'instruction dans les comptes */

#ifndef NDEBUG

    for (i = 0; i < len; i++)
        assert(area->instructions[start + i] == NULL);

#endif

    if (instr != NULL)
    {
        area->instructions[start] = instr;
        g_object_ref(G_OBJECT(instr));

        g_atomic_pointer_add(&area->count, 1);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : area  = aire représentant à contenu à parcourir.             *
*                instr = instruction à mémoriser pour la suite ou NULL.       *
*                start = début de la zone à manipuler.                        *
*                len   = taille de cette même aire de données.                *
*                                                                             *
*  Description : Marque une série d'octets comme non traités.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void unmark_range_in_mem_area_as_processed(mem_area *area, phys_t start, phys_t len)
{
    phys_t i;                               /* Boucle de parcours          */
    GArchInstruction *old;                  /* Instruction remplacée       */

    assert(!g_mutex_trylock(&area->mutex));

    assert((start + len) <= get_mrange_length(&area->range));

    /* Retrait d'éventuelles instructions */

    for (i = 0; i < len; i++)
    {
        old = area->instructions[start + i];

        if (old != NULL)
        {
            g_object_unref(G_OBJECT(old));
            area->instructions[start + i] = NULL;

            g_atomic_pointer_add(&area->count, -1);

        }

    }

    /* Actualisation du registre des bits */

    reset_in_bit_field(area->processed, start, len);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : area   = aire représentant à contenu à parcourir.            *
*                offset = point de départ au sein de l'aire en question.      *
*                pos    = tête de lecture dans l'espace global.               *
*                size   = taille de l'instruction mise en place. [OUT]        *
*                                                                             *
*  Description : Crée une instruction issue d'un désassemblage brut.          *
*                                                                             *
*  Retour      : Instruction mise en place ou NULL en cas d'échec.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction *load_raw_instruction_from_mem_area(mem_area *area, phys_t offset, vmpa2t *pos, phys_t *size)
{
    GArchInstruction *result;               /* Instruction à retourner     */
    GBinContent *content;                   /* Données binaires à lire     */
    SourceEndian endianness;                /* Boutisme de cette machine   */
    phys_t sz;                              /* Volume de données traité    */
    vmpa2t prev;                            /* Boucle de parcours          */

    result = NULL;

    content = area->content;
    endianness = area->endianness;

    sz = area->packing_size;

    /**
     * Une vérification est effectuée en amont pour garantir qu'il existe
     * toujours au moins un octet à traiter.
     *
     * Si on veut en manipuler plus d'un, aucune vérification en amont ne s'occupe
     * du cas où on dépasse les limites de la zone lors des tests de marquage.
     *
     * D'habitude, c'est la création préalable d'une instruction, via la lecture
     * du contenu binaire restreint, qui part en échec et qui fait qu'on ne teste
     * pas la zone sur un espace hors champ.
     *
     * Ce test est effectué avant la création d'une instruction ici (et c'est le
     * seul endroit dans ce cas de figure), donc il faut faire les vérifications
     * de débordement avant tout !
     */

    if (get_virt_addr(pos) % sz == 0
        && (offset + sz) <= get_mrange_length(&area->range)
        && is_range_empty_in_mem_area(area, offset, sz))
    {
        *size = sz;

        copy_vmpa(&prev, pos);

        result = g_raw_instruction_new_array(content, MDS_FROM_BYTES(sz), 1, pos, endianness);

        if (result == NULL)
            copy_vmpa(pos, &prev);

    }

    if (result == NULL)
    {
        *size = 1;

        result = g_raw_instruction_new_array(content, MDS_8_BITS, 1, pos, endianness);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format binaire en cours de traitement.              *
*                addr   = adresse d'une instruction présentée comme première. *
*                                                                             *
*  Description : S'assure de la présence d'un début de routine à un point.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void update_address_as_routine(GBinFormat *format, const vmpa2t *addr)
{
    GBinSymbol *symbol;                     /* Symbole présent ou créé     */
    bool found;                             /* Détection de symbole        */
    SymbolType sym_type;                    /* Type de symbole en place    */
    bool wrong_type;                        /* Analyse plus fine de ce type*/
    mrange_t range;                         /* Etendue du symbole à créer  */
    VMPA_BUFFER(loc);                       /* Traduction de l'adresse     */
    char name[5 + VMPA_MAX_LEN];            /* Nom de symbole nouveau      */
    GBinRoutine *routine;                   /* Nouvelle routine trouvée    */

    found = g_binary_format_find_symbol_at(format, addr, &symbol);

    if (found)
    {
        sym_type = g_binary_symbol_get_stype(symbol);
        wrong_type = (sym_type != STP_ROUTINE && sym_type != STP_ENTRY_POINT);
    }

    if (!found || (found && wrong_type))
    {
        if (found)
        {
            g_binary_format_remove_symbol(format, symbol);
            g_object_unref(G_OBJECT(symbol));
        }

        init_mrange(&range, addr, 0);

        vmpa2_virt_to_string(addr, MDS_UNDEFINED, loc, NULL);
        snprintf(name, sizeof(name), "sub_%s", loc + 2);

        routine = g_binary_routine_new();
        symbol = G_BIN_SYMBOL(routine);

        g_binary_routine_set_name(routine, strdup(name));
        g_binary_symbol_set_range(symbol, &range);

        g_binary_format_add_symbol(format, symbol);

    }

    else
        g_object_unref(G_OBJECT(symbol));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : area   = aire représentant à contenu à parcourir.            *
*                list   = liste de zones délimitant des contenus à traiter.   *
*                count  = nombre de zones à disposition.                      *
*                index  = indice de l'aire à considérer pendant l'opération.  *
*                binary = représentation de binaire chargé.                   *
*                ctx    = contexte offert en soutien à un désassemblage.      *
*                start  = démarrage de l'exécution au sein de la zone.        *
*                force  = force la création d'au moins une instruction.       *
*                status = barre de statut à actualiser.                       *
*                id     = identifiant du groupe de progression à l'affichage. *
*                                                                             *
*  Description : Procède au désassemblage d'un contenu binaire exécutable.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void load_code_from_mem_area(mem_area *area, mem_area *list, size_t count, GProcContext *ctx, const vmpa2t *start, bool force, GtkStatusStack *status, activity_id_t id)
{
    GBinFormat *format;                     /* Format du fichier binaire   */
    GArchProcessor *proc;                   /* Architecture du binaire     */
    GBinContent *content;                   /* Données binaires à lire     */
    phys_t init_diff;                       /* Position initiale de lecture*/
    phys_t alen;                            /* Taille de l'aire utilisée   */
    vmpa2t pos;                             /* Tête de lecture             */
    bool forced_once;                       /* Préfigure une sortie rapide */
    phys_t i;                               /* Boucle de parcours          */
    vmpa2t prev;                            /* Sauvegarde de la tête       */
    GArchInstruction *instr;                /* Instruction décodée         */
    phys_t diff;                            /* Volume de données traité    */
    mrange_t range;                         /* Couverture de l'instruction */
    bool done;                              /* Enregistrement effectué ?   */
    GArchInstruction *extra;                /* Instruction supplémentaire  */

    /* Récupération des informations de base */

    format = area->format;
    proc = area->proc;
    content = area->content;

    init_diff = compute_vmpa_diff(get_mrange_addr(&area->range), start);
    alen = get_mrange_length(&area->range);

    copy_vmpa(&pos, start);

    /* Traitement de la zone */

    forced_once = false;

    for (i = init_diff; i < alen; i += diff)
    {
        /**
         * On réalise un premier test informel (car non atomique) peu coûteux
         * avant de se lancer dans un désassemblage d'instruction potentiellement
         * inutile.
         */

        if (is_range_busy_in_mem_area(area, i, 1))
            break;

        /* Décodage d'une nouvelle instruction */

        copy_vmpa(&prev, &pos);

        instr = g_arch_processor_disassemble(proc, ctx, content, &pos, G_EXE_FORMAT(format));

        if (instr != NULL)
            diff = compute_vmpa_diff(&prev, &pos);

        else
        {
            if (i == init_diff && force)
            {
                instr = load_raw_instruction_from_mem_area(area, i, &pos, &diff);
                forced_once = true;
            }

            if (instr == NULL)
                break;

        }

        /* Enregistrement des positions et adresses */

        init_mrange(&range, &prev, diff);

        g_arch_instruction_set_range(instr, &range);

        /* Progression dans les traitements */

        done = insert_instr_into_mem_areas(list, count, instr, (mem_area *[]) { area });

        if (!done)
        {
            g_object_unref(G_OBJECT(instr));
            break;
        }

        gtk_status_stack_update_activity_value(status, id, diff);

        /* Enregistrement d'un éventuel début de routine */

        if (g_arch_instruction_get_flags(instr) & AIF_ROUTINE_START)
            update_address_as_routine(format, &prev);

        /* Eventuel renvoi vers d'autres adresses */

        g_arch_instruction_call_hook(instr, IPH_FETCH, proc, ctx, G_EXE_FORMAT(format));

        /* Insertion des symboles découverts en parallèle */

        for (extra = g_preload_info_pop_instruction(G_PRELOAD_INFO(ctx));
             extra != NULL;
             extra = g_preload_info_pop_instruction(G_PRELOAD_INFO(ctx)))
        {
            insert_instr_into_mem_areas_forced(list, count, extra);
            g_object_unref(G_OBJECT(extra));
        }

        /* Rupture du flot d'exécution ? */
        if (forced_once || g_arch_instruction_get_flags(instr) & AIF_RETURN_POINT)
        {
            g_object_unref(G_OBJECT(instr));
            break;
        }
        else
            g_object_unref(G_OBJECT(instr));

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : area   = aire représentant à contenu à parcourir.            *
*                start  = démarrage de l'exécution au sein de la zone.        *
*                status = barre de statut à actualiser.                       *
*                id     = identifiant du groupe de progression à l'affichage. *
*                                                                             *
*  Description : Procède au désassemblage d'un contenu binaire non exécutable.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void load_data_from_mem_area(mem_area *area, const vmpa2t *start, GtkStatusStack *status, activity_id_t id)
{
    phys_t diff;                            /* Volume de données traité    */
    phys_t alen;                            /* Taille de l'aire utilisée   */
    vmpa2t pos;                             /* Boucle de parcours          */
    phys_t i;                               /* Boucle de parcours          */
    vmpa2t prev;                            /* Boucle de parcours          */
    GArchInstruction *instr;                /* Instruction décodée         */
    mrange_t range;                         /* Couverture de l'instruction */
    bool done;                              /* Enregistrement effectué ?   */

    /* Récupération des informations de base */

    diff = compute_vmpa_diff(get_mrange_addr(&area->range), start);
    alen = get_mrange_length(&area->range);

    copy_vmpa(&pos, start);

    /* Traitement de la zone */

    for (i = diff; i < alen; i += diff)
    {
        /* On cherche à obtenir l'assurance que le traitement n'a jamais été fait */

        if (is_range_busy_in_mem_area(area, i, 1))
            break;

        /* Décodage d'une nouvelle instruction, sur mesure puis minimale */

        copy_vmpa(&prev, &pos);

        instr = load_raw_instruction_from_mem_area(area, i, &pos, &diff);

        /* On rencontre ici un morceau déjà traité. */

        if (instr == NULL) break;

        /* Enregistrement des positions et adresses */

        assert(diff == compute_vmpa_diff(&prev, &pos));

        init_mrange(&range, &prev, diff);

        g_arch_instruction_set_range(instr, &range);

        /* Progression dans les traitements */

        done = insert_instr_into_mem_areas(area, 1, instr, (mem_area *[]) { area });

        g_object_unref(G_OBJECT(instr));

        if (!done)
            break;

        gtk_status_stack_update_activity_value(status, id, diff);

        /* On laisse une chance au code pour se reprendre... */

        if (area->is_exec) break;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : area   = aire représentant à contenu à parcourir.            *
*                list   = liste de zones délimitant des contenus à traiter.   *
*                count  = nombre de zones à disposition.                      *
*                binary = représentation de binaire chargé.                   *
*                ctx    = contexte offert en soutien à un désassemblage.      *
*                status = barre de statut à actualiser.                       *
*                id     = identifiant du groupe de progression à l'affichage. *
*                                                                             *
*  Description : S'assure qu'une aire contient toutes ses instructions.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void fill_mem_area_with_code(mem_area *area, mem_area *list, size_t count, GProcContext *ctx, GtkStatusStack *status, activity_id_t id)
{
    const vmpa2t *addr;                     /* Début de la zone à traiter  */
    phys_t len;                             /* Taille de la zone à remplir */
    phys_t i;                               /* Boucle de parcours          */
    vmpa2t start;                           /* Adresse de départ de combles*/

    if (area->is_exec)
    {
        addr = get_mrange_addr(&area->range);
        len = get_mrange_length(&area->range);

        for (i = 0; i < len; i++)
        {
            if (is_range_empty_in_mem_area(area, i, 1))
            {
                copy_vmpa(&start, addr);
                advance_vmpa(&start, i);

                if (get_virt_addr(&start) % area->packing_size == 0)
                    load_code_from_mem_area(area, list, count, ctx, &start, false, status, id);

            }

        }

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : area   = aire représentant à contenu à parcourir.            *
*                list   = liste de zones délimitant des contenus à traiter.   *
*                count  = nombre de zones à disposition.                      *
*                status = barre de statut à actualiser.                       *
*                id     = identifiant du groupe de progression à l'affichage. *
*                                                                             *
*  Description : S'assure qu'une aire contient toutes ses instructions.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void fill_mem_area_with_data(mem_area *area, mem_area *list, size_t count, GtkStatusStack *status, activity_id_t id)
{
    const vmpa2t *addr;                     /* Début de la zone à traiter  */
    phys_t len;                             /* Taille de la zone à remplir */
    bool err_trigger;                       /* Présence d'une instruction  */
    phys_t i;                               /* Boucle de parcours          */
    vmpa2t start;                           /* Adresse de départ de combles*/

    addr = get_mrange_addr(&area->range);
    len = get_mrange_length(&area->range);

    err_trigger = true;

    for (i = 0; i < len; i++)
    {
        if (is_range_empty_in_mem_area(area, i, 1))
        {
            copy_vmpa(&start, addr);
            advance_vmpa(&start, i);

            if (area->is_exec && err_trigger)
            {
                g_arch_processor_add_error(area->proc, APE_DISASSEMBLY, &start,
                                           _("Unable to disassemble code instruction"));

                err_trigger = false;

            }

            load_data_from_mem_area(area, &start, status, id);

        }

        else
            err_trigger = true;

        assert(is_range_busy_in_mem_area(area, i, 1));

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : area  = aire représentant à contenu à parcourir.             *
*                list  = liste d'instructions à compléter.                    *
*                count = taille de cette liste. [OUT]                         *
*                                                                             *
*  Description : Rassemble les instructions conservées dans une zone donnée.  *
*                                                                             *
*  Retour      : Liste d'instructions prêtes à emploi.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchInstruction **get_instructions_from_mem_area(const mem_area *area, GArchInstruction **list, size_t *count)
{
    GArchInstruction **result;              /* Liste d'instr. à renvoyer   */
    phys_t len;                             /* Nombre d'instructions au max*/
#ifndef NDEBUG
    size_t check;                           /* Verification de débordement */
#endif
    phys_t i;                               /* Boucle de parcours          */
    GArchInstruction *instr;                /* Instruction décodée         */

    result = (GArchInstruction **)realloc(list, (*count + area->count) * sizeof(GArchInstruction *));

    len = get_mrange_length(&area->range);

#ifndef NDEBUG
    check = 0;
#endif

    for (i = 0; i < len; i++)
    {
        instr = area->instructions[i];

        if (instr != NULL)
        {
            g_object_ref(G_OBJECT(instr));
            result[(*count)++] = instr;

#ifndef NDEBUG
            check++;
            assert(check <= area->count);
#endif

        }

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                            TRAITEMENT DE ZONES PAR LOTS                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : list  = listes de zones utable à consulter.                  *
*                count = nombre de zones mises en place.                      *
*                addr  = adresse à retrouver dans les aires présentes.        *
*                                                                             *
*  Description : Détermine une liste de zones contigües à traiter.            *
*                                                                             *
*  Retour      : Indice de la zone trouvée, ou nombre d'aires en cas d'échec. *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

mem_area *find_memory_area_by_addr(mem_area *list, size_t count, const vmpa2t *addr)
{
    mem_area *result;                       /* Elément trouvé à renvoyer   */

    int find_mem_area(const vmpa2t *_addr, const mem_area *_area)
    {
        int status;                         /* Bilan à retourner           */

        if (mrange_contains_addr(&_area->range, _addr))
            status = 0;

        else
            status = cmp_vmpa(_addr, get_mrange_addr(&_area->range));

        return status;

    }

    result = bsearch(addr, list, count, sizeof(mem_area), (__compar_fn_t)find_mem_area);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : areas  = liste de zones délimitant des contenus à traiter.   *
*                count  = nombre de zones à disposition.                      *
*                instr  = nouvelle instruction à venir insérer dans les zones.*
*                advice = éventuelle indication pour la zone de départ. [OUT] *
*                                                                             *
*  Description : Insère une instruction dans un ensemble d'aires.             *
*                                                                             *
*  Retour      : true si l'enregistrement a bien été réalisé, false sinon.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool insert_instr_into_mem_areas(mem_area *areas, size_t count, GArchInstruction *instr, mem_area **advice)
{
    bool result;                            /* Bilan d'action à renvoyer   */
    const mrange_t *range;                  /* Emplacement d'instruction   */
    const vmpa2t *start_addr;               /* Localisation précise        */
    mem_area *first_area;                   /* Zone d'appartenance         */
    vmpa2t end_addr;                        /* Position finale nominale    */
    mem_area *last_area;                    /* Zone d'arrivée              */
    size_t first_index;                     /* Indice de la première zone  */
    size_t last_index;                      /* Indice de la dernière zone  */
    size_t i;                               /* Boucle de parcours          */
    phys_t mark_start;                      /* Début du marquage           */
    phys_t mark_len;                        /* Taille dudit marquage       */

    range = g_arch_instruction_get_range(instr);
    start_addr = get_mrange_addr(range);

    /* Zone de départ */

    first_area = NULL;

    if (advice != NULL && *advice != NULL)
    {
        if (mrange_contains_addr(&(*advice)->range, start_addr))
            first_area = *advice;
    }

    if (first_area == NULL)
        first_area = find_memory_area_by_addr(areas, count, start_addr);

    assert(first_area != NULL);

    /* Zone d'arrivée */

    compute_mrange_end_addr(range, &end_addr);

    deminish_vmpa(&end_addr, 1);

    if (mrange_contains_addr(&first_area->range, &end_addr))
        last_area = first_area;

    else
    {
        last_area = find_memory_area_by_addr(areas, count, &end_addr);

        assert(last_area != NULL);

    }

    /* Verrouillage global ou local */

    first_index = first_area - areas;
    last_index = last_area - areas;

    if (first_index != last_index)
        g_mutex_lock(first_area->global);

    for (i = first_index; i <= last_index; i++)
        g_mutex_lock(&areas[i].mutex);

    if (first_index != last_index)
        g_mutex_unlock(first_area->global);

    /* Vérification des disponibilités */

    result = true;

    for (i = first_index; i <= last_index && result; i++)
    {
        if (i == first_index)
            mark_start = compute_vmpa_diff(get_mrange_addr(&first_area->range), start_addr);
        else
            mark_start = 0;

        if (i == last_index)
            mark_len = compute_vmpa_diff(get_mrange_addr(&last_area->range), &end_addr) + 1;
        else
            mark_len = get_mrange_length(&areas[i].range);;

        mark_len -= mark_start;

        result = _is_range_empty_in_mem_area(&areas[i], mark_start, mark_len);

    }

    if (!result)
        goto no_space_available;

    /* Inscriptions */

    for (i = first_index; i <= last_index; i++)
    {
        if (i == first_index)
            mark_start = compute_vmpa_diff(get_mrange_addr(&first_area->range), start_addr);
        else
            mark_start = 0;

        if (i == last_index)
            mark_len = compute_vmpa_diff(get_mrange_addr(&last_area->range), &end_addr) + 1;
        else
            mark_len = get_mrange_length(&areas[i].range);;

        mark_len -= mark_start;

        mark_range_in_mem_area_as_processed(&areas[i],
                                            i == first_index ? instr : NULL,
                                            mark_start, mark_len);

    }

 no_space_available:

    /* Déverrouillage global ou local */

    for (i = first_index; i <= last_index; i++)
        g_mutex_unlock(&areas[i].mutex);

    if (advice != NULL)
        *advice = last_area;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : areas = liste de zones délimitant des contenus à traiter.    *
*                count = nombre de zones à disposition.                       *
*                instr = nouvelle instruction à venir insérer dans les zones. *
*                                                                             *
*  Description : Force l'insertion d'une instruction dans un ensemble d'aires.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void insert_instr_into_mem_areas_forced(mem_area *areas, size_t count, GArchInstruction *instr)
{
    const mrange_t *range;                  /* Emplacement d'instruction   */
    const vmpa2t *start_addr;               /* Localisation précise        */
    mem_area *first_area;                   /* Zone d'appartenance         */
    vmpa2t end_addr;                        /* Position finale nominale    */
    mem_area *last_area;                    /* Zone d'arrivée              */
    size_t first_index;                     /* Indice de la première zone  */
    size_t last_index;                      /* Indice de la dernière zone  */
    size_t i;                               /* Boucle de parcours          */
    bool available;                         /* Zone intégralement dispo ?  */
    phys_t mark_start;                      /* Début du marquage           */
    phys_t mark_len;                        /* Taille dudit marquage       */
    mem_area *first_covered_area;           /* Zone d'appartenance         */
    size_t first_covered_index;             /* Indice de la première zone  */
    phys_t coverage_start;                  /* Début de zone à vider       */
    phys_t coverage_iter;                   /* Parcours des zones à vider  */
    phys_t coverage_len;                    /* Taille de cette même zone   */
    mem_area *last_covered_area;            /* Zone d'appartenance         */
    size_t last_covered_index;              /* Indice de la première zone  */
    phys_t remaining;                       /* Couverture minimale restante*/
    phys_t length;                          /* Taille de zone restante     */

    range = g_arch_instruction_get_range(instr);
    start_addr = get_mrange_addr(range);

    /* Récupération des zones couvertes par l'instruction */

    first_area = find_memory_area_by_addr(areas, count, start_addr);

    assert(first_area != NULL);

    compute_mrange_end_addr(range, &end_addr);

    deminish_vmpa(&end_addr, 1);

    if (mrange_contains_addr(&first_area->range, &end_addr))
        last_area = first_area;

    else
    {
        last_area = find_memory_area_by_addr(areas, count, &end_addr);

        assert(last_area != NULL);

    }

    /* Verrouillage global */

    first_index = first_area - areas;
    last_index = last_area - areas;

    g_mutex_lock(first_area->global);

    for (i = first_index; i <= last_index; i++)
        g_mutex_lock(&areas[i].mutex);

    /* Validation des disponibilités */

    available = true;

    for (i = first_index; i <= last_index && available; i++)
    {
        if (i == first_index)
            mark_start = compute_vmpa_diff(get_mrange_addr(&first_area->range), start_addr);
        else
            mark_start = 0;

        if (i == last_index)
            mark_len = compute_vmpa_diff(get_mrange_addr(&last_area->range), &end_addr) + 1;
        else
            mark_len = get_mrange_length(&areas[i].range);;

        mark_len -= mark_start;

        available = _is_range_empty_in_mem_area(&areas[i], mark_start, mark_len);

    }

    /* Si la couverture nécessite une mise à disposition */

    if (!available)
    {
        /**
         * Un cas de remplacement forcé intervient en ARM, lorsque qu'une
         * instruction utilise une valeur immédiate placée dans le code.
         *
         * Cette valeur doit être référencée en tant que donnée.
         *
         * Mais cette même valeur a pu être désassemblée en tant que code
         * exécutable si le flot d'exécution s'est poursuivi jusqu'à elle.
         *
         * C'est par exemple le cas lors de l'utilisation d'appels système
         * en assembleur, qui ne sont pas reconnus en tant qu'instructions
         * cassant le flot d'exécution (typiquement : un exit()).
         *
         * On réinitialise donc la zone couverte par la nouvelle instruction.
         */

        first_covered_area = first_area;
        first_covered_index = first_index;

        coverage_start = compute_vmpa_diff(get_mrange_addr(&first_covered_area->range), start_addr);

        coverage_iter = coverage_start;

        coverage_len = 0;

        /**
         * Par ailleurs, il se peut que la nouvelle instruction ne couvre
         * que partiellement une instruction existante.
         *
         * Il faut donc dans ce cas remonter la table des enregistrements
         * pour retrouver l'instruction à l'origine de la couverture à remplacer.
         */

        while (first_covered_area->instructions[coverage_start] == NULL)
        {
            if (coverage_start == 0)
            {
                assert(first_covered_index > 0);

                first_covered_area = &areas[--first_covered_index];
                g_mutex_lock(&first_covered_area->mutex);

                assert(get_mrange_length(&first_covered_area->range) > 0);

                coverage_start = get_mrange_length(&first_covered_area->range) - 1;

            }

            else
                coverage_start--;

            coverage_len++;

        }

        /**
         * De la même manière, on étend la couverture au besoin dans l'autre sens.
         */

        last_covered_area = last_area;
        last_covered_index = last_index;

        remaining = get_mrange_length(range);

        while (remaining > 0)
        {
            length = get_mrange_length(&last_covered_area->range) - coverage_iter;

            if (remaining >= length)
            {
                coverage_len += length;
                remaining -= length;

                if (remaining > 0)
                {
                    assert((last_covered_index + 1) < count);

                    last_covered_area = &areas[++last_covered_index];
                    g_mutex_lock(&last_covered_area->mutex);

                    coverage_iter = 0;

                }

            }

            else
            {
                coverage_len += remaining;
                remaining = 0;
            }

        }

        g_mutex_unlock(first_area->global);

        assert(coverage_len >= get_mrange_length(range));

        /* Réinitialisation */

        for (i = first_covered_index; i <= last_covered_index; i++)
        {
            if (i == first_covered_index)
                mark_start = coverage_start;
            else
                mark_start = 0;

            if (i == last_covered_index)
                mark_len = coverage_len;
            else
            {
                mark_len = get_mrange_length(&areas[i].range);;

                assert(mark_len > mark_start);

                mark_len -= mark_start;

            }

            coverage_len -= mark_len;

            unmark_range_in_mem_area_as_processed(&areas[i], mark_start, mark_len);

        }

        /* Libération des zones frontalières */

        for (i = first_covered_index; i < first_index; i++)
            g_mutex_unlock(&areas[i].mutex);

        for (i = (last_index + 1); i <= last_covered_index; i++)
            g_mutex_unlock(&areas[i].mutex);

        /* Vérification ultime */

#ifndef NDEBUG

        available = true;

        for (i = first_index; i <= last_index && available; i++)
        {
            if (i == first_index)
                mark_start = compute_vmpa_diff(get_mrange_addr(&first_area->range), start_addr);
            else
                mark_start = 0;

            if (i == last_index)
                mark_len = compute_vmpa_diff(get_mrange_addr(&last_area->range), &end_addr) + 1;
            else
                mark_len = get_mrange_length(&areas[i].range);;

            mark_len -= mark_start;

            available = _is_range_empty_in_mem_area(&areas[i], mark_start, mark_len);

        }

        assert(available);

#endif

    }

    else
        g_mutex_unlock(first_area->global);

    /* Inscription */

    for (i = first_index; i <= last_index; i++)
    {
        if (i == first_index)
            mark_start = compute_vmpa_diff(get_mrange_addr(&first_area->range), start_addr);
        else
            mark_start = 0;

        if (i == last_index)
            mark_len = compute_vmpa_diff(get_mrange_addr(&last_area->range), &end_addr) + 1;
        else
            mark_len = get_mrange_length(&areas[i].range);;

        mark_len -= mark_start;

        mark_range_in_mem_area_as_processed(&areas[i],
                                            i == first_index ? instr : NULL,
                                            mark_start, mark_len);

    }

    /* Déverrouillage des zones traitées restantes */

    for (i = first_index; i <= last_index; i++)
        g_mutex_unlock(&areas[i].mutex);

}



/* ---------------------------------------------------------------------------------- */
/*                         MANIPULATIONS PARALLELES DES ZONES                         */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour les tâches de traitement des zones. */
G_DEFINE_TYPE(GAreaCollector, g_area_collector, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des manipulations parallèles de zones.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_area_collector_class_init(GAreaCollectorClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_area_collector_dispose;
    object->finalize = (GObjectFinalizeFunc)g_area_collector_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_area_collector_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collector = instance à initialiser.                          *
*                                                                             *
*  Description : Initialise des manipulations parallèles de zones.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_area_collector_init(GAreaCollector *collector)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collector = instance d'objet GLib à traiter.                 *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_area_collector_dispose(GAreaCollector *collector)
{
    if (collector->run == (run_task_fc)g_area_collector_do_compute)
        g_clear_object(&collector->binary);

    else if (collector->run == (run_task_fc)g_area_collector_do_insert)
        g_clear_object(&collector->info);

    else if (collector->run == (run_task_fc)g_area_collector_do_fill)
            g_clear_object(&collector->ctx);

    G_OBJECT_CLASS(g_area_collector_parent_class)->dispose(G_OBJECT(collector));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collector = instance d'objet GLib à traiter.                 *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_area_collector_finalize(GAreaCollector *collector)
{
    if (collector->run == (run_task_fc)g_area_collector_do_compute)
    {
        /**
         * Il s'agit de la seule procédure où les zones mises en place sont
         * propres à un collecteur donné unique.
         *
         * Dans les autres cas, la liste est globale et partagée.
         */
        if (collector->areas != NULL)
            free(collector->areas);

    }

    else if (collector->run == (run_task_fc)g_area_collector_do_collect)
    {
        if (collector->collected != NULL)
            free(collector->collected);
    }

    G_OBJECT_CLASS(g_area_collector_parent_class)->finalize(G_OBJECT(collector));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collector = opérations à mener.                              *
*                status    = barre de statut à tenir informée.                *
*                                                                             *
*  Description : Assure un traitement particulier concernant les zones.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_area_collector_process(GAreaCollector *collector, GtkStatusStack *status)
{
    collector->run(G_DELAYED_WORK(collector), status);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id      = identifiant pour signaler la progression courante. *
*                binary  = binaire chargé à conserver dans les zones définies.*
*                global  = verrou pour les accès sur plusieurs zones.         *
*                info    = préchargements effectués via le format binaire.    *
*                first   = localisation du début de la portion à traiter.     *
*                last    = localisation de la fin de la portion à traiter.    *
*                closing = indique si la tâche doit terminer l'analyse.       *
*                                                                             *
*  Description : Crée une tâche de calcul des zones binaires à désassembler.  *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GAreaCollector *g_area_collector_new_intro(activity_id_t id, GLoadedBinary *binary, GMutex *global, phys_t first, phys_t last, bool closing)
{
    GAreaCollector *result;            /* Tâche à retourner           */

    result = g_object_new(G_TYPE_AREA_COLLECTOR, NULL);

    result->id = id;
    result->run = (run_task_fc)g_area_collector_do_compute;

    result->areas = NULL;

    result->created = 0;

    result->binary = binary;
    g_object_ref(G_OBJECT(binary));

    result->global = global;

    result->first = first;
    result->last = last;

    result->closing = closing;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collector = opération à mener.                               *
*                status    = barre de statut à tenir informée.                *
*                                                                             *
*  Description : Construit une liste bornée de zones contigües.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_area_collector_do_compute(GAreaCollector *collector, GtkStatusStack *status)
{
    mem_area **list;                        /* Liste de zones à constituer */
    size_t *count;                          /* Nombre d'éléments intégrés  */
    vmpa2t first;                           /* Point de départ             */
    vmpa2t last;                            /* Point d'arrivée             */
    GExeFormat *format;                     /* Format du binaire           */
    vmpa2t prev;                            /* Dernière bordure rencontrée */
    bool state;                             /* Bilan d'une conversion      */
    GBinPortion *portions;                  /* Couche première de portions */

    void fill_gap(vmpa2t *old, vmpa2t *new, bool alloc, bool exec)
    {
        phys_t diff;                        /* Espace entre bordures       */
        mem_area *area;                     /* Zone avec valeurs à éditer  */

        diff = compute_vmpa_diff(old, new);

        /**
         * S'il existe un écart entre la dernière bordure ajoutée et
         * l'extréminité de la portion courante, on le comble !
         */

        if (diff > 0)
        {
            if (!alloc)
                reset_virt_addr(old);

            /* Zone tampon à constituer */

            *list = (mem_area *)realloc(*list, ++(*count) * sizeof(mem_area));

            area = &(*list)[*count - 1];

            init_mem_area_from_addr(area, old, diff, collector->binary, collector->global);
            area->is_exec = exec;

            /* Avancée du curseur */

            copy_vmpa(old, new);

            gtk_status_stack_update_activity_value(status, collector->id, diff);

        }

        else
        {
            /**
             * La comparaison entre les bordures se réalise selon les positions
             * physiques renseignées.
             *
             * Aussi, même dans le cas d'une jointure sans espace, il se peut que
             * la transition concerne deux zones aux adresses virtuelles non
             * consécutives.
             *
             * Comme "old" est mise à jour pour devenir le point de départ de
             * la zone suivante, on se doit de même à jour les deux positions :
             * physique et virtuelle.
             */

            copy_vmpa(old, new);

        }

    }

    bool build_area_from_portion(GBinPortion *portion, GBinPortion *parent, BinaryPortionVisit visit, void *unused)
    {
        const mrange_t *range;              /* Espace de portion à traiter */
        vmpa2t border;                      /* Nouvelle bordure rencontrée */
        bool on_track;                      /* Le tronçon courant est bon ?*/
        PortionAccessRights rights;         /* Droits d'accès à analyser   */

        range = g_binary_portion_get_range(portion);

        if (visit == BPV_ENTER)
        {
            copy_vmpa(&border, get_mrange_addr(range));

            on_track = cmp_vmpa(&first, &border) <= 0 && cmp_vmpa(&border, &last) < 0;

            if (on_track)
            {
                rights = (parent != NULL ? g_binary_portion_get_rights(parent) : PAC_NONE);
                fill_gap(&prev, &border, rights != PAC_NONE, rights & PAC_EXEC);
            }
            else
                copy_vmpa(&prev, &border);

        }

        else if (visit == BPV_SHOW)
        {
            copy_vmpa(&border, get_mrange_addr(range));

            on_track = cmp_vmpa(&first, &border) <= 0 && cmp_vmpa(&border, &last) < 0;

            if (on_track)
            {
                rights = (parent != NULL ? g_binary_portion_get_rights(parent) : PAC_NONE);
                fill_gap(&prev, &border, rights != PAC_NONE, rights & PAC_EXEC);

                compute_mrange_end_addr(range, &border);

                rights = g_binary_portion_get_rights(portion);
                fill_gap(&prev, &border, rights != PAC_NONE, rights & PAC_EXEC);

            }
            else
                compute_mrange_end_addr(range, &prev);

        }

        else if (visit == BPV_EXIT)
        {
            compute_mrange_end_addr(range, &border);

            if (collector->closing)
                on_track = cmp_vmpa(&first, &border) <= 0 && cmp_vmpa(&border, &last) <= 0;
            else
                on_track = cmp_vmpa(&first, &border) <= 0 && cmp_vmpa(&border, &last) < 0;

            if (on_track)
            {
                rights = (parent != NULL ? g_binary_portion_get_rights(parent) : PAC_NONE);
                fill_gap(&prev, &border, rights != PAC_NONE, rights & PAC_EXEC);
            }
            else
                copy_vmpa(&prev, &border);

        }

#ifndef NDEBUG
        else
            assert(false);
#endif

        return (cmp_vmpa(&prev, &last) < 0);

    }

    list = &collector->areas;
    count = &collector->created;

    init_vmpa(&first, collector->first, VMPA_NO_VIRTUAL);
    init_vmpa(&last, collector->last, VMPA_NO_VIRTUAL);

    format = g_loaded_binary_get_format(collector->binary);

    state = g_exe_format_translate_offset_into_vmpa(format, 0, &prev);

    if (!state)
        init_vmpa(&prev, 0, VMPA_NO_PHYSICAL);

    portions = g_exe_format_get_portions(format);

    g_binary_portion_visit(portions, (visit_portion_fc)build_area_from_portion, NULL);

    g_object_unref(G_OBJECT(portions));

    g_object_unref(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : gid    = groupe de travail impliqué.                         *
*                status = barre de statut à tenir informée.                   *
*                binary = binaire analysé contenant quantités d'infos.        *
*                length = quantité d'octets à traiter au total.               *
*                count  = nombre de zones mises en place. [OUT]               *
*                                                                             *
*  Description : Détermine une liste de zones contigües à traiter.            *
*                                                                             *
*  Retour      : Liste de zones mémoire à libérer après usage.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

mem_area *collect_memory_areas(wgroup_id_t gid, GtkStatusStack *status, GLoadedBinary *binary, phys_t length, size_t *count)
{
    mem_area *result;                       /* Liste finale à retourner    */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    phys_t run_size;                        /* Volume réparti par exécution*/
    GAreaCollector **collectors;            /* Collecteurs à suivre        */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    activity_id_t id;                       /* Identifiant de progression  */
    GMutex *global;                         /* Atomicité sur zones multi.  */
    guint i;                                /* Boucle de parcours          */
    phys_t first;                           /* Début de zone de traitement */
    bool closing;                           /* Détection de fin en amont   */
    phys_t last;                            /* Fin de zone de traitement   */

    /* Création d'un verrou global */

    global = (GMutex *)malloc(sizeof(GMutex));

    g_mutex_init(global);

    /* Lancement des traitements */

    run_size = compute_run_size(length, &runs_count);

    collectors = (GAreaCollector **)calloc(runs_count, sizeof(GAreaCollector *));

    queue = get_work_queue();

    id = gtk_status_stack_add_activity(status, _("Computing memory areas to disassemble"), length);

    for (i = 0; i < runs_count; i++)
    {
        first = i * run_size;

        closing = ((i + 1) == runs_count);

        if (closing)
            last = length;
        else
            last = first + run_size;

        collectors[i] = g_area_collector_new_intro(id, binary, global, first, last, closing);

        g_object_ref(G_OBJECT(collectors[i]));
        g_work_queue_schedule_work(queue, G_DELAYED_WORK(collectors[i]), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

    /* Récupération des aires */

    result = NULL;
    *count = 0;

    for (i = 0; i < runs_count; i++)
    {
        result = (mem_area *)realloc(result, (*count + collectors[i]->created) * sizeof(mem_area));

        memcpy(&result[*count], collectors[i]->areas, collectors[i]->created * sizeof(mem_area));
        *count += collectors[i]->created;

        g_object_unref(G_OBJECT(collectors[i]));

    }

    /* Fin */

    free(collectors);

    gtk_status_stack_remove_activity(status, id);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id        = identifiant pour signaler la progression.        *
*                areas     = liste des zones en place à parcourir.            *
*                available = nombre de zones disponibles pour les traitements.*
*                info      = préchargements effectués via le format binaire.  *
*                start     = indice de la première instruction à insérer.     *
*                stop      = indice de la première instruction à ignorer.     *
*                                                                             *
*  Description : Crée une tâche de calcul des zones binaires à remplir.       *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GAreaCollector *g_area_collector_new_insert(activity_id_t id, mem_area *areas, size_t available, GPreloadInfo *info, size_t start, size_t stop)
{
    GAreaCollector *result;            /* Tâche à retourner           */

    result = g_object_new(G_TYPE_AREA_COLLECTOR, NULL);

    result->id = id;
    result->run = (run_task_fc)g_area_collector_do_insert;

    result->areas = areas;

    result->available = available;

    result->info = info;
    g_object_ref(G_OBJECT(info));

    result->start = start;
    result->stop = stop;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collector = opération à mener.                               *
*                status    = barre de statut à tenir informée.                *
*                                                                             *
*  Description : Insère dans les zones contigües les instructions préchargées.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_area_collector_do_insert(GAreaCollector *collector, GtkStatusStack *status)
{
    mem_area *last;                         /* Zone d'appartenance         */
    size_t i;                               /* Boucle de parcours #1       */
    GArchInstruction *instr;                /* Instruction à analyser      */
    bool done;                              /* Insertion réalisée ?        */
    const mrange_t *range;                  /* Emplacement de l'instruction*/
    VMPA_BUFFER(loc);                       /* Traduction en texte         */

    last = NULL;

    for (i = collector->start; i < collector->stop; i++)
    {
        instr = _g_preload_info_grab_instruction(collector->info, i);

        done = insert_instr_into_mem_areas(collector->areas, collector->available, instr, &last);

        if (!done)
        {
            range = g_arch_instruction_get_range(instr);
            vmpa2_phys_to_string(get_mrange_addr(range), MDS_UNDEFINED, loc, NULL);

            log_variadic_message(LMT_ERROR, "Failed to insert one collected instruction @ %s", loc);

        }

        g_object_unref(G_OBJECT(instr));

        gtk_status_stack_update_activity_value(status, collector->id, 1);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : gid    = groupe de travail impliqué.                         *
*                status = barre de statut à tenir informée.                   *
*                area   = nombre de zones mises en place.                     *
*                count  = quantité de ces zones.                              *
*                info   = préchargements effectués via le format binaire.     *
*                                                                             *
*  Description : Intègre toutes les instructions préchargées dans des zones.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void populate_fresh_memory_areas(wgroup_id_t gid, GtkStatusStack *status, mem_area *areas, size_t count, GPreloadInfo *info)
{
    size_t icount;                          /* Quantité d'instructions     */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    phys_t run_size;                        /* Volume réparti par exécution*/
    GAreaCollector **collectors;            /* Collecteurs à suivre        */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    activity_id_t id;                       /* Identifiant de progression  */
    guint i;                                /* Boucle de parcours          */
    size_t start;                           /* Premier indice à traiter    */
    size_t stop;                            /* Premier indice à ignorer    */

    g_preload_info_lock_instructions(info);

    icount = _g_preload_info_count_instructions(info);

    run_size = compute_run_size(icount, &runs_count);

    collectors = (GAreaCollector **)calloc(runs_count, sizeof(GAreaCollector *));

    queue = get_work_queue();

    id = gtk_status_stack_add_activity(status, _("Inserting all preloaded instructions"), icount);

    for (i = 0; i < runs_count; i++)
    {
        start = i * run_size;

        if ((i + 1) == runs_count)
            stop = icount;
        else
            stop = start + run_size;

        collectors[i] = g_area_collector_new_insert(id, areas, count, info, start, stop);

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(collectors[i]), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

    /* Fin */

    free(collectors);

    _g_preload_info_drain_instructions(info);

    assert(_g_preload_info_count_instructions(info) == 0);

    g_preload_info_unlock_instructions(info);

    gtk_status_stack_remove_activity(status, id);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id    = identifiant pour signaler la progression courante.   *
*                areas = liste complète des zones à traiter.                  *
*                count = taille de cette liste.                               *
*                ctx   = éventuel contexte pour du code ou NULL si données.   *
*                start = première zone à traiter.                             *
*                stop  = première zone à écarter.                             *
*                                                                             *
*  Description : Crée une tâche de fin de désassemblage pour zones binaires.  *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GAreaCollector *g_area_collector_new_filling(activity_id_t id, mem_area *areas, size_t count, GProcContext *ctx, size_t start, size_t stop)
{
    GAreaCollector *result;            /* Tâche à retourner           */

    result = g_object_new(G_TYPE_AREA_COLLECTOR, NULL);

    result->id = id;
    result->run = (run_task_fc)g_area_collector_do_fill;

    result->areas = areas;

    result->count = count;

    result->ctx = ctx;

    if (ctx != NULL)
        g_object_ref(G_OBJECT(ctx));

    result->fill_start = start;
    result->fill_stop = stop;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collector = opération à mener.                               *
*                status    = barre de statut à tenir informée.                *
*                                                                             *
*  Description : Remplit de code ou de données une série de zones.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_area_collector_do_fill(GAreaCollector *collector, GtkStatusStack *status)
{
    mem_area *areas;                        /* Zone de productions         */
    size_t count;                           /* Nombre de ces zones         */
    size_t i;                               /* Boucle de parcours          */

    areas = collector->areas;
    count = collector->count;

    if (collector->ctx != NULL)
        for (i = collector->fill_start; i < collector->fill_stop; i++)
            fill_mem_area_with_code(&areas[i], areas, count, collector->ctx, status, collector->id);

    else
        for (i = collector->fill_start; i < collector->fill_stop; i++)
            fill_mem_area_with_data(&areas[i], areas, count, status, collector->id);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : gid    = groupe de travail impliqué.                         *
*                status = barre de statut à tenir informée.                   *
*                id     = identifiant d'activité à modifier.                  *
*                area   = nombre de zones mises en place.                     *
*                count  = quantité de ces zones.                              *
*                ctx    = contexte de désassemblage pour du code, ou NULL.    *
*                                                                             *
*  Description : Remplit les espaces vacants des zones à désassembler.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void ensure_all_mem_areas_are_filled(wgroup_id_t gid, GtkStatusStack *status, activity_id_t id, mem_area *areas, size_t count, GProcContext *ctx)
{
    guint runs_count;                       /* Qté d'exécutions parallèles */
    phys_t run_size;                        /* Volume réparti par exécution*/
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    guint i;                                /* Boucle de parcours          */
    size_t start;                           /* Premier indice à traiter    */
    size_t stop;                            /* Premier indice à ignorer    */
    GAreaCollector *collector;              /* Collecteur à lancer         */

    runs_count = get_max_online_threads();

    run_size = count / runs_count;

    queue = get_work_queue();

    if (ctx != NULL)
        gtk_status_stack_update_activity(status, id, _("Disassembling the remaining instructions..."));
    else
        gtk_status_stack_update_activity(status, id, _("Filling holes with data..."));

    for (i = 0; i < runs_count; i++)
    {
        start = i * run_size;

        if ((i + 1) == runs_count)
            stop = count;
        else
            stop = start + run_size;

        collector = g_area_collector_new_filling(id, areas, count, ctx, start, stop);

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(collector), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id    = identifiant pour signaler la progression courante.   *
*                list  = liste des zones en place à parcourir.                *
*                begin = indice de la première zone à traiter.                *
*                end   = indice de la première zone à ne pas traiter.         *
*                                                                             *
*  Description : Crée une tâche de récupération d'instructions différée.      *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GAreaCollector *g_area_collector_new_outro(activity_id_t id, mem_area *list, size_t begin, size_t end)
{
    GAreaCollector *result;            /* Tâche à retourner           */

    result = g_object_new(G_TYPE_AREA_COLLECTOR, NULL);

    result->id = id;
    result->run = (run_task_fc)g_area_collector_do_collect;

    result->areas = list;

    result->begin = begin;
    result->end = end;

    result->collected = NULL;
    result->ccount = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collector = opération à mener.                               *
*                status    = barre de statut à tenir informée.                *
*                                                                             *
*  Description : Assure la récupération d'instructions en différé.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_area_collector_do_collect(GAreaCollector *collector, GtkStatusStack *status)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = collector->begin; i < collector->end; i++)
    {
        collector->collected = get_instructions_from_mem_area(&collector->areas[i],
                                                              collector->collected, &collector->ccount);

        fini_mem_area(&collector->areas[i]);

        gtk_status_stack_update_activity_value(status, collector->id, 1);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : gid    = groupe de travail impliqué.                         *
*                status = barre de statut à tenir informée.                   *
*                list   = liste des zones de données à relire puis libérer.   *
*                acount = taille de cette liste de zones.                     *
*                icount = nombre d'instructions récupérées. [OUT]             *
*                                                                             *
*  Description : Rassemble les instructions conservées dans des zones données.*
*                                                                             *
*  Retour      : Liste d'instructions rassemblées.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction **collect_disassembled_instructions(wgroup_id_t gid, GtkStatusStack *status, mem_area *list, size_t acount, size_t *icount)
{
    GArchInstruction **result;              /* Liste finale à retourner    */
    GMutex *global;                         /* Atomicité sur zones multi.  */
    guint runs_count;                       /* Qté d'exécutions parallèles */
    size_t run_size;                        /* Volume réparti par exécution*/
    GAreaCollector **collectors;            /* Collecteurs à suivre        */
    GWorkQueue *queue;                      /* Gestionnaire de différés    */
    activity_id_t id;                       /* Identifiant de progression  */
    guint i;                                /* Boucle de parcours          */
    size_t begin;                           /* Début de bloc de traitement */
    size_t end;                             /* Fin d'un bloc de traitement */

    /* Suppression du verrou global */

    assert(acount > 0);

    global = list[0].global;

    g_mutex_clear(global);

    free(global);

    /* Lancement des traitements */

    run_size = compute_run_size(acount, &runs_count);

    collectors = (GAreaCollector **)calloc(runs_count, sizeof(GAreaCollector *));

    queue = get_work_queue();

    id = gtk_status_stack_add_activity(status, _("Collecting all disassembled instructions"), acount);

    for (i = 0; i < runs_count; i++)
    {
        begin = i * run_size;

        if ((i + 1) == runs_count)
            end = acount;
        else
            end = begin + run_size;

        collectors[i] = g_area_collector_new_outro(id, list, begin, end);

        g_object_ref(G_OBJECT(collectors[i]));
        g_work_queue_schedule_work(queue, G_DELAYED_WORK(collectors[i]), gid);

    }

    g_work_queue_wait_for_completion(queue, gid);

    /* Récupération des instructions */

    result = NULL;
    *icount = 0;

    for (i = 0; i < runs_count; i++)
    {
        result = (GArchInstruction **)realloc(result,
                                              (*icount + collectors[i]->ccount) * sizeof(GArchInstruction *));

        memcpy(&result[*icount], collectors[i]->collected, collectors[i]->ccount * sizeof(GArchInstruction *));
        *icount += collectors[i]->ccount;

        g_object_unref(G_OBJECT(collectors[i]));

    }

    /* Fin */

    free(collectors);

    free(list);

    gtk_status_stack_remove_activity(status, id);

    return result;

}
