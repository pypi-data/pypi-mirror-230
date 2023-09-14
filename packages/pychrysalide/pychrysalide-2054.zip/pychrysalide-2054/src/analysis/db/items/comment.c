
/* Chrysalide - Outil d'analyse de fichiers binaires
 * comment.c - gestion des commentaires dans du texte
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


#include "comment.h"


#include <assert.h>
#include <malloc.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>


#include <i18n.h>


#include "../collection-int.h"
#include "../item-int.h"
#include "../../human/asm/lang.h"
#include "../../../common/array.h"
#include "../../../common/extstr.h"
#include "../../../core/columns.h"
#include "../../../glibext/gbinarycursor.h"
#include "../../../glibext/linegen-int.h"



/* --------------------- ELABORATION D'UN ELEMENT DE COLLECTION --------------------- */


/* Commentaire à placer dans du texte quelconque (instance) */
struct _GDbComment
{
    GDbItem parent;                         /* A laisser en premier        */

    vmpa2t addr;                            /* Adresse du commentaire      */
    CommentEmbeddingType type;              /* Type d'incrustation         */
    BufferLineFlags flags;                  /* Identification de l'accroche*/

    flat_array_t *text;                     /* Contenu du commentaire      */

};

/* Commentaire à placer dans du texte quelconque (classe) */
struct _GDbCommentClass
{
    GDbItemClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des commentaires dans une zone de texte. */
static void g_db_comment_class_init(GDbCommentClass *);

/* Initialise un commentaire dans une zone de texte. */
static void g_db_comment_init(GDbComment *);

/* Supprime toutes les références externes. */
static void g_db_comment_dispose(GDbComment *);

/* Procède à la libération totale de la mémoire. */
static void g_db_comment_finalize(GDbComment *);

/* Constitue un ensemble de lignes pour un commentaire. */
static void g_db_comment_define_text_lines(GDbComment *, const char *);

/* Calcule le condensat associé à l'élément vu comme clef. */
static guint g_db_comment_hash_key(const GDbComment *);

/* Compare deux éléments en tant que clefs. */
static gboolean g_db_comment_cmp_key(const GDbComment *, const GDbComment *);

/* Effectue la comparaison entre deux commentaires enregistrés. */
static gint g_db_comment_cmp(const GDbComment *, const GDbComment *);

/* Importe la définition d'un commentaire dans un flux réseau. */
static bool g_db_comment_unpack(GDbComment *, packed_buffer_t *);

/* Exporte la définition d'un commentaire dans un flux réseau. */
static bool g_db_comment_pack(GDbComment *, packed_buffer_t *);

/* Construit la description humaine d'un commentaire. */
static char *g_db_comment_build_label(GDbComment *);

/* Exécute l'impression de commentaire dans du code de binaire. */
static bool g_db_comment_run(GDbComment *, GLoadedBinary *, bool);

/* Réalise l'impression de commentaire dans du code de binaire. */
static bool g_db_comment_apply(GDbComment *, GLoadedBinary *);

/* Annule l'impression d'un commentaire dans du code de binaire. */
static bool g_db_comment_cancel(GDbComment *, GLoadedBinary *);

/* Charge les valeurs utiles pour un commentaire. */
static bool g_db_comment_load(GDbComment *, const bound_value *, size_t);

/* Constitue les champs destinés à une insertion / modification. */
static bool g_db_comment_store(GDbComment *, bound_value **, size_t *);



/* ------------------------ OFFRE DE CAPACITES DE GENERATION ------------------------ */


/* Indique le nombre de ligne prêtes à être générées. */
static size_t g_db_comment_count_lines(GDbComment *);

/* Retrouve l'emplacement correspondant à une position donnée. */
static void g_db_comment_compute_cursor(const GDbComment *, gint, size_t, size_t, GLineCursor **);

/* Détermine si le conteneur s'inscrit dans une plage donnée. */
static int g_db_comment_contain_cursor(const GDbComment *, size_t, size_t, const GLineCursor *);

/* Renseigne sur les propriétés liées à un générateur. */
static BufferLineFlags g_db_comment_get_generator_flags(const GDbComment *, size_t, size_t);

/* Imprime dans une ligne de rendu le contenu représenté. */
static void g_db_comment_print(GDbComment *, GBufferLine *, size_t, size_t, const GBinContent *);



/* ---------------------- DEFINITION DE LA COLLECTION ASSOCIEE ---------------------- */


/* Collection dédiée aux commentaires textuels (instance) */
struct _GCommentCollection
{
    GDbCollection parent;                   /* A laisser en premier        */

};

/* Collection dédiée aux commentaires textuels (classe) */
struct _GCommentCollectionClass
{
    GDbCollectionClass parent;              /* A laisser en premier        */

};


/* Initialise la classe des commentaires sous forme de texte. */
static void g_comment_collection_class_init(GCommentCollectionClass *);

/* Initialise un commentaire sous forme de zone de texte. */
static void g_comment_collection_init(GCommentCollection *);

/* Procède à l'initialisation de l'interface de génération. */
static void g_db_comment_interface_init(GLineGeneratorInterface *);

/* Supprime toutes les références externes. */
static void g_comment_collection_dispose(GCommentCollection *);

/* Procède à la libération totale de la mémoire. */
static void g_comment_collection_finalize(GCommentCollection *);

/* Crée la table des commentaires dans une base de données. */
static bool g_comment_collection_create_db_table(const GCommentCollection *, sqlite3 *);



/* ---------------------------------------------------------------------------------- */
/*                       ELABORATION D'UN ELEMENT DE COLLECTION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un commentaire à l'intérieur d'une zone de texte. */
G_DEFINE_TYPE_WITH_CODE(GDbComment, g_db_comment, G_TYPE_DB_ITEM,
                        G_IMPLEMENT_INTERFACE(G_TYPE_LINE_GENERATOR, g_db_comment_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des commentaires dans une zone de texte.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_comment_class_init(GDbCommentClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDbItemClass *item;                     /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_db_comment_dispose;
    object->finalize = (GObjectFinalizeFunc)g_db_comment_finalize;

    item = G_DB_ITEM_CLASS(klass);

    item->feature = DBF_COMMENTS;

    item->hash_key = (hash_db_item_key_fc)g_db_comment_hash_key;
    item->cmp_key = (cmp_db_item_key_fc)g_db_comment_cmp_key;
    item->cmp = (cmp_db_item_fc)g_db_comment_cmp;

    item->unpack = (unpack_db_item_fc)g_db_comment_unpack;
    item->pack = (pack_db_item_fc)g_db_comment_pack;

    item->build_label = (build_item_label_fc)g_db_comment_build_label;
    item->apply = (run_item_fc)g_db_comment_apply;
    item->cancel = (run_item_fc)g_db_comment_cancel;

    item->load = (load_db_item_fc)g_db_comment_load;
    item->store = (store_db_item_fc)g_db_comment_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise un commentaire dans une zone de texte.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_comment_init(GDbComment *comment)
{
    init_vmpa(&comment->addr, VMPA_NO_PHYSICAL, VMPA_NO_VIRTUAL);

    comment->type = CET_COUNT;
    comment->flags = BLF_NONE;

    comment->text = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de génération.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_comment_interface_init(GLineGeneratorInterface *iface)
{
    iface->count = (linegen_count_lines_fc)g_db_comment_count_lines;
    iface->compute = (linegen_compute_fc)g_db_comment_compute_cursor;
    iface->contain = (linegen_contain_fc)g_db_comment_contain_cursor;
    iface->get_flags = (linegen_get_flags_fc)g_db_comment_get_generator_flags;
    iface->print = (linegen_print_fc)g_db_comment_print;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_comment_dispose(GDbComment *comment)
{
    G_OBJECT_CLASS(g_db_comment_parent_class)->dispose(G_OBJECT(comment));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_comment_finalize(GDbComment *comment)
{
    size_t count;                           /* Nombre d'éléments textuels  */
    size_t i;                               /* Boucle de parcours          */
    rle_string *string;                     /* Chaîne à traiter            */

    lock_flat_array(&comment->text);

    count = count_flat_array_items(comment->text);

    for (i = 0; i < count; i++)
    {
        string = get_flat_array_item(comment->text, 0, sizeof(rle_string));

        exit_rle_string(string);

        rem_item_from_flat_array(&comment->text, 0, sizeof(rle_string));

    }

    unlock_flat_array(&comment->text);

    G_OBJECT_CLASS(g_db_comment_parent_class)->finalize(G_OBJECT(comment));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr  = adresse inamovible localisant une position.          *
*                type  = type d'incrustation à respecter pour l'insertion.    *
*                flags = indentifiants supplémentaires de ligne visée.        *
*                text  = contenu textuel associé au commentaire ou NULL.      *
*                                                                             *
*  Description : Crée une définition de commentaire textuel.                  *
*                                                                             *
*  Retour      : Commentaire mis en place ou NULL en cas d'erreur.            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GDbComment *g_db_comment_new(const vmpa2t *addr, CommentEmbeddingType type, BufferLineFlags flags, const char *text)
{
    GDbComment *result;                     /* Instance à retourner        */
    bool status;                            /* Bilan de l'initialisation   */

    result = g_object_new(G_TYPE_DB_COMMENT, NULL);

    status = g_db_comment_fill(result, addr, type, flags, text);
    if (!status) goto error;

    return result;

 error:

    g_object_unref(G_OBJECT(result));

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr  = adresse inamovible localisant une position.          *
*                type  = type d'incrustation à respecter pour l'insertion.    *
*                flags = indentifiants supplémentaires de ligne visée.        *
*                text  = contenu textuel associé au commentaire ou NULL.      *
*                                                                             *
*  Description : Initialise la définition d'un commentaire à incruster.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_db_comment_fill(GDbComment *comment, const vmpa2t *addr, CommentEmbeddingType type, BufferLineFlags flags, const char *text)
{
    bool result;                            /* Bilan à retourner           */

    /**
     * Cette fonction est principalement destinée aux initialisations
     * depuis l'extension Python.
     */

    result = true;

    copy_vmpa(&comment->addr, addr);

    comment->type = type;
    comment->flags = flags;

    g_db_comment_define_text_lines(comment, text);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = commentaire dont les lignes sont à constituer.     *
*                text  = contenu textuel associé au commentaire ou NULL.      *
*                                                                             *
*  Description : Constitue un ensemble de lignes pour un commentaire.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_comment_define_text_lines(GDbComment *comment, const char *text)
{
    char *tmp;                              /* Zone de travail modifiable  */
    char **lines;                           /* Lignes du texte découpé     */
    size_t count;                           /* Quantité de ces lignes      */
    size_t i;                               /* Boucle de parcours          */
    rle_string string;                      /* Fragment de texte à ajouter */

    if (text != NULL)
    {
        tmp = strdup(text);

        tmp = strrpl(tmp, "\r", "");

        lines = strtoka(tmp, "\n", &count);

        lock_flat_array(&comment->text);

        for (i = 0; i < count; i++)
        {
            init_dynamic_rle_string(&string, lines[i]);

            add_item_to_flat_array(&comment->text, &string, sizeof(rle_string));

        }

        unlock_flat_array(&comment->text);

        free(lines);

        free(tmp);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = élément de collection à consulter.                 *
*                                                                             *
*  Description : Calcule le condensat associé à l'élément vu comme clef.      *
*                                                                             *
*  Retour      : Condensat associé à l'élément.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint g_db_comment_hash_key(const GDbComment *comment)
{
    guint result;                           /* Valeur "unique" à renvoyer  */

    result = hash_vmpa(&comment->addr);

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

static gboolean g_db_comment_cmp_key(const GDbComment *a, const GDbComment *b)
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
*  Description : Effectue la comparaison entre deux commentaires enregistrés. *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gint g_db_comment_cmp(const GDbComment *a, const GDbComment *b)
{
    gint result;                            /* Bilan de la comparaison     */
    char *string_a;                         /* Texte du commentaire A      */
    char *string_b;                         /* Texte du commentaire B      */

    result = cmp_vmpa_by_phy(&a->addr, &b->addr);

    if (result == 0)
    {
        string_a = g_db_comment_get_text((GDbComment *)a);
        string_b = g_db_comment_get_text((GDbComment *)b);

        if (string_a == NULL && string_b == NULL)
            result = 0;

        else if (string_a != NULL && string_b == NULL)
            result = 1;

        else if (string_a == NULL && string_b != NULL)
            result = -1;

        else
            result = strcmp(string_a, string_b);

        if (string_a != NULL) free(string_a);
        if (string_b != NULL) free(string_b);

    }

    return 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = commentaire avec informations sont à charger. [OUT]*
*                pbuf    = paquet de données où venir inscrire les infos.     *
*                                                                             *
*  Description : Importe la définition d'un commentaire dans un flux réseau.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_comment_unpack(GDbComment *comment, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uint8_t tmp8;                           /* Valeur sur 8 bits           */
    uint32_t tmp32;                         /* Valeur sur 32 bits          */
    rle_string text;                        /* Texte brut récupéré         */

    result = G_DB_ITEM_CLASS(g_db_comment_parent_class)->unpack(G_DB_ITEM(comment), pbuf);

    if (result)
        result = unpack_vmpa(&comment->addr, pbuf);

    if (result)
    {
        result = extract_packed_buffer(pbuf, &tmp8, sizeof(uint8_t), true);
        comment->type = tmp8;
    }

    if (result)
    {
        result = extract_packed_buffer(pbuf, &tmp32, sizeof(uint32_t), true);
        comment->flags = tmp32;
    }

    if (result)
    {
        setup_empty_rle_string(&text);
        result = unpack_rle_string(&text, pbuf);

        g_db_comment_define_text_lines(comment, get_rle_string(&text));

        exit_rle_string(&text);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = informations à sauvegarder.                        *
*                pbuf    = paquet de données où venir inscrire les infos.     *
*                                                                             *
*  Description : Exporte la définition d'un commentaire dans un flux réseau.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_comment_pack(GDbComment *comment, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    rle_string text;                        /* Texte brut récupéré         */

    result = G_DB_ITEM_CLASS(g_db_comment_parent_class)->pack(G_DB_ITEM(comment), pbuf);

    if (result)
        result = pack_vmpa(&comment->addr, pbuf);

    if (result)
        result = extend_packed_buffer(pbuf, (uint8_t []) { comment->type }, sizeof(uint8_t), true);

    if (result)
        result = extend_packed_buffer(pbuf, (uint32_t []) { comment->flags }, sizeof(uint32_t), true);

    if (result)
    {
        init_dynamic_rle_string(&text, g_db_comment_get_text(comment));
        result = pack_rle_string(&text, pbuf);
        exit_rle_string(&text);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = définition de commentaire à manipuler.             *
*                                                                             *
*  Description : Construit la description humaine d'un commentaire.           *
*                                                                             *
*  Retour      : Chaîne de caractère correspondante.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_db_comment_build_label(GDbComment *comment)
{
    char *result;                           /* Description à retourner     */
    DbItemFlags flags;                      /* Propriétés de l'élément     */
    const char *text;                       /* Commentaire associé         */
    const char *prefix;                     /* Préfixe à ajouter           */

    flags = g_db_item_get_flags(G_DB_ITEM(comment));

    if (flags & DIF_ERASER)
        asprintf(&result, _("Removed comment"));

    else if (flags & DIF_UPDATED)
    {
        text = "...";//get_rle_string(&comment->text);

        if (text != NULL)
            asprintf(&result, _("Updated comment: \"%s\""), text);
        else
            asprintf(&result, _("Reset comment"));
    }

    else
    {
        prefix = _("Created");

        text = "...";//get_rle_string(&comment->text);

        if (text != NULL)
            asprintf(&result, _("%s comment \"%s\""), prefix, text);
        else
            asprintf(&result, _("%s empty comment"), prefix);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = définition de commentaire à manipuler.             *
*                binary  = binaire chargé en mémoire à modifier.              *
*                apply   = indique s'il faut appliquer la définition ou non.  *
*                                                                             *
*  Description : Exécute l'impression de commentaire dans du code de binaire. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_comment_run(GDbComment *comment, GLoadedBinary *binary, bool apply)
{
    bool result;                            /* Bilan à faire remonter      */
    GBufferCache *cache;                    /* Ensemble de lignes à traiter*/
    GLineCursor *cursor;                    /* Emplacement dans un tampon  */
    size_t index;                           /* Point d'insertion           */
    GArchProcessor *proc;                   /* Propriétaire d'instructions */
    GArchInstruction *instr;                /* Instruction à traiter       */
    size_t scount;                          /* Nbre de sources affichées   */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *source;             /* Instruction diverse liée    */
    const mrange_t *range;                  /* Emplacement d'instruction   */
    size_t linked;                          /* Indice lié à traiter        */

    result = false;

    cache = g_loaded_binary_get_disassembly_cache(binary);
    if (cache == NULL) goto exit;

    g_buffer_cache_wlock(cache)

    switch (comment->type)
    {
        case CET_INLINED:

            cursor = g_binary_cursor_new();
            g_binary_cursor_update(G_BINARY_CURSOR(cursor), &comment->addr);

            index = g_buffer_cache_find_index_by_cursor(cache, cursor, true);

            g_object_unref(G_OBJECT(cursor));

            index = g_buffer_cache_look_for_flag(cache, index, BLF_HAS_CODE);

            g_buffer_cache_delete_type_at(cache, index, G_TYPE_DB_COMMENT, false, false);

            if (apply)
                g_buffer_cache_insert_at(cache, index, G_LINE_GENERATOR(comment), BLF_NONE, false, false);

            break;

        case CET_REPEATED:

            proc = g_loaded_binary_get_processor(binary);

            instr = g_arch_processor_find_instr_by_address(proc, &comment->addr);
            assert(instr != NULL);

            scount = g_arch_instruction_count_sources(instr);

            for (i = 0; i < scount && result; i++)
            {
                source = g_arch_instruction_get_source(instr, i);

                range = g_arch_instruction_get_range(source->linked);

                cursor = g_binary_cursor_new();
                g_binary_cursor_update(G_BINARY_CURSOR(cursor), get_mrange_addr(range));

                linked = g_buffer_cache_find_index_by_cursor(cache, cursor, true);
                assert(linked != g_buffer_cache_count_lines(cache));

                g_object_unref(G_OBJECT(cursor));

                /**
                 * On recherche ici une ligne potentiellement BLF_HAS_CODE ou BLF_IS_LABEL.
                 * Comme on ne peut pas traiter les deux cas, on prend la première qui vient
                 * avec BLF_NONE.
                 */

                linked = g_buffer_cache_look_for_flag(cache, linked, BLF_HAS_CODE | BLF_IS_LABEL);

                g_buffer_cache_delete_type_at(cache, linked, G_TYPE_DB_COMMENT, false, false);

                if (apply)
                    g_buffer_cache_insert_at(cache, linked, G_LINE_GENERATOR(comment), BLF_NONE, false, false);

                unref_instr_link(source);

            }

            g_object_unref(G_OBJECT(proc));
            break;

        case CET_BEFORE:
            break;

        case CET_AFTER:
            break;

        case CET_COUNT:
            assert(false);
            result = false;
            break;

    }

    g_buffer_cache_wunlock(cache);

    g_object_unref(G_OBJECT(cache));

    result = true;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = définition de commentaire à manipuler.             *
*                binary  = binaire chargé en mémoire à modifier.              *
*                                                                             *
*  Description : Réalise l'impression de commentaire dans du code de binaire. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_comment_apply(GDbComment *comment, GLoadedBinary *binary)
{
    bool result;                            /* Bilan à faire remonter      */

    result = g_db_comment_run(comment, binary, true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = définition de commentaire à manipuler.             *
*                binary  = binaire chargé en mémoire à modifier.              *
*                                                                             *
*  Description : Annule l'impression d'un commentaire dans du code de binaire.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_comment_cancel(GDbComment *comment, GLoadedBinary *binary)
{
    bool result;                            /* Bilan à faire remonter      */

    result = g_db_comment_run(comment, binary, false);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = commentaire textuel à charger depuis les réponses. *
*                values  = tableau d'éléments à consulter.                    *
*                count   = nombre de descriptions renseignées.                *
*                                                                             *
*  Description : Charge les valeurs utiles pour un commentaire.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_db_comment_load(GDbComment *comment, const bound_value *values, size_t count)
{
    bool result;                            /* Bilan à faire remonter      */
    const bound_value *value;               /* Valeur à éditer / définir   */
    rle_string string;                      /* Texte brut récupéré         */

    result = G_DB_ITEM_CLASS(g_db_comment_parent_class)->load(G_DB_ITEM(comment), values, count);

    if (result)
        result = load_vmpa(&comment->addr, NULL, values, count);

    if (result)
    {
        value = find_bound_value(values, count, "type");
        result = (value != NULL && value->type == SQLITE_INTEGER);

        if (result)
            comment->type = value->integer;

    }

    if (result)
    {
        value = find_bound_value(values, count, "line_flags");
        result = (value != NULL && value->type == SQLITE_INTEGER);

        if (result)
            comment->flags = value->integer;

    }

    if (result)
    {
        result = load_rle_string(&string, "text", values, count);

        if (result)
        {
            g_db_comment_define_text_lines(comment, get_rle_string(&string));
            exit_rle_string(&string);
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = base d'éléments sur laquelle s'appuyer.            *
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

static bool g_db_comment_store(GDbComment *comment, bound_value **values, size_t *count)
{
    bool status;                            /* Bilan d'opération initiale  */
    bound_value *value;                     /* Valeur à éditer / définir   */
    rle_string text;                        /* Texte brut récupéré         */

    if (comment == NULL)
        status = G_DB_ITEM_CLASS(g_db_comment_parent_class)->store(NULL, values, count);
    else
        status = G_DB_ITEM_CLASS(g_db_comment_parent_class)->store(G_DB_ITEM(comment), values, count);

    if (!status) return false;

    if (comment == NULL)
        status = store_vmpa(NULL, NULL, values, count);
    else
        status = store_vmpa(&comment->addr, NULL, values, count);

    if (!status) return false;

    *count += 1;
    *values = realloc(*values, *count * sizeof(bound_value));

    value = &(*values)[*count - 1];

    value->cname = "type";
    value->built_name = false;
    value->type = SQLITE_INTEGER;

    value->has_value = (comment != NULL);

    if (value->has_value)
    {
        value->integer = comment->type;
        value->delete = NULL;
    }

    *count += 1;
    *values = realloc(*values, *count * sizeof(bound_value));

    value = &(*values)[*count - 1];

    value->cname = "line_flags";
    value->built_name = false;
    value->type = SQLITE_INTEGER;

    value->has_value = (comment != NULL);

    if (value->has_value)
    {
        value->integer = comment->flags;
        value->delete = NULL;
    }

    if (comment == NULL)
        status = store_rle_string(NULL, "text", values, count);

    else
    {
        init_dynamic_rle_string(&text, g_db_comment_get_text(comment));
        status = store_rle_string(&text, "text", values, count);
        exit_rle_string(&text);
    }

    if (!status) return false;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : key     = clef de comparaison sous forme de localisation.    *
*                comment = informations de commentaire à consulter.           *
*                                                                             *
*  Description : Etablit la comparaison d'une adresse avec un commentaire.    *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int compare_comment_by_addr(const vmpa2t *key, const GDbComment * const *comment)
{
    int result;                         /* Bilan à retourner           */
    const vmpa2t *addr;                 /* Position du commentaire     */

    addr = g_db_comment_get_address(*comment);

    result = cmp_vmpa(key, addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = informations à consulter.                          *
*                                                                             *
*  Description : Fournit l'adresse associée à un commentaire.                 *
*                                                                             *
*  Retour      : Adresse mémoire.                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const vmpa2t *g_db_comment_get_address(const GDbComment *comment)
{
    const vmpa2t *result;                   /* Localisation à retourner    */

    result = &comment->addr;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = informations à consulter.                          *
*                                                                             *
*  Description : Indique le type d'incrustation prévue pour un commentaire.   *
*                                                                             *
*  Retour      : Incrustation associée au commentaire.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

CommentEmbeddingType g_db_comment_get_embedding_type(const GDbComment *comment)
{
    CommentEmbeddingType result;            /* Type à renvoyer             */

    result = comment->type;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = informations à consulter.                          *
*                                                                             *
*  Description : Fournit les particularités d'accroche liées à un commentaire.*
*                                                                             *
*  Retour      : Particularités éventuelles pour l'accroche.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

BufferLineFlags g_db_comment_get_flags(const GDbComment *comment)
{
    BufferLineFlags result;                 /* Type à renvoyer             */

    result = comment->flags;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = informations à consulter.                          *
*                                                                             *
*  Description : Fournit le commentaire associé à un commentaire.             *
*                                                                             *
*  Retour      : Commentaire existant à libérer après usage ou NULL.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_db_comment_get_text(GDbComment *comment)
{
    char *result;                           /* Chaîne constituée à renvoyer*/
    size_t count;                           /* Nombre d'éléments textuels  */
    size_t i;                               /* Boucle de parcours          */
    rle_string *string;                     /* Chaîne à consulter          */

    result = NULL;

    lock_flat_array(&comment->text);

    count = count_flat_array_items(comment->text);

    for (i = 0; i < count; i++)
    {
        string = get_flat_array_item(comment->text, i, sizeof(rle_string));

        assert(!is_rle_string_empty(string));

        result = stradd(result, get_rle_string(string));

    }

    unlock_flat_array(&comment->text);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          OFFRE DE CAPACITES DE GENERATION                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = générateur à consulter.                            *
*                                                                             *
*  Description : Indique le nombre de ligne prêtes à être générées.           *
*                                                                             *
*  Retour      : Nombre de lignes devant apparaître au final.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t g_db_comment_count_lines(GDbComment *comment)
{
    size_t result;                          /* Quantité à retourner        */

    lock_flat_array(&comment->text);

    result = count_flat_array_items(comment->text);

    unlock_flat_array(&comment->text);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = générateur à consulter.                            *
*                x       = position géographique sur la ligne concernée.      *
*                index   = indice de cette même ligne dans le tampon global.  *
*                repeat  = indice d'utilisations successives du générateur.   *
*                cursor  = emplacement à constituer. [OUT]                    *
*                                                                             *
*  Description : Retrouve l'emplacement correspondant à une position donnée.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_comment_compute_cursor(const GDbComment *comment, gint x, size_t index, size_t repeat, GLineCursor **cursor)
{
    *cursor = g_binary_cursor_new();

    g_binary_cursor_update(G_BINARY_CURSOR(*cursor), &comment->addr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = générateur à consulter.                            *
*                index   = indice de cette même ligne dans le tampon global.  *
*                repeat  = indice d'utilisations successives du générateur.   *
*                cursor  = emplacement à analyser.                            *
*                                                                             *
*  Description : Détermine si le conteneur s'inscrit dans une plage donnée.   *
*                                                                             *
*  Retour      : Bilan de la détermination, utilisable en comparaisons.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int g_db_comment_contain_cursor(const GDbComment *comment, size_t index, size_t repeat, const GLineCursor *cursor)
{
    int result;                             /* Conclusion à retourner      */
    vmpa2t addr;                            /* Autre emplacement à comparer*/

    assert(G_IS_BINARY_CURSOR(cursor));

    g_binary_cursor_retrieve(G_BINARY_CURSOR(cursor), &addr);

    result = cmp_vmpa(&addr, &comment->addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = générateur à consulter.                            *
*                index   = indice de cette même ligne dans le tampon global.  *
*                repeat  = indice d'utilisations successives du générateur.   *
*                                                                             *
*  Description : Renseigne sur les propriétés liées à un générateur.          *
*                                                                             *
*  Retour      : Propriétés particulières associées.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static BufferLineFlags g_db_comment_get_generator_flags(const GDbComment *comment, size_t index, size_t repeat)
{
    return BLF_NONE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : comment = générateur à utiliser pour l'impression.           *
*                line    = ligne de rendu à compléter.                        *
*                index   = indice de cette même ligne dans le tampon global.  *
*                repeat  = indice d'utilisations successives du générateur.   *
*                content = éventuel contenu binaire brut à imprimer.          *
*                                                                             *
*  Description : Imprime dans une ligne de rendu le contenu représenté.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_db_comment_print(GDbComment *comment, GBufferLine *line, size_t index, size_t repeat, const GBinContent *content)
{
    char *full;                             /* Contenu textuel complet     */
    size_t count;                           /* Quantité de ces lignes      */
    char **lines;                           /* Lignes brutes à représenter */
    GCodingLanguage *lang;                  /* Langage de sortie préféré   */
    size_t i;                               /* Boucle de parcours          */

    full = g_db_comment_get_text(comment);

    if (full != NULL)
    {
        lines = strtoka(full, "\n", &count);

        lang = g_asm_language_new();
        g_coding_language_encapsulate_comments(lang, &lines, &count);
        g_object_unref(G_OBJECT(lang));

        g_buffer_line_append_text(line, DLC_COMMENTS, SL(lines[repeat]), RTT_COMMENT, NULL);

        for (i = 0; i < count; i++)
            free(lines[i]);

        if (lines != NULL)
            free(lines);

        free(full);

    }

}



/* ---------------------------------------------------------------------------------- */
/*                        DEFINITION DE LA COLLECTION ASSOCIEE                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une collection de commentaires. */
G_DEFINE_TYPE(GCommentCollection, g_comment_collection, G_TYPE_DB_COLLECTION);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des commentaires sous forme de texte.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_comment_collection_class_init(GCommentCollectionClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GDbCollectionClass *collec;             /* Encore une autre vision...  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_comment_collection_dispose;
    object->finalize = (GObjectFinalizeFunc)g_comment_collection_finalize;

    collec = G_DB_COLLECTION_CLASS(klass);

    collec->create_table = (collec_create_db_table_fc)g_comment_collection_create_db_table;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise un commentaire sous forme de zone de texte.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_comment_collection_init(GCommentCollection *collec)
{
    G_DB_COLLECTION(collec)->featuring = DBF_COMMENTS;
    G_DB_COLLECTION(collec)->type = G_TYPE_DB_COMMENT;
    G_DB_COLLECTION(collec)->name = "Comments";

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

static void g_comment_collection_dispose(GCommentCollection *collec)
{
    G_OBJECT_CLASS(g_comment_collection_parent_class)->dispose(G_OBJECT(collec));

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

static void g_comment_collection_finalize(GCommentCollection *collec)
{
    G_OBJECT_CLASS(g_comment_collection_parent_class)->finalize(G_OBJECT(collec));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une collection dédiée aux commentaires.                 *
*                                                                             *
*  Retour      : Collection mise en place.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GCommentCollection *g_comment_collection_new(void)
{
    GCommentCollection *result;            /* Instance à retourner        */

    result = g_object_new(G_TYPE_COMMENT_COLLECTION, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : collec = ensemble d'éléments spectateur des opérations.      *
*                db     = accès à la base de données.                         *
*                                                                             *
*  Description : Crée la table des commentaires dans une base de données.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_comment_collection_create_db_table(const GCommentCollection *collec, sqlite3 *db)
{
    const char *sql;                        /* Patron de requête SQL       */
    char *addr_fields;                      /* Champs pour l'adresse       */
    char *request;                          /* Requête à exécuter          */
    char *msg;                              /* Message d'erreur            */
    int ret;                                /* Bilan de la création        */

    sql = "CREATE TABLE Comments ("         \
             SQLITE_DB_ITEM_CREATE ", "     \
             "%s, "                         \
             "type INTEGER, "               \
             "line_flags INTEGER, "         \
             SQLITE_RLESTR_CREATE("text")   \
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
