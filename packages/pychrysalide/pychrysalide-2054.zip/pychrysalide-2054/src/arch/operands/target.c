
/* Chrysalide - Outil d'analyse de fichiers binaires
 * target.c - opérandes ciblant un symbole
 *
 * Copyright (C) 2014-2020 Cyrille Bagard
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


#include "target.h"


#include <assert.h>
#include <inttypes.h>
#include <malloc.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>


#include "immediate.h"
#include "target-int.h"
#include "targetable-int.h"
#include "../../analysis/routine.h"
#include "../../common/extstr.h"
#include "../../common/sort.h"
#include "../../format/format.h"
#include "../../format/strsym.h"
#include "../../glibext/gbinarycursor.h"
#include "../../core/columns.h"



/* ------------------------- POINTAGE D'UN SYMBOLE EXISTANT ------------------------- */


/* Initialise la classe des opérandes ciblant des symboles. */
static void g_target_operand_class_init(GTargetOperandClass *);

/* Initialise la classe des opérandes ciblant des symboles. */
static void g_target_operand_init(GTargetOperand *);

/* Procède à l'initialisation de l'interface de ciblage. */
static void g_target_operand_targetable_interface_init(GTargetableOperandInterface *);

/* Supprime toutes les références externes. */
static void g_target_operand_dispose(GTargetOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_target_operand_finalize(GTargetOperand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Compare un opérande avec un autre. */
static int g_target_operand_compare(const GTargetOperand *, const GTargetOperand *, bool);

/* Traduit un opérande en version humainement lisible. */
static void g_target_operand_print(const GTargetOperand *, GBufferLine *);

#ifdef INCLUDE_GTK_SUPPORT

/* Construit un petit résumé concis de l'opérande. */
static char *g_target_operand_build_tooltip(const GTargetOperand *, const GLoadedBinary *);

#endif

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint g_target_operand_hash(const GTargetOperand *, bool);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_target_operand_load(GTargetOperand *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_target_operand_store(GTargetOperand *, GObjectStorage *, packed_buffer_t *);



/* ----------------------- INTERFACE DE CIBLAGE POUR OPERANDE ----------------------- */


/* Obtient l'adresse de la cible visée par un opérande. */
static bool g_target_operand_get_addr(const GTargetOperand *, const vmpa2t *, GBinFormat *, GArchProcessor *, vmpa2t *);



/* ---------------------------------------------------------------------------------- */
/*                           POINTAGE D'UN SYMBOLE EXISTANT                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un opérande de valeur numérique. */
G_DEFINE_TYPE_WITH_CODE(GTargetOperand, g_target_operand, G_TYPE_ARCH_OPERAND,
                        G_IMPLEMENT_INTERFACE(G_TYPE_TARGETABLE_OPERAND, g_target_operand_targetable_interface_init));



/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des opérandes ciblant des symboles.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_target_operand_class_init(GTargetOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);
    operand = G_ARCH_OPERAND_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_target_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_target_operand_finalize;

    operand->compare = (operand_compare_fc)g_target_operand_compare;
    operand->print = (operand_print_fc)g_target_operand_print;
#ifdef INCLUDE_GTK_SUPPORT
    operand->build_tooltip = (operand_build_tooltip_fc)g_target_operand_build_tooltip;
#endif

    operand->hash = (operand_hash_fc)g_target_operand_hash;

    operand->load = (load_operand_fc)g_target_operand_load;
    operand->store = (store_operand_fc)g_target_operand_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise la classe des opérandes ciblant des symboles.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_target_operand_init(GTargetOperand *operand)
{
    GET_TARGET_OP_EXTRA(operand)->size = MDS_UNDEFINED;

    init_vmpa(&operand->addr, VMPA_NO_PHYSICAL, VMPA_NO_VIRTUAL);

    operand->symbol = NULL;
    operand->diff = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de ciblage.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_target_operand_targetable_interface_init(GTargetableOperandInterface *iface)
{
    iface->get_addr = (get_targetable_addr_fc)g_target_operand_get_addr;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_target_operand_dispose(GTargetOperand *operand)
{
    G_OBJECT_CLASS(g_target_operand_parent_class)->dispose(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_target_operand_finalize(GTargetOperand *operand)
{
    G_OBJECT_CLASS(g_target_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a    = premier opérande à consulter.                         *
*                b    = second opérande à consulter.                          *
*                lock = précise le besoin en verrouillage.                    *
*                                                                             *
*  Description : Compare un opérande avec un autre.                           *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int g_target_operand_compare(const GTargetOperand *a, const GTargetOperand *b, bool lock)
{
    int result;                             /* Bilan à retourner           */
    tarop_extra_data_t *ea;                 /* Données insérées à modifier */
    tarop_extra_data_t *eb;                 /* Données insérées à modifier */
    GArchOperandClass *class;               /* Classe parente normalisée   */

    ea = GET_TARGET_OP_EXTRA(a);
    eb = GET_TARGET_OP_EXTRA(b);

    if (lock)
    {
        LOCK_GOBJECT_EXTRA(ea);
        LOCK_GOBJECT_EXTRA(eb);
    }

    result = sort_unsigned_long(ea->size, eb->size);

    if (result == 0)
        result = cmp_vmpa(&a->addr, &b->addr);

    if (result == 0)
    {
        if (a->symbol == NULL && b->symbol != NULL)
            result = -1;

        else if (a->symbol != NULL && b->symbol == NULL)
            result = 1;

        else if (a->symbol != NULL && b->symbol != NULL)
            result = g_binary_symbol_cmp((const GBinSymbol *[]) { a->symbol },
                                         (const GBinSymbol *[]) { b->symbol });

    }

    if (result == 0)
        result = sort_uint64_t(a->diff, b->diff);

    if (result == 0)
    {
        class = G_ARCH_OPERAND_CLASS(g_target_operand_parent_class);
        result = class->compare(G_ARCH_OPERAND(a), G_ARCH_OPERAND(b), false);
    }

    if (lock)
    {
        UNLOCK_GOBJECT_EXTRA(eb);
        UNLOCK_GOBJECT_EXTRA(ea);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à traiter.                                *
*                line    = ligne tampon où imprimer l'opérande donné.         *
*                                                                             *
*  Description : Traduit un opérande en version humainement lisible.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_target_operand_print(const GTargetOperand *operand, GBufferLine *line)
{
    char *label;                            /* Etiquette liée à un symbole */
    vmpa2t tmp;                             /* Coquille vide pour argument */
    VMPA_BUFFER(value);                     /* Adresse brute à imprimer    */
    size_t len;                             /* Taille de l'élément inséré  */
    MemoryDataSize size;                    /* Taille retenue              */

    label = g_binary_symbol_get_label(operand->symbol);

    if (operand->symbol != NULL && label != NULL)
    {
        if (operand->diff > 0)
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "<", 1, RTT_LTGT, NULL);

        g_buffer_line_append_text(line, DLC_ASSEMBLY, label, strlen(label), RTT_LABEL, G_OBJECT(operand));

        if (operand->diff > 0)
        {
            g_buffer_line_append_text(line, DLC_ASSEMBLY, "+", 1, RTT_SIGNS, G_OBJECT(operand));

            init_vmpa(&tmp, operand->diff, VMPA_NO_VIRTUAL);
            vmpa2_phys_to_string(&tmp, MDS_4_BITS, value, &len);

            g_buffer_line_append_text(line, DLC_ASSEMBLY, value, len, RTT_LABEL, G_OBJECT(operand));

            g_buffer_line_append_text(line, DLC_ASSEMBLY, ">", 1, RTT_LTGT, NULL);

        }

    }
    else
    {
        size = g_target_operand_get_size(operand);

        vmpa2_to_string(&operand->addr, size, value, &len);

        g_buffer_line_append_text(line, DLC_ASSEMBLY, value, len, RTT_LABEL, G_OBJECT(operand));

    }

    if (label != NULL)
        free(label);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : size = taille des adresse mémoire virtuelles.                *
*                addr = localisation d'un élément à retrouver.                *
*                                                                             *
*  Description : Crée un opérande réprésentant une valeur numérique.          *
*                                                                             *
*  Retour      : Instruction mise en place.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_target_operand_new(MemoryDataSize size, const vmpa2t *addr)
{
    GTargetOperand *result;                 /* Opérande à retourner        */

    result = g_object_new(G_TYPE_TARGET_OPERAND, NULL);

    assert(size != MDS_UNDEFINED);

    GET_TARGET_OP_EXTRA(result)->size = size;

    copy_vmpa(&result->addr, addr);

    return G_ARCH_OPERAND(result);

}


#ifdef INCLUDE_GTK_SUPPORT


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à consulter.                              *
*                binary  = informations relatives au binaire chargé.          *
*                                                                             *
*  Description : Construit un petit résumé concis de l'opérande.              *
*                                                                             *
*  Retour      : Chaîne de caractères à libérer après usage ou NULL.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_target_operand_build_tooltip(const GTargetOperand *operand, const GLoadedBinary *binary)
{
    char *result;                           /* Description à retourner     */
    SymbolType stype;                       /* Type de symbole identifié   */
    const mrange_t *srange;                 /* Emplacement du symbole      */
    GBufferCache *cache;                    /* Tampon de désassemblage     */
    GLineCursor *cursor;                    /* Emplacement dans un tampon  */
    size_t index;                           /* Indice de ligne à traiter   */
    GBufferLine *line;                      /* Ligne présente à l'adresse  */

    result = NULL;

    if (operand->symbol != NULL && operand->diff == 0)
    {
        stype = g_binary_symbol_get_stype(operand->symbol);

        switch (stype)
        {
            case STP_ROUTINE:
            case STP_ENTRY_POINT:
                result = g_binary_routine_build_tooltip(G_BIN_ROUTINE(operand->symbol), binary);
                break;

            case STP_RO_STRING:
            case STP_DYN_STRING:

                srange = g_binary_symbol_get_range(operand->symbol);

                cache = g_loaded_binary_get_disassembly_cache(binary);

                g_buffer_cache_rlock(cache);

                cursor = g_binary_cursor_new();
                g_binary_cursor_update(G_BINARY_CURSOR(cursor), get_mrange_addr(srange));

                index = g_buffer_cache_find_index_by_cursor(cache, cursor, true);

                g_object_unref(G_OBJECT(cursor));

                index = g_buffer_cache_look_for_flag(cache, index, BLF_HAS_CODE);

                line = g_buffer_cache_find_line_by_index(cache, index);

                if (line != NULL)
                {
                    result = g_buffer_line_get_text(line, DLC_ASSEMBLY, DLC_COUNT, true);
                    g_object_unref(G_OBJECT(line));
                }

                g_buffer_cache_runlock(cache);

                g_object_unref(G_OBJECT(cache));

                break;

            default:
                break;

        }

    }

    return result;

}


#endif


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = structure dont le contenu est à consulter.         *
*                                                                             *
*  Description : Renseigne la taille de la valeur indiquée à la construction. *
*                                                                             *
*  Retour      : Taille de la valeur représentée en mémoire.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

MemoryDataSize g_target_operand_get_size(const GTargetOperand *operand)
{
    MemoryDataSize result;                  /* Taille à retourner          */
    tarop_extra_data_t *extra;              /* Données insérées à consulter*/

    extra = GET_TARGET_OP_EXTRA(operand);

    LOCK_GOBJECT_EXTRA(extra);

    result = extra->size;

    UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande dont le contenu est à raffiner. [OUT]     *
*                format  = format du binaire d'origine à consulter.           *
*                strict  = indique la perfection attendue de la résolution.   *
*                                                                             *
*  Description : Tente une résolution de symbole.                             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_target_operand_resolve(GTargetOperand *operand, GBinFormat *format, bool strict)
{
    bool result;                            /* Bilan à retourner           */
    GBinSymbol *symbol;                     /* Facilités d'accès au symbole*/
    char *label;                            /* Désignation de la chaîne    */
#ifndef NDEBUG
    const mrange_t *range;                  /* Couverture du symbole       */
#endif

    if (strict)
        g_arch_operand_set_flag(G_ARCH_OPERAND(operand), TOF_STRICT);
    else
        g_arch_operand_unset_flag(G_ARCH_OPERAND(operand), TOF_STRICT);

    result = g_binary_format_resolve_symbol(format, &operand->addr, strict, &operand->symbol, &operand->diff);

    assert(!result || !strict || (strict && operand->diff == 0));

    /**
     * Si plusieurs chaînes se suivent, la seconde et les suivantes bénéficient
     * d'une étiquette si et seulement si elles sont détachées des précédentes
     * par un octet nul.
     *
     * S'il y a juste un retour à la ligne ("\n"), alors aucune séparation n'est
     * considérée, et le bloc de chaînes est uniforme.
     *
     * Aussi, si une référence renvoie vers une ligne de ce bloc, alors on
     * attribue à cette ligne une étiquette propre.
     */

    if (result && operand->diff == 0)
    {
        symbol = operand->symbol;

        if (G_IS_STR_SYMBOL(symbol))
        {
            label = g_binary_symbol_get_label(symbol);

            if (label != NULL)
                free(label);

            else
            {
#ifndef NDEBUG
                range = g_binary_symbol_get_range(symbol);

                assert(cmp_vmpa(&operand->addr, get_mrange_addr(range)) == 0);
#endif

                g_string_symbol_build_label(G_STR_SYMBOL(symbol), format);

            }

        }

    }

    /* Référence circulaire */
    if (operand->symbol != NULL)
        g_object_unref(operand->symbol);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande dont le contenu est à raffiner.           *
*                diff    = décalage entre le symbole et l'adresse initiale.   *
*                                                                             *
*  Description : Fournit les indications concernant le symbole associé.       *
*                                                                             *
*  Retour      : Symbole résolu ou NULL si aucun.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinSymbol *g_target_operand_get_symbol(const GTargetOperand *operand, phys_t *diff)
{
    GBinSymbol *result;                     /* Symbole associé à retourner */

    if (diff != NULL)
        *diff = operand->diff;

    result = operand->symbol;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = objet dont l'instance se veut unique.              *
*                lock    = précise le besoin en verrouillage.                 *
*                                                                             *
*  Description : Fournit l'empreinte d'un candidat à une centralisation.      *
*                                                                             *
*  Retour      : Empreinte de l'élément représenté.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static guint g_target_operand_hash(const GTargetOperand *operand, bool lock)
{
    guint result;                           /* Valeur à retourner          */
    tarop_extra_data_t *extra;              /* Données insérées à modifier */
    GArchOperandClass *class;               /* Classe parente normalisée   */

    extra = GET_TARGET_OP_EXTRA(operand);

    if (lock)
        LOCK_GOBJECT_EXTRA(extra);

    class = G_ARCH_OPERAND_CLASS(g_target_operand_parent_class);
    result = class->hash(G_ARCH_OPERAND(operand), false);

    result ^= extra->size;

    result ^= g_direct_hash(operand->symbol);

    result ^= (operand->diff & 0xffffffff);
    result ^= (operand->diff >> 32);

    if (lock)
        UNLOCK_GOBJECT_EXTRA(extra);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à constuire.                          *
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

static bool g_target_operand_load(GTargetOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    assert(false);

    /**
     * Comme ce type d'opérande peut générer de nouveaux symboles lorsque
     * sa résolution échoue, il faut appeler ces résolutions dans les contextes
     * d'origine.
     *
     * Ces contextes sont généralement le lieu de conversions de valeurs immédiates
     * en valeurs de cibles, donc la sérialisation de l'opérande conduit à
     * la sauvegarde d'un opérande de valeur immédiate de subsitution.
     *
     * La désérialisation est donc prise en compte par ce dernier type d'opérande.
     */

    result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à consulter.                          *
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

static bool g_target_operand_store(GTargetOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    MemoryDataSize size;                    /* Taille retenue              */
    GArchOperand *original;                 /* Opérande d'origine          */

    /**
     * Pour les architectures sans mémoire virtuelle, la valeur est portée
     * par la position physique.
     */

    size = g_target_operand_get_size(operand);

    if (has_virt_addr(&operand->addr))
        original = g_imm_operand_new_from_value(size, get_virt_addr(&operand->addr));
    else
        original = g_imm_operand_new_from_value(size, get_phy_addr(&operand->addr));

    result = g_object_storage_pack_object(storage, "operands", G_SERIALIZABLE_OBJECT(original), pbuf);

    g_object_unref(G_OBJECT(original));

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                         INTERFACE DE CIBLAGE POUR OPERANDE                         */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = operande à consulter.                              *
*                src     = localisation de l'instruction mère.                *
*                format  = format reconnu pour le binaire chargé.             *
*                proc    = architecture associée à ce même binaire.           *
*                addr    = localisation de la cible. [OUT]                    *
*                                                                             *
*  Description : Obtient l'adresse de la cible visée par un opérande.         *
*                                                                             *
*  Retour      : true si la cible est valide, false sinon.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_target_operand_get_addr(const GTargetOperand *operand, const vmpa2t *src, GBinFormat *format, GArchProcessor *proc, vmpa2t *addr)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    copy_vmpa(addr, &operand->addr);

    return result;

}
