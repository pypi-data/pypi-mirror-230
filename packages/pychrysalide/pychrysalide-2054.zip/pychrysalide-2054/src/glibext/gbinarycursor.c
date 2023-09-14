
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gbinarycursor.c - suivi de positions dans des panneaux de chargement
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include "gbinarycursor.h"


#include <assert.h>
#include <malloc.h>


#include <i18n.h>


#include "glinecursor-int.h"
#include "../analysis/binary.h"
#include "../common/extstr.h"



/* ----------------------- FONCTIONNALITES D'UN SUIVI DE BASE ----------------------- */


/* Suivi de positions dans un panneau de chargement (instance) */
struct _GBinaryCursor
{
    GLineCursor parent;                     /* A laisser en premier        */

    bool raw;                               /* Position brute ?            */
    vmpa2t addr;                            /* Position mémoire du curseur */

};

/* Suivi de positions dans un panneau de chargement (classe) */
struct _GBinaryCursorClass
{
    GLineCursorClass parent;                /* A laisser en premier        */

};


/* Procède à l'initialisation d'une classe de suivi de position. */
static void g_binary_cursor_class_init(GBinaryCursorClass *);

/* Procède à l'initialisation d'un suivi de positions. */
static void g_binary_cursor_init(GBinaryCursor *);

/* Supprime toutes les références externes. */
static void g_binary_cursor_dispose(GBinaryCursor *);

/* Procède à la libération totale de la mémoire. */
static void g_binary_cursor_finalize(GBinaryCursor *);

/* Réalise la copie d'un suivi d'emplacements. */
static GLineCursor *g_binary_cursor_duplicate(const GBinaryCursor *);

/* Compare deux suivis d'emplacements. */
static int g_binary_cursor_compare(const GBinaryCursor *, const GBinaryCursor *);

/* Détermine si la position de suivi est pertinente ou non. */
static bool g_binary_cursor_is_valid(const GBinaryCursor *);

/* Construit une étiquette de représentation d'un suivi. */
static char *g_binary_cursor_build_label(const GBinaryCursor *);

/* Extrait des détails complémentaires et actualise le statut. */
#ifdef INCLUDE_GTK_SUPPORT
static void prepare_and_show_status_from_binary_cursor(const mrange_t *, const char *, const GLoadedBinary *, GtkStatusStack *);
#endif

/* Affiche une position dans une barre de statut. */
static void g_binary_cursor_show_status(const GBinaryCursor *, GtkStatusStack *, GLoadedContent *);



/* ---------------------- ENCADREMENT DES TRANSFERTS DE DONEES ---------------------- */


/* Exporte la définition d'un emplacement dans un flux réseau. */
static bool g_binary_cursor_serialize(const GBinaryCursor *, packed_buffer_t *);

/* Importe la définition d'un emplacement depuis un flux réseau. */
static bool g_binary_cursor_unserialize(GBinaryCursor *, packed_buffer_t *);



/* ------------------------- LIENS AVEC UNE BASE DE DONNEES ------------------------- */


/* Charge les valeurs utiles pour une localisation. */
static bool g_binary_cursor_load(GBinaryCursor *, const char *, const bound_value *, size_t);



/* ---------------------------------------------------------------------------------- */
/*                         FONCTIONNALITES D'UN SUIVI DE BASE                         */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type du gestionnaire de largeurs associées aux lignes. */
G_DEFINE_TYPE(GBinaryCursor, g_binary_cursor, G_TYPE_LINE_CURSOR);


/******************************************************************************
*                                                                             *
*  Paramètres  : class = classe de composant GTK à initialiser.               *
*                                                                             *
*  Description : Procède à l'initialisation d'une classe de suivi de position.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_cursor_class_init(GBinaryCursorClass *class)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GLineCursorClass *line;                 /* Version parente de la classe*/

    object = G_OBJECT_CLASS(class);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_binary_cursor_dispose;
    object->finalize = (GObjectFinalizeFunc)g_binary_cursor_finalize;

    line = G_LINE_CURSOR_CLASS(class);

    line->duplicate = (duplicate_cursor_fc)g_binary_cursor_duplicate;
    line->compare = (compare_cursor_fc)g_binary_cursor_compare;
    line->is_valid = (is_cursor_valid_fc)g_binary_cursor_is_valid;
    line->build_label = (build_cursor_label_fc)g_binary_cursor_build_label;
    line->show_status = (show_cursor_status_fc)g_binary_cursor_show_status;

    line->serialize = (serialize_cursor_fc)g_binary_cursor_serialize;
    line->unserialize = (unserialize_cursor_fc)g_binary_cursor_unserialize;

    line->create_db = (create_cursor_db_table_fc)g_binary_cursor_create_db_table;
    line->load = (load_cursor_fc)g_binary_cursor_load;
    line->store = (store_cursor_fc)g_binary_cursor_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = composant GLib à initialiser.                       *
*                                                                             *
*  Description : Procède à l'initialisation d'un suivi de positions.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_cursor_init(GBinaryCursor *cursor)
{
    cursor->raw = false;

    init_vmpa(&cursor->addr, VMPA_NO_PHYSICAL, VMPA_NO_VIRTUAL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_cursor_dispose(GBinaryCursor *cursor)
{
    G_OBJECT_CLASS(g_binary_cursor_parent_class)->dispose(G_OBJECT(cursor));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_cursor_finalize(GBinaryCursor *cursor)
{
    G_OBJECT_CLASS(g_binary_cursor_parent_class)->finalize(G_OBJECT(cursor));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouveau suivi de positions dans un panneau.          *
*                                                                             *
*  Retour      : Instance de suivi en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GLineCursor *g_binary_cursor_new(void)
{
    GLineCursor *result;                    /* Instance à retourner        */

    result = g_object_new(G_TYPE_BINARY_CURSOR, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi d'emplacement à dupliquer.                    *
*                                                                             *
*  Description : Réalise la copie d'un suivi d'emplacements.                  *
*                                                                             *
*  Retour      : Nouvelle instance copiée.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GLineCursor *g_binary_cursor_duplicate(const GBinaryCursor *cursor)
{
    GLineCursor *result;                    /* Instance à retourner        */

    result = g_binary_cursor_new();

    G_BINARY_CURSOR(result)->raw = cursor->raw;

    g_binary_cursor_update(G_BINARY_CURSOR(cursor), &cursor->addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = premier suivi d'emplacement à comparer.             *
*                other  = second suivi d'emplacement à comparer.              *
*                                                                             *
*  Description : Compare deux suivis d'emplacements.                          *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int g_binary_cursor_compare(const GBinaryCursor *cursor, const GBinaryCursor *other)
{
    int result;                             /* Bilan à renvoyer            */

    result = cmp_vmpa(&cursor->addr, &other->addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi d'emplacement à consulter.                    *
*                                                                             *
*  Description : Détermine si la position de suivi est pertinente ou non.     *
*                                                                             *
*  Retour      : Bilan de validité.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_binary_cursor_is_valid(const GBinaryCursor *cursor)
{
    bool result;                            /* Bilan à renvoyer            */

    result = !is_invalid_vmpa(&cursor->addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi d'emplacement à consulter.                    *
*                                                                             *
*  Description : Construit une étiquette de représentation d'un suivi.        *
*                                                                             *
*  Retour      : Etiquette à libérer de la mémoire après usage.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_binary_cursor_build_label(const GBinaryCursor *cursor)
{
    char *result;                           /* Etiquette à retourner       */
    VMPA_BUFFER(loc);                       /* Indication de position      */

    vmpa2_to_string(&cursor->addr, MDS_UNDEFINED, loc, NULL);

    result = strdup(loc);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : range    = emplacement à mettre en valeur.                   *
*                encoding = encodage d'une éventuelle instruction ou NULL.    *
*                binary   = binaire chargé rassemblant l'ensemble des infos.  *
*                stack    = barre de statut à actualiser.                     *
*                                                                             *
*  Description : Extrait des détails complémentaires et actualise le statut.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

#ifdef INCLUDE_GTK_SUPPORT
static void prepare_and_show_status_from_binary_cursor(const mrange_t *range, const char *encoding, const GLoadedBinary *binary, GtkStatusStack *stack)
{
    GExeFormat *format;                     /* Format de binaire à traiter */
    const vmpa2t *addr;                     /* Localisation de départ      */
    GBinPortion *portions;                  /* Couche première de portions */
    GBinPortion *portion;                   /* Zone mémoire d'appartenance */
    const char *text;                       /* Texte au contenu à copier   */
    const char *segment;                    /* Désignation d'un segment    */
    GBinSymbol *symbol;                     /* Symbole présent à l'adresse */
    phys_t diff;                            /* Décalage de l'adresse       */
    char *label;                            /* Description d'un symbole    */
    vmpa2t tmp;                             /* Zone de construction temp.  */
    VMPA_BUFFER(offset);                    /* Décalage physique           */
    char *sym_name;                         /* Position selon un symbole   */

    /* Préparations utiles */

    format = g_loaded_binary_get_format(binary);

    addr = get_mrange_addr(range);

    /* Zone d'appartenance */

    portions = g_exe_format_get_portions(format);

    portion = g_binary_portion_find_at_addr(portions, addr);

    text = g_binary_portion_get_desc(portion);

    segment = (text != NULL ? text : _("Binary"));

    g_object_unref(G_OBJECT(portion));

    g_object_unref(G_OBJECT(portions));

    /* Symbole concerné */

    sym_name = NULL;

    if (g_binary_format_resolve_symbol(G_BIN_FORMAT(format), addr, false, &symbol, &diff))
    {
        label = g_binary_symbol_get_label(symbol);

        if (label != NULL)
        {
            sym_name = label;

            sym_name = stradd(sym_name, "+");

            init_vmpa(&tmp, diff, VMPA_NO_VIRTUAL);
            vmpa2_phys_to_string(&tmp, MDS_UNDEFINED, offset, NULL);

            sym_name = stradd(sym_name, offset);

        }

        g_object_unref(G_OBJECT(symbol));

    }

    /* Demande d'affichage final */

    gtk_status_stack_update_current_location(stack, range, segment, sym_name, encoding);

    if (sym_name != NULL)
        free(sym_name);

}
#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor  = emplacement du curseur à afficher.                 *
*                stack   = pile de statuts à mettre à jour.                   *
*                content = contenu contenant le curseur à représenter.        *
*                                                                             *
*  Description : Affiche une position dans une barre de statut.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_cursor_show_status(const GBinaryCursor *cursor, GtkStatusStack *stack, GLoadedContent *content)
{
#ifdef INCLUDE_GTK_SUPPORT
    GLoadedBinary *binary;                  /* Binaire chargé et analysé   */
    GArchProcessor *proc;                   /* Architecture du binaire     */
    mrange_t tmp;                           /* Emplacement réduit          */
    const mrange_t *range;                  /* Emplacement d'instruction   */
    const char *encoding;                   /* Encodage à présenter        */
    GArchInstruction *instr;                /* Instruction présente        */

    if (g_binary_cursor_is_valid(cursor))
    {
        assert(G_IS_LOADED_BINARY(content));

        binary = G_LOADED_BINARY(content);

        if (cursor->raw)
        {
            init_mrange(&tmp, &cursor->addr, VMPA_NO_PHYSICAL);

            prepare_and_show_status_from_binary_cursor(&tmp, NULL, binary, stack);

        }

        else
        {
            proc = g_loaded_binary_get_processor(binary);

            instr = _g_arch_processor_find_instr_by_address(proc, &cursor->addr, true);
            assert(instr != NULL);

            range = g_arch_instruction_get_range(instr);
            encoding = g_arch_instruction_get_encoding(instr);

            prepare_and_show_status_from_binary_cursor(range, encoding, binary, stack);

            g_object_unref(G_OBJECT(instr));

            g_object_unref(G_OBJECT(proc));

        }

    }

    else
        gtk_status_stack_reset_current_location(stack);
#endif
}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi de positions à mettre à jour.                 *
*                raw    = nature de la représentation de l'emplacement visé.  *
*                                                                             *
*  Description : Précise la représentation de l'emplacement.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_cursor_set_raw(GBinaryCursor *cursor, bool raw)
{
    cursor->raw = raw;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi de positions à consulter.                     *
*                                                                             *
*  Description : Indique la représentation de l'emplacement.                  *
*                                                                             *
*  Retour      : true so la représentation de l'emplacement est brute.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_cursor_is_raw(const GBinaryCursor *cursor)
{
    bool result;                            /* Statut à retourner          */

    result = cursor->raw;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi de positions à mettre à jour.                 *
*                addr   = emplacement dans le binaire visé.                   *
*                                                                             *
*  Description : Met à jour la position suivi dans un panneau de chargement.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_cursor_update(GBinaryCursor *cursor, const vmpa2t *addr)
{
    copy_vmpa(&cursor->addr, addr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi de positions à consulter.                     *
*                addr   = emplacement dans le binaire visé. [OUT]             *
*                                                                             *
*  Description : Transmet la position de suivi dans un panneau de chargement. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_cursor_retrieve(const GBinaryCursor *cursor, vmpa2t *addr)
{
    copy_vmpa(addr, &cursor->addr);

}



/* ---------------------------------------------------------------------------------- */
/*                        ENCADREMENT DES TRANSFERTS DE DONEES                        */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi de positions à sauvegarder.                   *
*                pbuf   = paquet de données où venir inscrire les infos.      *
*                                                                             *
*  Description : Exporte la définition d'un emplacement dans un flux réseau.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_binary_cursor_serialize(const GBinaryCursor *cursor, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = pack_vmpa(&cursor->addr, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi de positions à charger. [OUT]                 *
*                pbuf = paquet de données où venir inscrire les infos.        *
*                                                                             *
*  Description : Importe la définition d'un emplacement depuis un flux réseau.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_binary_cursor_unserialize(GBinaryCursor *cursor, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = unpack_vmpa(&cursor->addr, pbuf);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           LIENS AVEC UNE BASE DE DONNEES                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : base = tronc commun pour les champs de la base de données.   *
*                                                                             *
*  Description : Donne les éléments requis pour la construction d'une table.  *
*                                                                             *
*  Retour      : Partie de requête à insérer dans la requête globale.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_binary_cursor_create_db_table(const char *base)
{
    char *result;                           /* Requête à retourner         */

    result = create_vmpa_db_table(base);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi de positions dont la définition est à définir.*
*                base   = tronc commun pour les champs de la base de données. *
*                values = tableau d'éléments à consulter.                     *
*                count  = nombre de descriptions renseignées.                 *
*                                                                             *
*  Description : Charge les valeurs utiles pour une localisation.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_binary_cursor_load(GBinaryCursor *cursor, const char *base, const bound_value *values, size_t count)
{
    bool result;                            /* Bilan à renvoyer            */

    result = load_vmpa(&cursor->addr, base, values, count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : cursor = suivi de positions à traiter.                       *
*                base   = tronc commun pour les champs de la base de données. *
*                values = couples de champs et de valeurs à lier. [OUT]       *
*                count  = nombre de ces couples. [OUT]                        *
*                                                                             *
*  Description : Constitue les champs destinés à une insertion / modification.*
*                                                                             *
*  Retour      : Bilan de l'opération : succès ou non.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_cursor_store(const GBinaryCursor *cursor, const char *base, bound_value **values, size_t *count)
{
    bool result;                            /* Bilan à renvoyer            */

    if (cursor == NULL)
        result = store_vmpa(NULL, base, values, count);
    else
        result = store_vmpa(&cursor->addr, base, values, count);

    return result;

}
