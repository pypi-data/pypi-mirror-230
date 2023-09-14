
/* Chrysalide - Outil d'analyse de fichiers binaires
 * symbol.c - gestion des symboles dans un binaire
 *
 * Copyright (C) 2009-2019 Cyrille Bagard
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


#include "symbol.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "symbol-int.h"
#include "../analysis/db/misc/rlestr.h"
#include "../core/columns.h"
#ifdef INCLUDE_GTK_SUPPORT
#   include "../glibext/gbinarycursor.h"
#endif
#include "../glibext/linegen-int.h"



/* --------------------- FONCTIONNALITES BASIQUES POUR SYMBOLES --------------------- */


/* Initialise la classe des symboles d'exécutables. */
static void g_binary_symbol_class_init(GBinSymbolClass *);

/* Initialise une instance de symbole d'exécutable. */
static void g_binary_symbol_init(GBinSymbol *);

/* Procède à l'initialisation de l'interface de génération. */
static void g_binary_symbol_interface_init(GLineGeneratorInterface *);

/* Procède à l'initialisation de l'interface de sérialisation. */
static void g_binary_symbol_serializable_init(GSerializableObjectInterface *);

/* Supprime toutes les références externes. */
static void g_binary_symbol_dispose(GBinSymbol *);

/* Procède à la libération totale de la mémoire. */
static void g_binary_symbol_finalize(GBinSymbol *);



/* ------------------------ OFFRE DE CAPACITES DE GENERATION ------------------------ */


/* Indique le nombre de ligne prêtes à être générées. */
static size_t g_binary_symbol_count_lines(const GBinSymbol *);

#ifdef INCLUDE_GTK_SUPPORT

/* Retrouve l'emplacement correspondant à une position donnée. */
static void g_binary_symbol_compute_cursor(const GBinSymbol *, gint, size_t, size_t, GLineCursor **);

/* Détermine si le conteneur s'inscrit dans une plage donnée. */
static int g_binary_symbol_contain_cursor(const GBinSymbol *, size_t, size_t, const GLineCursor *);

#endif

/* Renseigne sur les propriétés liées à un générateur. */
static BufferLineFlags g_binary_symbol_get_line_flags(const GBinSymbol *, size_t, size_t);

/* Imprime dans une ligne de rendu le contenu représenté. */
static void g_binary_symbol_print(GBinSymbol *, GBufferLine *, size_t, size_t, const GBinContent *);



/* -------------------- CONSERVATION ET RECHARGEMENT DES DONNEES -------------------- */


/* Charge un contenu depuis une mémoire tampon. */
static bool _g_binary_symbol_load(GBinSymbol *, GObjectStorage *, packed_buffer_t *);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_binary_symbol_load(GBinSymbol *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool _g_binary_symbol_store(GBinSymbol *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_binary_symbol_store(GBinSymbol *, GObjectStorage *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                       FONCTIONNALITES BASIQUES POUR SYMBOLES                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un symbole d'exécutable. */
G_DEFINE_TYPE_WITH_CODE(GBinSymbol, g_binary_symbol, G_TYPE_OBJECT,
                        G_IMPLEMENT_INTERFACE(G_TYPE_LINE_GENERATOR, g_binary_symbol_interface_init)
                        G_IMPLEMENT_INTERFACE(G_TYPE_SERIALIZABLE_OBJECT, g_binary_symbol_serializable_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des symboles d'exécutables.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_symbol_class_init(GBinSymbolClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_binary_symbol_dispose;
    object->finalize = (GObjectFinalizeFunc)g_binary_symbol_finalize;

    klass->load = (load_symbol_fc)_g_binary_symbol_load;
    klass->store = (store_symbol_fc)_g_binary_symbol_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de symbole d'exécutable.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_symbol_init(GBinSymbol *symbol)
{
    sym_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_SYMBOL_EXTRA(symbol);

    INIT_GOBJECT_EXTRA_LOCK(extra);

    g_binary_symbol_set_stype(symbol, STP_COUNT);

    g_binary_symbol_set_status(symbol, SSS_INTERNAL);

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

static void g_binary_symbol_interface_init(GLineGeneratorInterface *iface)
{
    iface->count = (linegen_count_lines_fc)g_binary_symbol_count_lines;
#ifdef INCLUDE_GTK_SUPPORT
    iface->compute = (linegen_compute_fc)g_binary_symbol_compute_cursor;
    iface->contain = (linegen_contain_fc)g_binary_symbol_contain_cursor;
#endif
    iface->get_flags = (linegen_get_flags_fc)g_binary_symbol_get_line_flags;
    iface->print = (linegen_print_fc)g_binary_symbol_print;

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

static void g_binary_symbol_serializable_init(GSerializableObjectInterface *iface)
{
    iface->load = (load_serializable_object_cb)g_binary_symbol_load;
    iface->store = (store_serializable_object_cb)g_binary_symbol_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_symbol_dispose(GBinSymbol *symbol)
{
    G_OBJECT_CLASS(g_binary_symbol_parent_class)->dispose(G_OBJECT(symbol));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_binary_symbol_finalize(GBinSymbol *symbol)
{
    if (symbol->alt != NULL)
        free(symbol->alt);

    G_OBJECT_CLASS(g_binary_symbol_parent_class)->finalize(G_OBJECT(symbol));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : range = espace couvert par le nouveau symbole.               *
*                type  = type de symbole à créer.                             *
*                                                                             *
*  Description : Crée un nouveau symbole d'exécutable.                        *
*                                                                             *
*  Retour      : Adresse de l'instance mise en place ou NULL en cas d'échec.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinSymbol *g_binary_symbol_new(const mrange_t *range, SymbolType type)
{
    GBinSymbol *result;                     /* Nouveau symbole à renvoyer  */

    result = g_object_new(G_TYPE_BIN_SYMBOL, NULL);

    g_binary_symbol_set_range(result, range);
    g_binary_symbol_set_stype(result, type);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier symbole à analyser.                              *
*                b = second symbole à analyser.                               *
*                                                                             *
*  Description : Compare deux symboles d'exécutable selon leurs propriétés.   *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1 (-1 par défaut).        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int g_binary_symbol_cmp(const GBinSymbol * const *a, const GBinSymbol * const *b)
{
    int result;                             /* Bilan à retourner           */
    const mrange_t *range_a;                /* Emplacement du symbole A    */
    const mrange_t *range_b;                /* Emplacement du symbole B    */

    range_a = &(*a)->range;
    range_b = &(*b)->range;

    result = cmp_vmpa(get_mrange_addr(range_a), get_mrange_addr(range_b));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à analyser.                                 *
*                addr   = localisation à venir comparer à celle du symbole.   *
*                                                                             *
*  Description : Compare un symbole et une localisation.                      *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1 (-1 par défaut).        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int g_binary_symbol_cmp_with_vmpa(const GBinSymbol *symbol, const vmpa2t *addr)
{
    int result;                             /* Bilan à retourner           */

    result = cmp_mrange_with_vmpa(&symbol->range, addr);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à mettre à jour.                            *
*                range  = plage mémoire ou physique déclarée.                 *
*                                                                             *
*  Description : Définit la couverture physique / en mémoire d'un symbole.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_symbol_set_range(GBinSymbol *symbol, const mrange_t *range)
{
    copy_mrange(&symbol->range, range);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                                                                             *
*  Description : Fournit l'emplacement où se situe un symbole.                *
*                                                                             *
*  Retour      : Zone mémoire couverte par le symbole.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const mrange_t *g_binary_symbol_get_range(const GBinSymbol *symbol)
{
    return &symbol->range;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir modifier.                           *
*                type   = type de symbole représenté.                         *
*                                                                             *
*  Description : Définit le type du symbole.                                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_symbol_set_stype(GBinSymbol *symbol, SymbolType type)
{
    sym_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_SYMBOL_EXTRA(symbol);

    LOCK_GOBJECT_EXTRA(extra);

    extra->stype = type;

    UNLOCK_GOBJECT_EXTRA(extra);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                                                                             *
*  Description : Fournit le type du symbole.                                  *
*                                                                             *
*  Retour      : Type de symbole représenté.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

SymbolType g_binary_symbol_get_stype(const GBinSymbol *symbol)
{
    SymbolType result;                      /* Type à retourner            */
    sym_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_SYMBOL_EXTRA(symbol);

    LOCK_GOBJECT_EXTRA(extra);

    result = extra->stype;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir modifier.                           *
*                status = état de la visibilité du symbole représenté.        *
*                                                                             *
*  Description : Définit la visibilité du symbole.                            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_symbol_set_status(GBinSymbol *symbol, SymbolStatus status)
{
    sym_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_SYMBOL_EXTRA(symbol);

    LOCK_GOBJECT_EXTRA(extra);

    extra->status = status;

    UNLOCK_GOBJECT_EXTRA(extra);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                                                                             *
*  Description : Fournit la visibilité du symbole.                            *
*                                                                             *
*  Retour      : Etat de la visibilité du symbole représenté.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

SymbolStatus g_binary_symbol_get_status(const GBinSymbol *symbol)
{
    SymbolStatus result;                    /* Visibilité à retourner      */
    sym_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_SYMBOL_EXTRA(symbol);

    LOCK_GOBJECT_EXTRA(extra);

    result = extra->status;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir modifier.                           *
*                flag   = drapeau d'information complémentaire à planter.     *
*                                                                             *
*  Description : Ajoute une information complémentaire à un symbole.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_symbol_set_flag(GBinSymbol *symbol, SymbolFlag flag)
{
    bool result;                            /* Bilan à retourner           */
    sym_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_SYMBOL_EXTRA(symbol);

    LOCK_GOBJECT_EXTRA(extra);

    result = !(extra->flags & flag);

    extra->flags |= flag;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir modifier.                           *
*                flag   = drapeau d'information complémentaire à planter.     *
*                                                                             *
*  Description : Retire une information complémentaire à un symbole.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_symbol_unset_flag(GBinSymbol *symbol, SymbolFlag flag)
{
    bool result;                            /* Bilan à retourner           */
    sym_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_SYMBOL_EXTRA(symbol);

    LOCK_GOBJECT_EXTRA(extra);

    result = (extra->flags & flag);

    extra->flags &= ~flag;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                flag   = drapeau d'information à rechercher.                 *
*                                                                             *
*  Description : Détermine si un symbole possède un fanion particulier.       *
*                                                                             *
*  Retour      : Bilan de la détection.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_symbol_has_flag(const GBinSymbol *symbol, SymbolFlag flag)
{
    bool result;                            /* Bilan à retourner           */
    sym_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_SYMBOL_EXTRA(symbol);

    LOCK_GOBJECT_EXTRA(extra);

    result = (extra->flags & flag);

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                                                                             *
*  Description : Fournit les particularités du symbole.                       *
*                                                                             *
*  Retour      : Somme de tous les fanions associés au symbole.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

SymbolFlag g_binary_symbol_get_flags(const GBinSymbol *symbol)
{
    SymbolFlag result;                      /* Fanions à retourner         */
    sym_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_SYMBOL_EXTRA(symbol);

    LOCK_GOBJECT_EXTRA(extra);

    result = extra->flags;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                prefix = éventuel préfixe à constituer. [OUT]                *
*                                                                             *
*  Description : Fournit le préfixe compatible avec une sortie "nm".          *
*                                                                             *
*  Retour      : true si un préfixe "nm" est renseigné.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_binary_symbol_get_nm_prefix(const GBinSymbol *symbol, char *prefix)
{
    bool result;                            /* Validité à retourner        */
    sym_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_SYMBOL_EXTRA(symbol);

    LOCK_GOBJECT_EXTRA(extra);

    result = (extra->flags & SFL_HAS_NM_PREFIX);

    if (result)
        *prefix = extra->nm_prefix;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}

/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                prefix = préfixe "nm" à associer au symbole.                 *
*                                                                             *
*  Description : Définit le préfixe compatible avec une sortie "nm".          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_symbol_set_nm_prefix(const GBinSymbol *symbol, char prefix)
{
    sym_extra_data_t *extra;                /* Données insérées à modifier */

    extra = GET_BIN_SYMBOL_EXTRA(symbol);

    LOCK_GOBJECT_EXTRA(extra);

    extra->nm_prefix = prefix;
    extra->flags |= SFL_HAS_NM_PREFIX;

    UNLOCK_GOBJECT_EXTRA(extra);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                                                                             *
*  Description : Fournit une étiquette pour viser un symbole.                 *
*                                                                             *
*  Retour      : Chaîne de caractères renvoyant au symbole.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_binary_symbol_get_label(const GBinSymbol *symbol)
{
    char *result;                           /* Etiquette à retourner       */

    if (symbol->alt != NULL)
        result = strdup(symbol->alt);

    else if (G_BIN_SYMBOL_GET_CLASS(symbol)->get_label != NULL)
        result = G_BIN_SYMBOL_GET_CLASS(symbol)->get_label(symbol);

    else
        result = NULL;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                alt    = désignation humaine alternative à favoriser.        *
*                                                                             *
*  Description : Définit un autre nom pour le symbole.                        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_symbol_set_alt_label(GBinSymbol *symbol, const char *alt)
{
    if (symbol->alt != NULL)
        free(symbol->alt);

    if (alt == NULL)
        symbol->alt = NULL;
    else
        symbol->alt = strdup(alt);

}



/* ---------------------------------------------------------------------------------- */
/*                          OFFRE DE CAPACITES DE GENERATION                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = générateur à consulter pour futur usage.            *
*                                                                             *
*  Description : Détermine si un symbole pour faire office de générateur.     *
*                                                                             *
*  Retour      : Instance de générateur si les capacités sont là.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GLineGenerator *g_binary_symbol_produce_label(GBinSymbol *symbol)
{
    GLineGenerator *result;                 /* Instance à retourner        */
    char *label;                            /* Etiquette à insérer         */

    label = g_binary_symbol_get_label(symbol);

    if (label == NULL)
        result = NULL;

    else
    {
        result = G_LINE_GENERATOR(symbol);
        free(label);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = générateur à consulter.                             *
*                                                                             *
*  Description : Indique le nombre de ligne prêtes à être générées.           *
*                                                                             *
*  Retour      : Nombre de lignes devant apparaître au final.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static size_t g_binary_symbol_count_lines(const GBinSymbol *symbol)
{
    return 1;

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = générateur à consulter.                             *
*                x      = position géographique sur la ligne concernée.       *
*                index  = indice de cette même ligne dans le tampon global.   *
*                repeat = indice d'utilisations successives du générateur.    *
*                cursor = emplacement à constituer. [OUT]                     *
*                                                                             *
*  Description : Retrouve l'emplacement correspondant à une position donnée.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_binary_symbol_compute_cursor(const GBinSymbol *symbol, gint x, size_t index, size_t repeat, GLineCursor **cursor)
{
    *cursor = g_binary_cursor_new();

    g_binary_cursor_update(G_BINARY_CURSOR(*cursor), get_mrange_addr(&symbol->range));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = générateur à consulter.                             *
*                index  = indice de cette même ligne dans le tampon global.   *
*                repeat = indice d'utilisations successives du générateur.    *
*                cursor = emplacement à analyser.                             *
*                                                                             *
*  Description : Détermine si le conteneur s'inscrit dans une plage donnée.   *
*                                                                             *
*  Retour      : Bilan de la détermination, utilisable en comparaisons.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int g_binary_symbol_contain_cursor(const GBinSymbol *symbol, size_t index, size_t repeat, const GLineCursor *cursor)
{
    int result;                             /* Conclusion à retourner      */
    vmpa2t addr;                            /* Autre emplacement à comparer*/

    assert(G_IS_BINARY_CURSOR(cursor));

    g_binary_cursor_retrieve(G_BINARY_CURSOR(cursor), &addr);

    /**
     * En tant que générateur, le symbole ne couvre qu'une ou plusieurs lignes
     * uniquement à son adresse de départ.
     *
     * On ne doit donc pas considérer l'ensemble de la taille du symbole en
     * utilisant par exemple un appel comme :
     *
     *    result = cmp_mrange_with_vmpa(&symbol->range, addr);
     *
     */

    result = cmp_vmpa(&addr, get_mrange_addr(&symbol->range));

    return result;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = générateur à consulter.                             *
*                index  = indice de cette même ligne dans le tampon global.   *
*                repeat = indice d'utilisations successives du générateur.    *
*                                                                             *
*  Description : Renseigne sur les propriétés liées à un générateur.          *
*                                                                             *
*  Retour      : Propriétés particulières associées.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static BufferLineFlags g_binary_symbol_get_line_flags(const GBinSymbol *symbol, size_t index, size_t repeat)
{
    return BLF_IS_LABEL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol  = générateur à utiliser pour l'impression.           *
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

static void g_binary_symbol_print(GBinSymbol *symbol, GBufferLine *line, size_t index, size_t repeat, const GBinContent *content)
{
    char *label;                            /* Etiquette à insérer         */

    g_buffer_line_fill_phys(line, DLC_PHYSICAL, MDS_32_BITS_UNSIGNED, get_mrange_addr(&symbol->range));

    g_buffer_line_fill_virt(line, DLC_VIRTUAL, MDS_32_BITS_UNSIGNED, get_mrange_addr(&symbol->range));

    label = g_binary_symbol_get_label(symbol);

    /**
     * Normalement, l'étiquette n'est pas vide car le générateur provient de
     * g_binary_symbol_produce_label(), qui filtre.
     *
     * Mais le symbole a pu être manipulé entre temps, donc on évite un assert().
     */

    if (label != NULL)
    {
        g_buffer_line_start_merge_at(line, DLC_ASSEMBLY_LABEL);
        g_buffer_line_append_text(line, DLC_ASSEMBLY_LABEL, SL(label), RTT_LABEL, NULL);
        g_buffer_line_append_text(line, DLC_ASSEMBLY_LABEL, ":", 1, RTT_PUNCT, NULL);

        free(label);

    }

}



/* ---------------------------------------------------------------------------------- */
/*                      CONSERVATION ET RECHARGEMENT DES DONNEES                      */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol  = élément GLib à constuire.                          *
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

static bool _g_binary_symbol_load(GBinSymbol *symbol, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    sym_extra_data_t *extra;                /* Données insérées à consulter*/
    uleb128_t value;                        /* Valeur ULEB128 à charger    */
    rle_string str;                         /* Chaîne à charger            */

    extra = GET_BIN_SYMBOL_EXTRA(symbol);

    LOCK_GOBJECT_EXTRA(extra);

    result = unpack_uleb128(&value, pbuf);

    if (result)
        extra->stype = value;

    if (result)
    {
        result = unpack_uleb128(&value, pbuf);

        if (result)
            extra->status = value;

    }

    if (result)
        result = extract_packed_buffer(pbuf, &extra->nm_prefix, 1, false);

    if (result)
    {
        result = unpack_uleb128(&value, pbuf);

        if (result)
            extra->flags = value;

    }

    UNLOCK_GOBJECT_EXTRA(extra);

    if (result)
        result = unpack_mrange(&symbol->range, pbuf);

    if (result)
    {
        setup_empty_rle_string(&str);

        result = unpack_rle_string(&str, pbuf);

        if (result && get_rle_string(&str) != NULL)
            symbol->alt = strdup(get_rle_string(&str));

        exit_rle_string(&str);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol  = élément GLib à constuire.                          *
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

static bool g_binary_symbol_load(GBinSymbol *symbol, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GBinSymbolClass *class;                 /* Classe à activer            */

    class = G_BIN_SYMBOL_GET_CLASS(symbol);

    result = class->load(symbol, storage, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol  = élément GLib à consulter.                          *
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

static bool _g_binary_symbol_store(GBinSymbol *symbol, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    sym_extra_data_t *extra;                /* Données insérées à consulter*/
    rle_string str;                         /* Chaîne à conserver          */

    extra = GET_BIN_SYMBOL_EXTRA(symbol);

    LOCK_GOBJECT_EXTRA(extra);

    result = pack_uleb128((uleb128_t []){ extra->stype }, pbuf);

    if (result)
        result = pack_uleb128((uleb128_t []){ extra->status }, pbuf);

    if (result)
        result = extend_packed_buffer(pbuf, &extra->nm_prefix, 1, false);

    if (result)
        result = pack_uleb128((uleb128_t []){ extra->flags }, pbuf);

    UNLOCK_GOBJECT_EXTRA(extra);

    if (result)
        result = pack_mrange(&symbol->range, pbuf);

    if (result)
    {
        init_static_rle_string(&str, symbol->alt);

        result = pack_rle_string(&str, pbuf);

        exit_rle_string(&str);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol  = élément GLib à consulter.                          *
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

static bool g_binary_symbol_store(GBinSymbol *symbol, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GBinSymbolClass *class;                 /* Classe à activer            */

    class = G_BIN_SYMBOL_GET_CLASS(symbol);

    result = class->store(symbol, storage, pbuf);

    return result;

}
