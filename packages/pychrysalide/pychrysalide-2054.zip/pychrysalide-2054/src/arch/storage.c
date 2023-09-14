
/* Chrysalide - Outil d'analyse de fichiers binaires
 * storage.c - conservation hors mémoire vive des instructions désassemblées
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "storage.h"


#include <assert.h>
#include <fcntl.h>
#include <malloc.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>


#include "instruction.h"
#include "operands/target.h"
#include "../common/compression.h"
#include "../common/extstr.h"
#include "../common/pathname.h"
#include "../common/xdg.h"
#include "../core/global.h"
#include "../core/logs.h"
#include "../core/queue.h"
#include "../glibext/delayed-int.h"



/* ----------------- CONSERVATION EXTERNE DES INSTRUCTIONS CHARGEES ----------------- */


#define G_TYPE_INS_CACHING            g_ins_caching_get_type()
#define G_INS_CACHING(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_INS_CACHING, GInsCaching))
#define G_IS_INS_CACHING(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_INS_CACHING))
#define G_INS_CACHING_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_INS_CACHING, GInsCachingClass))
#define G_IS_INS_CACHING_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_INS_CACHING))
#define G_INS_CACHING_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_INS_CACHING, GInsCachingClass))


/* Ensembles binaires à désassembler (instance) */
typedef struct _GInsCaching
{
    GDelayedWork parent;                    /* A laisser en premier        */

    GArchProcessor *proc;                   /* Ensemble à traiter          */
    GAsmStorage *storage;                   /* Cache de destinartion       */

    GBinFormat *format;                     /* Nature de l'opération       */

    bool status;                            /* Bilan de l'opération        */

} GInsCaching;

/* Ensembles binaires à désassembler (classe) */
typedef struct _GInsCachingClass
{
    GDelayedWorkClass parent;               /* A laisser en premier        */

} GInsCachingClass;


/* Indique le type défini pour les tâches d'enregistrement des instructions. */
GType g_ins_caching_get_type(void);

/* initialise la classe des tâches de cache d'instructions. */
static void g_ins_caching_class_init(GInsCachingClass *);

/* Initialise une tâche de cache d'instructions. */
static void g_ins_caching_init(GInsCaching *);

/* Supprime toutes les références externes. */
static void g_ins_caching_dispose(GInsCaching *);

/* Procède à la libération totale de la mémoire. */
static void g_ins_caching_finalize(GInsCaching *);

/* Crée une tâche de mise en cache de toutes les instructions. */
static GInsCaching *g_ins_caching_new(GArchProcessor *, GAsmStorage *, GBinFormat *);

/* Assure la conservation ou le chargement d'instructions. */
static void g_ins_caching_process(GInsCaching *, GtkStatusStack *);

/* Assure le chargement d'instructions en différé. */
static void g_ins_caching_process_load(GInsCaching *, GtkStatusStack *);

/* Assure la conservation d'instructions en différé. */
static void g_ins_caching_process_store(GInsCaching *, GtkStatusStack *);

/* Fournit le bilan des traitements d'instructions en différé. */
static bool g_ins_caching_get_status(const GInsCaching *);



/* ------------------- MECANISME DE SAUVEGARDE ET DE RESTAURATION ------------------- */


/* Conservation d'une référence sur un type */
typedef struct _gtype_ref_info_t
{
    GType gtype;                            /* Type pour la GLib           */
    gpointer gclass;                        /* Lien vers sa classe         */

} gtype_ref_info_t;

/* Définition d'une conservation d'instructions d'assemblage (instance) */
struct _GAsmStorage
{
    GObject parent;                         /* A laisser en premier        */

    char *id;                               /* Identifiant de contenu      */

    char *idx_filename;                     /* Fichier pour l'indexage     */
    char *ins_filename;                     /* Fichier pour instructions   */
    char *op_filename;                      /* Fichier pour les opérandes  */
    char *reg_filename;                     /* Fichier pour les registres  */
    char *tp_filename;                      /* Fichier pour les types      */

    int idx_fd;                             /* Flux pour l'indexage        */
    int ins_fd;                             /* Flux pour les instructions  */
    int op_fd;                              /* Flux pour les opérandes     */
    int reg_fd;                             /* Flux pour les registres     */
    int tp_fd;                              /* Flux pour les types         */

    /**
     * La GLib n'est pas très claire sur la taille de GType :
     *
     *    #if     GLIB_SIZEOF_SIZE_T != GLIB_SIZEOF_LONG || !defined __cplusplus
     *    typedef gsize                           GType;
     *    #else   // for historic reasons, C++ links against gulong GTypes
     *    typedef gulong                          GType;
     *    #endif
     *
     * Et :
     *
     *    typedef unsigned $glib_size_type_define gsize;
     *
     * On prend le parti de réduire à 65536 types possibles dans l'enregistrement
     * des objets instanciés, et on conserve ces types en tant qu'unsigned short.
     */

    gtype_ref_info_t *gtypes;               /* Types des objets reconnus   */
    size_t gtp_count;                       /* Quantité de ces objets      */
    GMutex gtp_mutex;                       /* Contrôle d'accès à la liste */

    GArchProcessor *proc;                   /* Ensemble à traiter          */

    GArchInstruction **collected;           /* Liste d'instructions        */
    off64_t length;                         /* Taille de cette liste       */
    size_t count;                           /* Nombre de présences         */

};

/* Définition d'une conservation d'instructions d'assemblage (classe) */
struct _GAsmStorageClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    /* Signaux */

    void (* saved) (GAsmStorage *);

};


/* Initialise la classe des conservations d'instructions. */
static void g_asm_storage_class_init(GAsmStorageClass *);

/* Initialise une instance de conservation d'instructions. */
static void g_asm_storage_init(GAsmStorage *);

/* Supprime toutes les références externes. */
static void g_asm_storage_dispose(GAsmStorage *);

/* Procède à la libération totale de la mémoire. */
static void g_asm_storage_finalize(GAsmStorage *);

/* Indique le chemin d'accès à l'archive finale. */
static char *g_asm_storage_get_archive_filename(const GAsmStorage *);

/* Décompresse les fichiers de cache d'instructions. */
static bool g_asm_storage_decompress(const GAsmStorage *);

/* Compresse les fichiers de cache d'instructions. */
static bool g_asm_storage_compress(const GAsmStorage *);

/* Apprend tous les types mémorisés dans un fichier. */
static bool g_asm_storage_read_types(GAsmStorage *);

/* Enregistre tous les types mémorisés dans un fichier. */
static bool g_asm_storage_write_types(GAsmStorage *);

/* Ouvre tous les fichiers nécessaires à une opération. */
static bool g_asm_storage_open_files(GAsmStorage *, int );

/* Acquitte la fin d'une tâche de sauvegarde complète. */
static void on_cache_saving_completed(GInsCaching *, GAsmStorage *);



/* ---------------------------------------------------------------------------------- */
/*                   CONSERVATION EXTERNE DES INSTRUCTIONS CHARGEES                   */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour les tâches d'enregistrement des instructions. */
G_DEFINE_TYPE(GInsCaching, g_ins_caching, G_TYPE_DELAYED_WORK);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des tâches de cache d'instructions.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_ins_caching_class_init(GInsCachingClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDelayedWorkClass *work;                /* Version en classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_ins_caching_dispose;
    object->finalize = (GObjectFinalizeFunc)g_ins_caching_finalize;

    work = G_DELAYED_WORK_CLASS(klass);

    work->run = (run_task_fc)g_ins_caching_process;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : caching = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une tâche de cache d'instructions.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_ins_caching_init(GInsCaching *caching)
{
    caching->status = true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : caching = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_ins_caching_dispose(GInsCaching *caching)
{
    g_object_unref(G_OBJECT(caching->proc));

    g_object_unref(G_OBJECT(caching->storage));

    if (caching->format != NULL)
        g_object_unref(G_OBJECT(caching->format));

    G_OBJECT_CLASS(g_ins_caching_parent_class)->dispose(G_OBJECT(caching));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : caching = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_ins_caching_finalize(GInsCaching *caching)
{
    G_OBJECT_CLASS(g_ins_caching_parent_class)->finalize(G_OBJECT(caching));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc    = gestionnaire de l'ensemble d'instructions visées.  *
*                storage = gestionnaire de la conservation à venir.           *
*                format  = format binaire chargé associé à l'architecture.    *
*                                                                             *
*  Description : Crée une tâche de mise en cache de toutes les instructions.  *
*                                                                             *
*  Retour      : Tâche créée.                                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GInsCaching *g_ins_caching_new(GArchProcessor *proc, GAsmStorage *storage, GBinFormat *format)
{
    GInsCaching *result;            /* Tâche à retourner           */

    result = g_object_new(G_TYPE_INS_CACHING, NULL);

    result->proc = proc;
    g_object_ref(G_OBJECT(result->proc));

    result->storage = storage;
    g_object_ref(G_OBJECT(result->storage));

    result->format = format;

    if (format != NULL)
        g_object_ref(G_OBJECT(format));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : caching = opération d'enregistrement à mener.                *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Assure la conservation ou le chargement d'instructions.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_ins_caching_process(GInsCaching *caching, GtkStatusStack *status)
{
    if (caching->format != NULL)
        g_ins_caching_process_load(caching, status);

    else
        g_ins_caching_process_store(caching, status);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : caching = opération d'enregistrement à mener.                *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Assure le chargement d'instructions en différé.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_ins_caching_process_load(GInsCaching *caching, GtkStatusStack *status)
{
    GAsmStorage *storage;                   /* Cache de destinartion       */
    packed_buffer_t pbuf;                   /* Tampon des données à écrire */
    off64_t i;                              /* Boucle de parcours          */
    off64_t pos;                            /* Position courante           */
    GArchInstruction *instr;                /* Instruction à traiter       */
    off64_t target;                         /* Position dans le flux       */

    storage = caching->storage;

    init_packed_buffer(&pbuf);

    for (i = 0; i < storage->length && caching->status; i++)
    {
        /* Des données sont-elles présentes à cette position ? */

        pos = lseek64(storage->idx_fd, i * sizeof(off64_t), SEEK_SET);

        if (pos != (i * sizeof(off64_t)))
        {
            perror("lseek64");
            caching->status = false;
            break;
        }

        caching->status = safe_read(storage->idx_fd, &target, sizeof(off64_t));

        if (!caching->status)
            break;

        if (target == (off64_t)-1)
            continue;

        /* Chargement de l'instruction */

        instr = g_asm_storage_get_instruction_at(storage, caching->format, i, &pbuf);

        if (instr == NULL)
            caching->status = false;

        else
            g_object_unref(G_OBJECT(instr));

    }

    exit_packed_buffer(&pbuf);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : caching = opération d'enregistrement à mener.                *
*                status  = barre de statut à tenir informée.                  *
*                                                                             *
*  Description : Assure la conservation d'instructions en différé.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_ins_caching_process_store(GInsCaching *caching, GtkStatusStack *status)
{
    GArchProcessor *proc;                   /* Ensemble à traiter          */
    GAsmStorage *storage;                   /* Cache de destinartion       */
    packed_buffer_t pbuf;                   /* Tampon des données à écrire */
    size_t count;                           /* Quantité d'instructions     */
    phys_t last_phys;                       /* Dernière position physique  */
    size_t i;                               /* Boucle de parcours #1       */
    GArchInstruction *instr;                /* Instruction à traiter       */
    off64_t pos;                            /* Position dans le flux       */
    const mrange_t *irange;                 /* Emplacement de l'instruction*/
    phys_t cur_phys;                        /* Position physique courante  */
    phys_t k;                               /* Boucle de parcours #2       */

    proc = caching->proc;
    storage = caching->storage;

    init_packed_buffer(&pbuf);

    g_arch_processor_lock(proc);

    count = g_arch_processor_count_instructions(proc);

    last_phys = VMPA_NO_PHYSICAL;

    for (i = 0; i < count && caching->status; i++)
    {
        /* Enregistrement de l'instruction */

        instr = g_arch_processor_get_instruction(proc, i);

        caching->status = false;//g_arch_instruction_store__old(instr, storage, &pbuf);

        if (caching->status)
            caching->status = g_asm_storage_store_instruction_data(storage, &pbuf, &pos);

        /* Enregistrement de la position */

        if (caching->status)
        {
            irange = g_arch_instruction_get_range(instr);

            cur_phys = get_phy_addr(get_mrange_addr(irange));

            assert((last_phys == VMPA_NO_PHYSICAL && cur_phys == 0) || (cur_phys > 0 && last_phys < cur_phys));

            if (last_phys != VMPA_NO_PHYSICAL)
                for (k = last_phys; k < (cur_phys - 1) && caching->status; k++)
                    caching->status = safe_write(storage->idx_fd, (off64_t []) { -1 }, sizeof(off64_t));

            caching->status = safe_write(storage->idx_fd, &pos, sizeof(off64_t));

            last_phys = cur_phys;

        }

        g_object_unref(G_OBJECT(instr));

    }

    g_arch_processor_unlock(proc);

    exit_packed_buffer(&pbuf);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : caching = opération d'enregistrement à mener.                *
*                                                                             *
*  Description : Fournit le bilan des traitements d'instructions en différé.  *
*                                                                             *
*  Retour      : Bilan des opérations.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_ins_caching_get_status(const GInsCaching *caching)
{
    bool result;                            /* Bilan à retourner           */

    result = caching->status;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                     MECANISME DE SAUVEGARDE ET DE RESTAURATION                     */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une conservation d'instructions d'assemblage. */
G_DEFINE_TYPE(GAsmStorage, g_asm_storage, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des conservations d'instructions.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_asm_storage_class_init(GAsmStorageClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_asm_storage_dispose;
    object->finalize = (GObjectFinalizeFunc)g_asm_storage_finalize;

    g_signal_new("saved",
                 G_TYPE_ASM_STORAGE,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GAsmStorageClass, saved),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__VOID,
                 G_TYPE_NONE, 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de conservation d'instructions.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_asm_storage_init(GAsmStorage *storage)
{
    storage->idx_filename = NULL;
    storage->ins_filename = NULL;
    storage->op_filename = NULL;
    storage->reg_filename = NULL;
    storage->tp_filename = NULL;

    storage->idx_fd = -1;
    storage->ins_fd = -1;
    storage->op_fd = -1;
    storage->reg_fd = -1;
    storage->tp_fd = -1;

    storage->gtypes = NULL;
    storage->gtp_count = 0;
    g_mutex_init(&storage->gtp_mutex);

    storage->proc = NULL;

    storage->collected = NULL;
    storage->length = 0;
    storage->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_asm_storage_dispose(GAsmStorage *storage)
{
    size_t i;                               /* Boucle de parcours          */

    g_mutex_lock(&storage->gtp_mutex);

    for (i = 0; i < storage->gtp_count; i++)
        if (storage->gtypes[i].gclass != NULL)
            g_type_class_unref(storage->gtypes[i].gclass);

    g_mutex_unlock(&storage->gtp_mutex);

    g_mutex_clear(&storage->gtp_mutex);

    if (storage->proc != NULL)
        g_object_unref(G_OBJECT(storage->proc));

    for (i = 0; i < storage->length; i++)
        if (storage->collected[i] != NULL)
            g_object_unref(G_OBJECT(storage->collected[i]));

    G_OBJECT_CLASS(g_asm_storage_parent_class)->dispose(G_OBJECT(storage));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_asm_storage_finalize(GAsmStorage *storage)
{
    int ret;                                /* Bilan d'un appel            */

    free(storage->id);

#define finalize_storage_file(f)                \
    if (f != NULL)                              \
    {                                           \
        ret = access(f, W_OK);                  \
        if (ret == 0)                           \
        {                                       \
            ret = unlink(f);                    \
            if (ret != 0) perror("unlink");     \
        }                                       \
        free(f);                                \
    }

    finalize_storage_file(storage->idx_filename);
    finalize_storage_file(storage->ins_filename);
    finalize_storage_file(storage->op_filename);
    finalize_storage_file(storage->reg_filename);
    finalize_storage_file(storage->tp_filename);

    if (storage->idx_fd != -1)
        close(storage->idx_fd);

    if (storage->ins_fd != -1)
        close(storage->ins_fd);

    if (storage->op_fd != -1)
        close(storage->op_fd);

    if (storage->reg_fd != -1)
        close(storage->reg_fd);

    if (storage->gtypes != NULL)
        free(storage->gtypes);

    if (storage->collected != NULL)
        free(storage->collected);

    G_OBJECT_CLASS(g_asm_storage_parent_class)->finalize(G_OBJECT(storage));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = gestionnaire de l'ensemble d'instructions visées.     *
*                id   = identifiant pour la zone d'enregistrements.           *
*                                                                             *
*  Description : Crée le support d'une conservation d'instructions.           *
*                                                                             *
*  Retour      : Mécanismes mis en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GAsmStorage *g_asm_storage_new_compressed(GArchProcessor *proc, const gchar *id)
{
    GAsmStorage *result;                    /* Structure à retourner       */
    char *suffix;                           /* Fin du nom de fichier       */
    char *basedir;                          /* Chemin d'accès              */
    bool status;                            /* Assurance de validité       */

    result = g_object_new(G_TYPE_ASM_STORAGE, NULL);

    result->id = strdup(id);

    result->proc = proc;
    g_object_ref(G_OBJECT(proc));

    suffix = strdup("chrysalide");
    suffix = stradd(suffix, G_DIR_SEPARATOR_S);
    suffix = stradd(suffix, "cache");
    suffix = stradd(suffix, G_DIR_SEPARATOR_S);

    basedir = get_xdg_config_dir(suffix);

    free(suffix);

    status = mkpath(basedir);
    if (!status) goto gasn_base_error;

    asprintf(&result->idx_filename, "%s.%s-%s", basedir, id, "index.bin");
    asprintf(&result->ins_filename, "%s.%s-%s", basedir, id, "instructions.bin");
    asprintf(&result->op_filename, "%s.%s-%s", basedir, id, "operands.bin");
    asprintf(&result->reg_filename, "%s.%s-%s", basedir, id, "registers.bin");
    asprintf(&result->tp_filename, "%s.%s-%s", basedir, id, "types.bin");

    free(basedir);

    return result;

 gasn_base_error:

    g_object_unref(G_OBJECT(result));

    free(basedir);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à consulter.                          *
*                                                                             *
*  Description : Indique le chemin d'accès à l'archive finale.                *
*                                                                             *
*  Retour      : Nom de fichier à libérer, ou NULL en cas d'erreur.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_asm_storage_get_archive_filename(const GAsmStorage *storage)
{
    char *result;                           /* Chemin d'accès à retourner  */
    char *suffix;                           /* Fin du nom de fichier       */

    suffix = strdup("chrysalide");
    suffix = stradd(suffix, G_DIR_SEPARATOR_S);
    suffix = stradd(suffix, "cache");
    suffix = stradd(suffix, G_DIR_SEPARATOR_S);
    suffix = stradd(suffix, storage->id);
    suffix = stradd(suffix, ".idb.tar.xz");

    result = get_xdg_config_dir(suffix);

    free(suffix);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à consulter.                          *
*                                                                             *
*  Description : Détermine si un cache d'instructions complet existe.         *
*                                                                             *
*  Retour      : Bilan de la détermination.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_asm_storage_has_cache(const GAsmStorage *storage)
{
    bool result;                            /* Bilan à faire remonter      */
    char *filename;                         /* Chemin d'accès à l'archive  */
    int ret;                                /* Résultat d'un test d'accès  */

    filename = g_asm_storage_get_archive_filename(storage);

    ret = access(filename, R_OK);

    result = (ret == 0);

    free(filename);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à manipuler.                          *
*                                                                             *
*  Description : Décompresse les fichiers de cache d'instructions.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_asm_storage_decompress(const GAsmStorage *storage)
{
    bool result;                            /* Bilan à retourner           */
    char *filename;                         /* Chemin d'accès à l'archive  */
    struct archive *in;                     /* Archive à consulter         */
    int ret;                                /* Bilan d'un appel            */
    struct archive_entry *entry;            /* Elément de l'archive        */
    const char *path;                       /* Désignation d'un fichier    */

    result = false;

    filename = g_asm_storage_get_archive_filename(storage);

    in = archive_read_new();
    archive_read_support_filter_all(in);
    archive_read_support_format_all(in);

    ret = archive_read_open_filename(in, filename, 10240 /* ?! */);
    if (ret != ARCHIVE_OK) goto gasd_bad_archive;

    for (ret = archive_read_next_header(in, &entry);
         ret == ARCHIVE_OK;
         ret = archive_read_next_header(in, &entry))
    {
        path = archive_entry_pathname(entry);

        if (strcmp(path, "index.bin") == 0)
        {
            if (!dump_archive_entry_into_file(in, entry, storage->idx_filename))
                goto gasd_exit;
        }
        else if (strcmp(path, "instructions.bin") == 0)
        {
            if (!dump_archive_entry_into_file(in, entry, storage->ins_filename))
                goto gasd_exit;
        }
        else if (strcmp(path, "operands.bin") == 0)
        {
            if (!dump_archive_entry_into_file(in, entry, storage->op_filename))
                goto gasd_exit;
        }
        else if (strcmp(path, "registers.bin") == 0)
        {
            if (!dump_archive_entry_into_file(in, entry, storage->reg_filename))
                goto gasd_exit;
        }
        else if (strcmp(path, "types.bin") == 0)
        {
            if (!dump_archive_entry_into_file(in, entry, storage->tp_filename))
                goto gasd_exit;
        }

    }

    if (ret != ARCHIVE_EOF)
        goto gasd_exit;

    result = true;

 gasd_exit:

 gasd_bad_archive:

    archive_read_close(in);
    archive_read_free(in);

    free(filename);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à manipuler.                          *
*                                                                             *
*  Description : Compresse les fichiers de cache d'instructions.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_asm_storage_compress(const GAsmStorage *storage)
{
    bool result;                            /* Bilan à retourner           */
    char *filename;                         /* Chemin d'accès à l'archive  */
    struct archive *out;                    /* Archive à constituer        */
    int ret;                                /* Bilan d'une création        */
    CPError status;                         /* Bilan d'une compression     */

    result = false;

    filename = g_asm_storage_get_archive_filename(storage);

    out = archive_write_new();
    archive_write_add_filter_xz(out);
    archive_write_set_format_gnutar(out);

    ret = archive_write_open_filename(out, filename);
    if (ret != ARCHIVE_OK) goto gasc_exit;

    status = add_file_into_archive(out, storage->idx_filename, "index.bin");
    if (status != CPE_NO_ERROR) goto gasc_exit;

    status = add_file_into_archive(out, storage->ins_filename, "instructions.bin");
    if (status != CPE_NO_ERROR) goto gasc_exit;

    status = add_file_into_archive(out, storage->op_filename, "operands.bin");
    if (status != CPE_NO_ERROR) goto gasc_exit;

    status = add_file_into_archive(out, storage->reg_filename, "registers.bin");
    if (status != CPE_NO_ERROR) goto gasc_exit;

    status = add_file_into_archive(out, storage->tp_filename, "types.bin");
    if (status != CPE_NO_ERROR) goto gasc_exit;

    result = true;

 gasc_exit:

    archive_write_close(out);
    archive_write_free(out);

    free(filename);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à compléter.                          *
*                                                                             *
*  Description : Apprend tous les types mémorisés dans un fichier.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_asm_storage_read_types(GAsmStorage *storage)
{
    bool result;                            /* Bilan à enregistrer         */
    packed_buffer_t pbuf;                   /* Tampon des données à lire   */
    size_t i;                               /* Boucle de parcours          */
    unsigned char len;                      /* Taille d'un nom de type     */
    char *name;                             /* Désignation d'un type       */

    init_packed_buffer(&pbuf);

    result = read_packed_buffer(&pbuf, storage->tp_fd);

    if (result)
    {
        g_mutex_lock(&storage->gtp_mutex);

        result = extract_packed_buffer(&pbuf, &storage->gtp_count, sizeof(size_t), true);

        if (result)
            storage->gtypes = (gtype_ref_info_t *)calloc(storage->gtp_count, sizeof(gtype_ref_info_t));

        for (i = 0; i < storage->gtp_count && result; i++)
        {
            result = extract_packed_buffer(&pbuf, &len, sizeof(unsigned char), false);

            if (result)
            {
                name = (char *)malloc(len);

                result = extract_packed_buffer(&pbuf, name, len, false);

                if (result)
                {
                    storage->gtypes[i].gtype = g_type_from_name(name);
                    result = (storage->gtypes[i].gtype != 0);

                    if (!result)
                        log_variadic_message(LMT_ERROR, "Unknown type: '%s'", name);

                }

                if (result)
                    storage->gtypes[i].gclass = g_type_class_ref(storage->gtypes[i].gtype);

                free(name);

            }

        }

        g_mutex_unlock(&storage->gtp_mutex);

    }

    exit_packed_buffer(&pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à manipuler.                          *
*                pbuf    = zone tampon à venir lire.                          *
*                                                                             *
*  Description : Crée une nouvelle instance d'objet à partir de son type.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GObject *g_asm_storage_create_object(GAsmStorage *storage, packed_buffer_t *pbuf)
{
    GObject *result;                        /* Nouvelle instance à renvoyer*/
    size_t index;                           /* Indice du point d'insertion */
    bool status;                            /* Bilan d'une récupération    */

    result = NULL;

    status = extract_packed_buffer(pbuf, &index, sizeof(size_t), true);

    if (status)
    {
        g_mutex_lock(&storage->gtp_mutex);

        if (index < storage->gtp_count)
            result = g_object_new(storage->gtypes[index].gtype, NULL);

        g_mutex_unlock(&storage->gtp_mutex);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à manipuler.                          *
*                obj     = instance dont le type est à mémoriser.             *
*                pbuf    = zone tampon à remplir.                             *
*                                                                             *
*  Description : Sauvegarde le type d'un objet instancié.                     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_asm_storage_store_object_gtype(GAsmStorage *storage, GObject *obj, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GType gtype;                            /* Type à enregistrer          */
    size_t index;                           /* Indice du point d'insertion */

    gtype = G_TYPE_FROM_INSTANCE(obj);

    /**
     * Pour quelques explications sur l'esquive suivante, se rapporter aux
     * commentaires de g_target_operand_unserialize().
     *
     * Dans la situation présente, on ne doit pas enregistrer le type dans le tampon,
     * car l'opérande va relancer l'opération entière (avec un opérande temporaire),
     * ce qui conduirait à l'enregistrement de deux types successifs dans les données.
     */

    if (gtype == G_TYPE_TARGET_OPERAND)
        result = true;

    else
    {
        g_mutex_lock(&storage->gtp_mutex);

        for (index = 0; index < storage->gtp_count; index++)
            if (storage->gtypes[index].gtype == gtype)
                break;

        if (index == storage->gtp_count)
        {
            storage->gtypes = (gtype_ref_info_t *)realloc(storage->gtypes,
                                                          ++storage->gtp_count * sizeof(gtype_ref_info_t));

            assert(storage->gtp_count > 0);

            storage->gtypes[index].gtype = gtype;
            storage->gtypes[index].gclass = g_type_class_ref(gtype);

        }

        g_mutex_unlock(&storage->gtp_mutex);

        result = extend_packed_buffer(pbuf, &index, sizeof(size_t), true);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à consulter.                          *
*                                                                             *
*  Description : Enregistre tous les types mémorisés dans un fichier.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_asm_storage_write_types(GAsmStorage *storage)
{
    bool result;                            /* Bilan à enregistrer         */
    packed_buffer_t pbuf;                   /* Tampon des données à écrire */
    size_t i;                               /* Boucle de parcours          */
    const gchar *name;                      /* Désignation d'un type       */
    size_t len;                             /* Taille de ce nom            */

    init_packed_buffer(&pbuf);

    g_mutex_lock(&storage->gtp_mutex);

    result = extend_packed_buffer(&pbuf, &storage->gtp_count, sizeof(size_t), true);

    for (i = 0; i < storage->gtp_count && result; i++)
    {
        name = g_type_name(storage->gtypes[i].gtype);
        len = strlen(name) + 1;

        if (len > (2 << (sizeof(unsigned char) * 8 - 1)))
        {
            log_variadic_message(LMT_ERROR, "Type name too long: '%s' (%zu bytes)", name, len);
            result = false;
            break;
        }

        result = extend_packed_buffer(&pbuf, (unsigned char []) { len }, sizeof(unsigned char), false);

        if (result)
            result = extend_packed_buffer(&pbuf, name, len, false);

    }

    if (result)
        result = write_packed_buffer(&pbuf, storage->tp_fd);

    g_mutex_unlock(&storage->gtp_mutex);

    exit_packed_buffer(&pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à manipuler.                          *
*                type    = type du fichier de destination.                    *
*                pbuf    = zone tampon à remplir.                             *
*                pos     = tête de lecture avant écriture.                    *
*                                                                             *
*  Description : Charge des données rassemblées.                              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _g_asm_storage_load_data(const GAsmStorage *storage, StorageFileType type, packed_buffer_t *pbuf, off64_t pos)
{
    bool result;                            /* Bilan à retourner           */
    int fd;                                 /* Flux ciblé                  */
    off64_t new;                            /* Nouvelle position de lecture*/

    switch (type)
    {
        case SFT_INSTRUCTION:
            fd = storage->ins_fd;
            break;
        case SFT_OPERAND:
            fd = storage->op_fd;
            break;
        case SFT_REGISTER:
            fd = storage->reg_fd;
            break;
        default:
            fd = -1;
            break;
    }

    if (fd == -1)
    {
        result = false;
        goto type_error;
    }

    new = lseek64(fd, pos, SEEK_SET);

    if (new != pos)
        result = false;

    else
    {
        reset_packed_buffer(pbuf);
        result = read_packed_buffer(pbuf, fd);
    }

 type_error:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à manipuler.                          *
*                type    = type du fichier de destination.                    *
*                pbuf    = zone tampon à lire.                                *
*                pos     = tête de lecture avant écriture. [OUT]              *
*                                                                             *
*  Description : Sauvegarde des données rassemblées.                          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _g_asm_storage_store_data(const GAsmStorage *storage, StorageFileType type, packed_buffer_t *pbuf, off64_t *pos)
{
    bool result;                            /* Bilan à retourner           */
    int fd;                                 /* Flux ciblé                  */

    switch (type)
    {
        case SFT_INSTRUCTION:
            fd = storage->ins_fd;
            break;
        case SFT_OPERAND:
            fd = storage->op_fd;
            break;
        case SFT_REGISTER:
            fd = storage->reg_fd;
            break;
        default:
            fd = -1;
            break;
    }

    if (fd == -1)
    {
        result = false;
        goto type_error;
    }

    *pos = lseek64(fd, 0, SEEK_CUR);

    if (*pos == (off64_t)-1)
        result = false;

    else
    {
        result = write_packed_buffer(pbuf, fd);
        reset_packed_buffer(pbuf);
    }

 type_error:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à manipuler.                          *
*                flags   = options d'ouverture supplémentaires.               *
*                                                                             *
*  Description : Ouvre tous les fichiers nécessaires à une opération.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_asm_storage_open_files(GAsmStorage *storage, int flags)
{
    bool result;                            /* Bilan à retourner           */

#define open_file(filename, fd)                             \
    ({                                                      \
        bool __status;                                      \
        fd = open(filename, flags | O_LARGEFILE, 0600);     \
        if (fd == -1)                                       \
        {                                                   \
            perror("open");                                 \
            __status = false;                               \
        }                                                   \
        else                                                \
            __status = true;                                \
        __status;                                           \
    })

    result = open_file(storage->idx_filename, storage->idx_fd);

    if (result)
        result = open_file(storage->ins_filename, storage->ins_fd);

    if (result)
        result = open_file(storage->op_filename, storage->op_fd);

    if (result)
        result = open_file(storage->reg_filename, storage->reg_fd);

    if (result)
        result = open_file(storage->tp_filename, storage->tp_fd);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à manipuler.                          *
*                format  = format binaire chargé associé à l'architecture.    *
*                gid     = groupe de travail dédié.                           *
*                                                                             *
*  Description : Lance une restauration complète d'unsauvegarde compressée.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_asm_storage_open(GAsmStorage *storage, GBinFormat *format, wgroup_id_t gid)
{
    bool result;                            /* Bilan à retourner           */
    GInsCaching *caching;                   /* Tâche à faire exécuter      */
    GWorkQueue *queue;                      /* Gestionnaire des tâches     */
    GArchInstruction **list;                /* Instructions rechargées     */
    size_t i;                               /* Boucle de parcours #1       */
    size_t k;                               /* Boucle de parcours #2       */

    result = g_asm_storage_decompress(storage);

    if (result)
        result = g_asm_storage_open_files(storage, O_RDONLY);

    if (result)
        result = g_asm_storage_read_types(storage);

    if (result)
    {
        storage->length = lseek64(storage->idx_fd, 0, SEEK_END);

        if (storage->length == (off64_t)-1)
        {
            perror("lseek64");
            result = false;
            goto gaso_exit;
        }

        result = (storage->length % sizeof(off64_t) == 0);

        storage->length /= sizeof(off64_t);

    }

    if (!result)
    {
        log_simple_message(LMT_ERROR, "Instruction cache seems corrupted...");
        goto gaso_exit;
    }

    storage->collected = (GArchInstruction **)calloc(storage->length, sizeof(GArchInstruction *));

    /**
     * Cette méthode ne peut être appelée que pour un objet construit
     * à partir du constructeur g_asm_storage_new_compressed().
     */
    assert(storage->proc != NULL);

    caching = g_ins_caching_new(storage->proc, storage, format);
    g_object_ref(G_OBJECT(caching));

    queue = get_work_queue();

    g_work_queue_schedule_work(queue, G_DELAYED_WORK(caching), gid);

    g_work_queue_wait_for_completion(queue, gid);

    result = g_ins_caching_get_status(caching);

    g_object_unref(G_OBJECT(caching));


    if (result)
    {
        log_simple_message(LMT_INFO, "Successfully restored all instructions from cache!");

        list = (GArchInstruction **)malloc(storage->count * sizeof(GArchInstruction *));

        for (i = 0, k = 0; i < storage->length; i++)
            if (storage->collected[i] != NULL)
            {
                list[k] = storage->collected[i];
                g_object_ref(G_OBJECT(list[k++]));
            }

        assert(k == storage->count);

        g_arch_processor_set_instructions(storage->proc, list, storage->count);

    }

    else
        log_simple_message(LMT_ERROR, "Failed to restore all instructions from cache!");

 gaso_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à manipuler.                          *
*                format  = format binaire chargé associé à l'architecture.    *
*                index   = position physique de l'instruction recherchée.     *
*                pbuf    = tampon de lecture à disposition pour l'opération.  *
*                                                                             *
*  Description : Fournit l'instruction correspondant à une position indicée.  *
*                                                                             *
*  Retour      : Instruction rechargée ou NULL en cas d'erreur.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchInstruction *g_asm_storage_get_instruction_at(GAsmStorage *storage, GBinFormat *format, off64_t index, packed_buffer_t *pbuf)
{
    GArchInstruction *result;               /* Instruction à renvoyer      */
    off64_t pos;                            /* Position dans le cache      */
    off64_t new;                            /* Nouvelle position de lecture*/
    off64_t target;                         /* Emplacement du cache ciblé  */
    bool status;                            /* Bilan d'une lecture         */
#ifndef NDEBUG
    const mrange_t *irange;                 /* Emplacement de l'instruction*/
#endif

    assert(index < storage->length);

    pos = index * sizeof(off64_t);

    if (storage->collected[index] == NULL)
    {
        new = lseek64(storage->idx_fd, pos, SEEK_SET);

        if (new == pos)
        {
            status = safe_read(storage->idx_fd, &target, sizeof(off64_t));

            if (status)
                status = g_asm_storage_load_instruction_data(storage, pbuf, target);

            if (status)
                storage->collected[index] = NULL;//g_arch_instruction_load__old(storage, format, pbuf);

            if (storage->collected[index] != NULL)
            {
                storage->count++;

#ifndef NDEBUG
                irange = g_arch_instruction_get_range(storage->collected[index]);

                assert(index == get_phy_addr(get_mrange_addr(irange)));
#endif

            }

        }

    }

    result = storage->collected[index];

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : storage = gestionnaire à manipuler.                          *
*                                                                             *
*  Description : Programme une sauvegarde complète et compressée.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_asm_storage_save(GAsmStorage *storage)
{
    bool status;                            /* Statut des préparatifs      */
    GInsCaching *caching;                   /* Tâche à faire exécuter      */
    GWorkQueue *queue;                      /* Gestionnaire des tâches     */

    status = g_asm_storage_open_files(storage, O_WRONLY | O_CREAT | O_TRUNC);

    if (!status)
        log_simple_message(LMT_ERROR, "Unable to setup files for instructions caching!");

    else
    {
        /**
         * Cette méthode ne peut être appelée que pour un objet construit
         * à partir du constructeur g_asm_storage_new_compressed().
         */
        assert(storage->proc != NULL);

        caching = g_ins_caching_new(storage->proc, storage, NULL);

        g_signal_connect(caching, "work-completed", G_CALLBACK(on_cache_saving_completed), storage);

        queue = get_work_queue();

        g_work_queue_schedule_work(queue, G_DELAYED_WORK(caching), STORAGE_WORK_GROUP);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : caching = tâche de sauvegarde menée à son terme.             *
*                storage = gestionnaire de conservation à la réception.       *
*                                                                             *
*  Description : Acquitte la fin d'une tâche de sauvegarde complète.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_cache_saving_completed(GInsCaching *caching, GAsmStorage *storage)
{
    bool status;                            /* Bilan des enregistrements   */

    status = g_ins_caching_get_status(caching);

    if (status)
        log_simple_message(LMT_INFO, "Successfully cached all instructions!");
    else
        log_simple_message(LMT_ERROR, "Failed to cache all instructions!");

    if (status)
        status = g_asm_storage_write_types(storage);

    if (status)
    {
        status = g_asm_storage_compress(storage);

        if (!status)
            log_simple_message(LMT_ERROR, "Failed to compress instruction cache!");

    }

    g_signal_emit_by_name(storage, "saved");

}
