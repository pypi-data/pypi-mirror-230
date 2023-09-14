
/* Chrysalide - Outil d'analyse de fichiers binaires
 * switcher.c - gestion des basculements d'affichage d'opérandes numériques
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#include "switcher.h"


#include <assert.h>
#include <stdio.h>
#include <sys/socket.h>


#include <i18n.h>


#include "../collection-int.h"
#include "../item-int.h"
#include "../../../glibext/gbinarycursor.h"



/* --------------------- ELABORATION D'UN ELEMENT DE COLLECTION --------------------- */


/* Bascule d'affichage pour un opérande numérique (instance) */
struct _GDbSwitcher
{
    GDbItem parent;                         /* A laisser en premier        */

    vmpa2t addr;                            /* Adresse de l'instruction    */
    rle_string path;                        /* Chemin vers l'opérande visé */

    ImmOperandDisplay display;              /* Type de bascule             */

};

/* Bascule d'affichage pour un opérande numérique (classe) */
struct _GDbSwitcherClass
{
    GDbItemClass parent;                    /* A laisser en premier        */

};



/* Initialise la classe des bascules d'affichage numérique. */
static void g_db_switcher_class_init(GDbSwitcherClass *);

/* Initialise une bascule d'affichage pour opérande numérique. */
static void g_db_switcher_init(GDbSwitcher *);

/* Supprime toutes les références externes. */
static void g_db_switcher_dispose(GDbSwitcher *);

/* Procède à la libération totale de la mémoire. */
static void g_db_switcher_finalize(GDbSwitcher *);

/* Calcule le condensat associé à l'élément vu comme clef. */
static guint g_db_switcher_hash_key(const GDbSwitcher *);

/* Compare deux éléments en tant que clefs. */
static gboolean g_db_switcher_cmp_key(const GDbSwitcher *, const GDbSwitcher *);

/* Effectue la comparaison entre deux signets de collection. */
static gint g_db_switcher_cmp(const GDbSwitcher *, const GDbSwitcher *);

/* Importe la définition d'un signet depuis un flux réseau. */
static bool g_db_switcher_unpack(GDbSwitcher *, packed_buffer_t *);

/* Exporte la définition d'un signet dans un flux réseau. */
static bool g_db_switcher_pack(const GDbSwitcher *, packed_buffer_t *);

/* Construit la description humaine d'un signet sur un tampon. */
static char *g_db_switcher_build_label(GDbSwitcher *);

/* Exécute une bascule d'affichage d'opérande sur un binaire. */
static bool g_db_switcher_run(GDbSwitcher *, GLoadedBinary *, ImmOperandDisplay);

/* Applique une bascule d'affichage d'opérande sur un binaire. */
static bool g_db_switcher_apply(GDbSwitcher *, GLoadedBinary *);

/* Annule une bascule d'affichage d'opérande sur un binaire. */
static bool g_db_switcher_cancel(GDbSwitcher *, GLoadedBinary *);

/* Charge les valeurs utiles pour un basculement d'affichage. */
static bool g_db_switcher_load(GDbSwitcher *, const bound_value *, size_t);

/* Constitue les champs destinés à une insertion / modification. */
static bool g_db_switcher_store(const GDbSwitcher *, bound_value **, size_t *);



/* ---------------------- DEFINITION DE LA COLLECTION ASSOCIEE ---------------------- */


/* Collection dédiée aux basculements d'affichage (instance) */
struct _GSwitcherCollection
{
    GDbCollection parent;                   /* A laisser en premier        */

};

/* Collection dédiée aux basculements d'affichage (classe) */
struct _GSwitcherCollectionClass
{
    GDbCollectionClass parent;              /* A laisser en premier        */

};


/* Initialise la classe des signets dans une zone de texte. */
static void g_switcher_collection_class_init(GSwitcherCollectionClass *);

/* Initialise un signet dans une zone de texte. */
static void g_switcher_collection_init(GSwitcherCollection *);

/* Supprime toutes les références externes. */
static void g_switcher_collection_dispose(GSwitcherCollection *);

/* Procède à la libération totale de la mémoire. */
static void g_switcher_collection_finalize(GSwitcherCollection *);

/* Crée la table des basculements dans une base de données. */
static bool g_switcher_collection_create_db_table(const GSwitcherCollection *, sqlite3 *);



/* ---------------------------------------------------------------------------------- */
/*                       ELABORATION D'UN ELEMENT DE COLLECTION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un signet à l'intérieur d'une zone de texte. */
G_DEFINE_TYPE(GDbSwitcher, g_db_switcher, G_TYPE_DB_ITEM);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des bascules d'affichage numérique.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_switcher_class_init(GDbSwitcherClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDbItemClass *item;                     /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_db_switcher_dispose;
    object->finalize = (GObjectFinalizeFunc)g_db_switcher_finalize;

    item = G_DB_ITEM_CLASS(klass);

    item->feature = DBF_DISPLAY_SWITCHERS;

    item->hash_key = (hash_db_item_key_fc)g_db_switcher_hash_key;
    item->cmp_key = (cmp_db_item_key_fc)g_db_switcher_cmp_key;
    item->cmp = (cmp_db_item_fc)g_db_switcher_cmp;

    item->unpack = (unpack_db_item_fc)g_db_switcher_unpack;
    item->pack = (pack_db_item_fc)g_db_switcher_pack;

    item->build_label = (build_item_label_fc)g_db_switcher_build_label;
    item->apply = (run_item_fc)g_db_switcher_apply;
    item->cancel = (run_item_fc)g_db_switcher_cancel;

    item->load = (load_db_item_fc)g_db_switcher_load;
    item->store = (store_db_item_fc)g_db_switcher_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = instance à initialiser.                           *
*                                                                             *
*  Description : Initialise une bascule d'affichage pour opérande numérique.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_switcher_init(GDbSwitcher *switcher)
{
    init_vmpa(&switcher->addr, VMPA_NO_PHYSICAL, VMPA_NO_VIRTUAL);

    setup_empty_rle_string(&switcher->path);

    switcher->display = IOD_COUNT;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_switcher_dispose(GDbSwitcher *switcher)
{
    G_OBJECT_CLASS(g_db_switcher_parent_class)->dispose(G_OBJECT(switcher));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = instance d'objet GLib à traiter.                  *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_switcher_finalize(GDbSwitcher *switcher)
{
    exit_rle_string(&switcher->path);

    G_OBJECT_CLASS(g_db_switcher_parent_class)->finalize(G_OBJECT(switcher));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : instr   = instruction contenant l'opérande à traiter.        *
*                imm     = opérande de valeur immédiate concernée.            *
*                display = forme d'affichage à établir pour l'opérande.       *
*                                                                             *
*  Description : Crée une définition de bascule d'affichage pour un immédiat. *
*                                                                             *
*  Retour      : Bascule mise en place ou NULL en cas d'erreur.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbSwitcher *g_db_switcher_new(GArchInstruction *instr, const GImmOperand *imm, ImmOperandDisplay display)
{
    GDbSwitcher *result;                    /* Instance à retourner        */
    bool status;                            /* Bilan de l'initialisation   */

    result = g_object_new(G_TYPE_DB_SWITCHER, NULL);

    status = g_db_switcher_fill(result, instr, imm, display);
    if (!status) goto error;

    return result;

 error:

    g_object_unref(G_OBJECT(result));

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = bascule à initialiser.                            *
*                instr    = instruction contenant l'opérande à traiter.       *
*                imm      = opérande de valeur immédiate concerné.            *
*                display  = forme d'affichage à établir pour l'opérande.      *
*                                                                             *
*  Description : Initialise la définition de bascule d'affichage.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_switcher_fill(GDbSwitcher *switcher, GArchInstruction *instr, const GImmOperand *imm, ImmOperandDisplay display)
{
    bool result;                            /* Bilan à retourner           */
    char *path;                             /* Chemin vers l'opérande visé */
    const mrange_t *range;                  /* Localisation de l'instruct° */

    /**
     * Cette fonction est principalement destinée aux initialisations
     * depuis l'extension Python.
     */

    result = false;

    /* Recherche de la position de l'opérande */

    path = g_arch_instruction_find_operand_path(instr, G_ARCH_OPERAND(imm));

    if (path == NULL)
        goto failure;

    /* Sauvegarde des propriétés */

    range = g_arch_instruction_get_range(instr);
    copy_vmpa(&switcher->addr, get_mrange_addr(range));

    dup_into_rle_string(&switcher->path, path);
    free(path);

    switcher->display = display;

    result = true;

 failure:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = élément de collection à consulter.                *
*                                                                             *
*  Description : Calcule le condensat associé à l'élément vu comme clef.      *
*                                                                             *
*  Retour      : Condensat associé à l'élément.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint g_db_switcher_hash_key(const GDbSwitcher *switcher)
{
    guint result;                           /* Valeur "unique" à renvoyer  */

    result = hash_vmpa(&switcher->addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier élément de collection à consulter.               *
*                b = second élément de collection à consulter.                *
*                                                                             *
*  Description : Compare deux éléments en tant que clefs.                     *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean g_db_switcher_cmp_key(const GDbSwitcher *a, const GDbSwitcher *b)
{
    gboolean result;                        /* Bilan à retourner           */
    int ret;                                /* Bilan intermédiaire         */

    ret = cmp_vmpa(&a->addr, &b->addr);

    result = (ret == 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier élément à analyser.                              *
*                b = second élément à analyser.                               *
*                                                                             *
*  Description : Effectue la comparaison entre deux signets de collection.    *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gint g_db_switcher_cmp(const GDbSwitcher *a, const GDbSwitcher *b)
{
    gint result;                            /* Bilan de la comparaison     */

    result = cmp_vmpa(&a->addr, &b->addr);

    if (result == 0)
        result = cmp_rle_string(&a->path, &b->path);

    if (result == 0)
    {
        if (a->display < b->display)
            result = -1;

        else if (a->display > b->display)
            result = 1;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = bascule d'affichage aux infos à charger. [OUT]    *
*                pbuf     = paquet de données où venir inscrire les infos.    *
*                                                                             *
*  Description : Importe la définition d'un signet depuis un flux réseau.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_switcher_unpack(GDbSwitcher *switcher, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uint32_t tmp32;                         /* Valeur sur 32 bits          */

    result = G_DB_ITEM_CLASS(g_db_switcher_parent_class)->unpack(G_DB_ITEM(switcher), pbuf);

    if (result)
        result = unpack_vmpa(&switcher->addr, pbuf);

    if (result)
        result = unpack_rle_string(&switcher->path, pbuf);

    if (result)
    {
        result = extract_packed_buffer(pbuf, &tmp32, sizeof(uint32_t), true);
        switcher->display = tmp32;

        if (switcher->display > IOD_COUNT)
            result = false;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = bascule d'affichage aux infos à sauvegarder.      *
*                pbuf     = paquet de données où venir inscrire les infos.    *
*                                                                             *
*  Description : Exporte la définition d'une bascule d'affichage d'opérande.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_switcher_pack(const GDbSwitcher *switcher, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = G_DB_ITEM_CLASS(g_db_switcher_parent_class)->pack(G_DB_ITEM(switcher), pbuf);

    if (result)
        result = pack_vmpa(&switcher->addr, pbuf);

    if (result)
        result = pack_rle_string(&switcher->path, pbuf);

    if (result)
        result = extend_packed_buffer(pbuf, (uint32_t []) { switcher->display }, sizeof(uint32_t), true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = bascule d'affichage à manipuler.                  *
*                                                                             *
*  Description : Construit la description humaine d'un signet sur un tampon.  *
*                                                                             *
*  Retour      : Description humaine mise en place à libérer après usage.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_db_switcher_build_label(GDbSwitcher *switcher)
{
    char *result;                           /* Description à retourner     */
    VMPA_BUFFER(loc);                       /* Indication de position      */

    vmpa2_to_string(&switcher->addr, MDS_UNDEFINED, loc, NULL);

    switch (switcher->display)
    {
        case IOD_BIN:
            asprintf(&result, _("Switch to binary display at %s"), loc);
            break;
        case IOD_OCT:
            asprintf(&result, _("Switch to octal display at %s"), loc);
            break;
        case IOD_DEC:
            asprintf(&result, _("Switch to octal display at %s"), loc);
            break;
        case IOD_HEX:
            asprintf(&result, _("Switch to octal display at %s"), loc);
            break;
        case IOD_COUNT:
            asprintf(&result, _("Reset to default display at %s"), loc);
            break;
        default:
            assert(false);
            result = NULL;
            break;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = bascule d'affichage à manipuler.                  *
*                binary   = binaire chargé en mémoire à modifier.             *
*                new      = nouvel état à appliquer.                          *
*                                                                             *
*  Description : Exécute une bascule d'affichage d'opérande sur un binaire.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_switcher_run(GDbSwitcher *switcher, GLoadedBinary *binary, ImmOperandDisplay new)
{
    bool result;                            /* Bilan à faire remonter      */
    GArchProcessor *proc;                   /* Propriétaire d'instructions */
    GArchInstruction *instr;                /* Instruction à traiter       */
    GArchOperand *op;                       /* Opérande à modifier         */
    GImmOperand *operand;                   /* Opérande de valeur immédiate*/
    GBufferCache *cache;                    /* Tampon de lignes à traiter  */
    GLineCursor *cursor;                    /* Emplacement dans un tampon  */
    size_t index;                           /* Indice de ligne à traiter   */

    result = false;

    /* Traitement au niveau des instructions */

    proc = g_loaded_binary_get_processor(binary);

    instr = g_arch_processor_find_instr_by_address(proc, &switcher->addr);
    if (instr == NULL) goto exit_instr;

    op = g_arch_instruction_get_operand_from_path(instr, get_rle_string(&switcher->path));
    if (op == NULL) goto exit_without_operand;

    result = G_IS_IMM_OPERAND(op);
    if (!result) goto exit_operand;

    operand = G_IMM_OPERAND(op);

    if (new == IOD_COUNT)
        new = g_imm_operand_get_default_display(operand);

    g_imm_operand_set_display(operand, new);

    /* Traitement au niveau du rendu graphique */

    cache = g_loaded_binary_get_disassembly_cache(binary);
    if (cache == NULL) goto exit_operand;

    cursor = g_binary_cursor_new();
    g_binary_cursor_update(G_BINARY_CURSOR(cursor), &switcher->addr);

    g_buffer_cache_wlock(cache);

    index = g_buffer_cache_find_index_by_cursor(cache, cursor, true);

    g_object_unref(G_OBJECT(cursor));

    index = g_buffer_cache_look_for_flag(cache, index, BLF_HAS_CODE);

    if (index == g_buffer_cache_count_lines(cache))
        goto exit_gui;

    g_buffer_cache_refresh_line(cache, index);

    result = true;

    /* Phase de sortie propre */

 exit_gui:

    g_buffer_cache_wunlock(cache);

    g_object_unref(G_OBJECT(cache));

 exit_operand:

    g_object_unref(G_OBJECT(op));

 exit_without_operand:

    g_object_unref(G_OBJECT(instr));

 exit_instr:

    g_object_unref(G_OBJECT(proc));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = bascule d'affichage à manipuler.                  *
*                binary   = binaire chargé en mémoire à modifier.             *
*                                                                             *
*  Description : Applique une bascule d'affichage d'opérande sur un binaire.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_switcher_apply(GDbSwitcher *switcher, GLoadedBinary *binary)
{
    bool result;                            /* Bilan à faire remonter      */

    result = g_db_switcher_run(switcher, binary, switcher->display);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = bascule d'affichage à manipuler.                  *
*                binary   = binaire chargé en mémoire à modifier.             *
*                                                                             *
*  Description : Annule une bascule d'affichage d'opérande sur un binaire.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_switcher_cancel(GDbSwitcher *switcher, GLoadedBinary *binary)
{
    bool result;                            /* Bilan à faire remonter      */

    result = g_db_switcher_run(switcher, binary, IOD_COUNT);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = bascule d'affichage à charger depuis les réponses.*
*                values   = tableau d'éléments à consulter.                   *
*                count    = nombre de descriptions renseignées.               *
*                                                                             *
*  Description : Charge les valeurs utiles pour un basculement d'affichage.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_switcher_load(GDbSwitcher *switcher, const bound_value *values, size_t count)
{
    bool result;                            /* Bilan à faire remonter      */
    const bound_value *value;               /* Valeur à éditer / définir   */

    result = G_DB_ITEM_CLASS(g_db_switcher_parent_class)->load(G_DB_ITEM(switcher), values, count);

    if (result) result = load_vmpa(&switcher->addr, NULL, values, count);

    if (result) result = load_rle_string(&switcher->path, "path", values, count);

    if (result)
    {
        value = find_bound_value(values, count, "type");
        result = (value != NULL && value->type == SQLITE_INTEGER);

        if (result)
            switcher->display = value->integer;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = base d'éléments sur laquelle s'appuyer.           *
*                values   = couples de champs et de valeurs à lier. [OUT]     *
*                count    = nombre de ces couples. [OUT]                      *
*                                                                             *
*  Description : Constitue les champs destinés à une insertion / modification.*
*                                                                             *
*  Retour      : Etat du besoin en sauvegarde.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_switcher_store(const GDbSwitcher *switcher, bound_value **values, size_t *count)
{
    bool status;                            /* Bilan d'opération initiale  */
    bound_value *value;                     /* Valeur à éditer / définir   */

    if (switcher == NULL)
        status = G_DB_ITEM_CLASS(g_db_switcher_parent_class)->store(NULL, values, count);
    else
        status = G_DB_ITEM_CLASS(g_db_switcher_parent_class)->store(G_DB_ITEM(switcher), values, count);

    if (!status) return false;

    if (switcher == NULL)
        status = store_vmpa(NULL, NULL, values, count);
    else
        status = store_vmpa(&switcher->addr, NULL, values, count);

    if (!status) return false;

    if (switcher == NULL)
        status &= store_rle_string(NULL, "path", values, count);
    else
        status &= store_rle_string(&switcher->path, "path", values, count);

    *count += 1;
    *values = realloc(*values, *count * sizeof(bound_value));

    value = &(*values)[*count - 1];

    value->cname = "type";
    value->built_name = false;
    value->type = SQLITE_INTEGER;

    value->has_value = (switcher != NULL);

    if (value->has_value)
    {
        value->integer = switcher->display;
        value->delete = NULL;
    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = informations à consulter.                         *
*                                                                             *
*  Description : Fournit l'adresse associée à une bascule.                    *
*                                                                             *
*  Retour      : Adresse mémoire.                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const vmpa2t *g_db_switcher_get_address(const GDbSwitcher *switcher)
{
    const vmpa2t *result;                   /* Localisation à retourner    */

    result = &switcher->addr;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = informations à consulter.                         *
*                                                                             *
*  Description : Fournit le chemin menant vers l'opérande basculé.            *
*                                                                             *
*  Retour      : Chemin de type "n[:n:n:n]".                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_db_switcher_get_path(const GDbSwitcher *switcher)
{
    const char *result;                     /* Chemin à renvoyer           */

    result = get_rle_string(&switcher->path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : switcher = informations à consulter.                         *
*                                                                             *
*  Description : Indique l'affichage vers lequel un opérande a basculé.       *
*                                                                             *
*  Retour      : Type d'affichage forcé pour un opérande.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ImmOperandDisplay g_db_switcher_get_display(const GDbSwitcher *switcher)
{
    ImmOperandDisplay result;               /* Type d'affichage à retourner*/

    result = switcher->display;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                        DEFINITION DE LA COLLECTION ASSOCIEE                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une collection de basculements d'affichage. */
G_DEFINE_TYPE(GSwitcherCollection, g_switcher_collection, G_TYPE_DB_COLLECTION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des signets dans une zone de texte.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_switcher_collection_class_init(GSwitcherCollectionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDbCollectionClass *collec;             /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_switcher_collection_dispose;
    object->finalize = (GObjectFinalizeFunc)g_switcher_collection_finalize;

    collec = G_DB_COLLECTION_CLASS(klass);

    collec->create_table = (collec_create_db_table_fc)g_switcher_collection_create_db_table;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise un signet dans une zone de texte.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_switcher_collection_init(GSwitcherCollection *collec)
{
    G_DB_COLLECTION(collec)->featuring = DBF_DISPLAY_SWITCHERS;
    G_DB_COLLECTION(collec)->type = G_TYPE_DB_SWITCHER;
    G_DB_COLLECTION(collec)->name = "Switchers";

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_switcher_collection_dispose(GSwitcherCollection *collec)
{
    G_OBJECT_CLASS(g_switcher_collection_parent_class)->dispose(G_OBJECT(collec));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_switcher_collection_finalize(GSwitcherCollection *collec)
{
    G_OBJECT_CLASS(g_switcher_collection_parent_class)->finalize(G_OBJECT(collec));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une collection dédiée aux basculements d'affichage.     *
*                                                                             *
*  Retour      : Collection mise en place.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GSwitcherCollection *g_switcher_collection_new(void)
{
    GSwitcherCollection *result;            /* Instance à retourner        */

    result = g_object_new(G_TYPE_SWITCHER_COLLECTION, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments spectateur des opérations.      *
*                db     = accès à la base de données.                         *
*                                                                             *
*  Description : Crée la table des basculements dans une base de données.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_switcher_collection_create_db_table(const GSwitcherCollection *collec, sqlite3 *db)
{
    const char *sql;                        /* Patron de requête SQL       */
    char *addr_fields;                      /* Champs pour l'adresse       */
    char *request;                          /* Requête à exécuter          */
    char *msg;                              /* Message d'erreur            */
    int ret;                                /* Bilan de la création        */

    sql = "CREATE TABLE Switchers ("            \
             SQLITE_DB_ITEM_CREATE ", "         \
             "%s, "                             \
             SQLITE_RLESTR_CREATE("path") ","   \
             "type INTEGER"                     \
          ");";

    addr_fields = create_vmpa_db_table(NULL);

    asprintf(&request, sql, addr_fields);

    ret = sqlite3_exec(db, request, NULL, NULL, &msg);

    free(addr_fields);
    free(request);

    if (ret != SQLITE_OK)
    {
        fprintf(stderr, "sqlite3_exec(): %s\n", msg);
        sqlite3_free(msg);
    }

    return (ret == SQLITE_OK);

}
