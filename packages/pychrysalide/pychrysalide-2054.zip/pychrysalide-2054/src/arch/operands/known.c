
/* Chrysalide - Outil d'analyse de fichiers binaires
 * known.c - opérandes représentant des valeurs numériques avec sémantique
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#include "known.h"


#include <assert.h>
#include <malloc.h>
#include <string.h>


#include "immediate-int.h"
#include "rename-int.h"
#include "../../analysis/db/misc/rlestr.h"
#include "../../core/columns.h"
#include "../../core/logs.h"



/* ----------------------- REMPLACEMENT DE VALEURS IMMEDIATES ----------------------- */


/* Définition d'un remplacement d'opérande de valeur numérique (instance) */
struct _GKnownImmOperand
{
    GImmOperand parent;                     /* Instance parente            */

    char *alt_text;                         /* Alternative humaine         */

};

/* Définition d'un remplacement d'opérande de valeur numérique (classe) */
struct _GKnownImmOperandClass
{
    GImmOperandClass parent;                /* Classe parente              */

};


/* Initialise la classe des remplacements d'opérandes. */
static void g_known_imm_operand_class_init(GKnownImmOperandClass *);

/* Initialise un remplacement d'opérande de valeur immédiate. */
static void g_known_imm_operand_init(GKnownImmOperand *);

/* Procède à l'initialisation de l'interface de renommage. */
static void g_known_imm_operand_renamed_interface_init(GRenamedOperandInterface *);

/* Supprime toutes les références externes. */
static void g_known_imm_operand_dispose(GKnownImmOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_known_imm_operand_finalize(GKnownImmOperand *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Compare un opérande avec un autre. */
static int g_known_imm_operand_compare(const GKnownImmOperand *, const GKnownImmOperand *, bool);

/* Traduit un opérande en version humainement lisible. */
static void g_known_imm_operand_print(const GKnownImmOperand *, GBufferLine *);

/* Fournit l'empreinte d'un candidat à une centralisation. */
static guint g_known_imm_operand_hash(const GKnownImmOperand *, bool);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_known_imm_operand_load(GKnownImmOperand *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_known_imm_operand_store(GKnownImmOperand *, GObjectStorage *, packed_buffer_t *);



/* ------------------------- AFFICHAGE D'UN CONTENU RENOMME ------------------------- */


/* Fournit un texte comme représentation alternative d'opérande. */
static const char *g_known_imm_operand_get_text(const GKnownImmOperand *);



/* ---------------------------------------------------------------------------------- */
/*                         REMPLACEMENT DE VALEURS IMMEDIATES                         */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un remplacemet d'opérande de valeur numérique. */
G_DEFINE_TYPE_WITH_CODE(GKnownImmOperand, g_known_imm_operand, G_TYPE_IMM_OPERAND,
                        G_IMPLEMENT_INTERFACE(G_TYPE_RENAMED_OPERAND, g_known_imm_operand_renamed_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des remplacements d'opérandes.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_known_imm_operand_class_init(GKnownImmOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchOperandClass *operand;             /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);
    operand = G_ARCH_OPERAND_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_known_imm_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_known_imm_operand_finalize;

    operand->compare = (operand_compare_fc)g_known_imm_operand_compare;
    operand->print = (operand_print_fc)g_known_imm_operand_print;

    operand->hash = (operand_hash_fc)g_known_imm_operand_hash;

    operand->load = (load_operand_fc)g_known_imm_operand_load;
    operand->store = (store_operand_fc)g_known_imm_operand_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise un remplacement d'opérande de valeur immédiate.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_known_imm_operand_init(GKnownImmOperand *operand)
{
    operand->alt_text = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de renommage.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_known_imm_operand_renamed_interface_init(GRenamedOperandInterface *iface)
{
    iface->get_text = (get_renamed_text_fc)g_known_imm_operand_get_text;

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

static void g_known_imm_operand_dispose(GKnownImmOperand *operand)
{
    if (operand->alt_text != NULL)
        free(operand->alt_text);

    G_OBJECT_CLASS(g_known_imm_operand_parent_class)->dispose(G_OBJECT(operand));

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

static void g_known_imm_operand_finalize(GKnownImmOperand *operand)
{
    G_OBJECT_CLASS(g_known_imm_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : old = opérande à venir copier avant son remplacement.        *
*                alt = texte alternatif à présenter pour l'impression.        *
*                                                                             *
*  Description : Crée un opérande remplaçant visuellement une valeur.         *
*                                                                             *
*  Retour      : Instruction mise en place.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_known_imm_operand_new(const GImmOperand *old, const char *alt)
{
    GKnownImmOperand *result;               /* Remplacement à retourner    */
    immop_extra_data_t *src;                /* Données insérées à consulter*/
    immop_extra_data_t *dest;               /* Données insérées à modifier */

    result = g_object_new(G_TYPE_KNOWN_IMM_OPERAND, NULL);

    result->parent.raw = old->raw;

    src = GET_IMM_OP_EXTRA(old);
    dest = GET_IMM_OP_EXTRA(&result->parent);

    LOCK_GOBJECT_EXTRA(src);

    *(&dest->parent) = *(&src->parent);

    dest->size = src->size;

    dest->def_display = src->def_display;
    dest->display = src->display;

    UNLOCK_GOBJECT_EXTRA(src);

    result->alt_text = strdup(alt);

    return G_ARCH_OPERAND(result);

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


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

static int g_known_imm_operand_compare(const GKnownImmOperand *a, const GKnownImmOperand *b, bool lock)
{
    int result;                             /* Bilan à retourner           */
    immop_extra_data_t *ea;                 /* Données insérées à consulter*/
    immop_extra_data_t *eb;                 /* Données insérées à consulter*/
    GArchOperandClass *class;               /* Classe parente normalisée   */

    ea = GET_IMM_OP_EXTRA(G_IMM_OPERAND(a));
    eb = GET_IMM_OP_EXTRA(G_IMM_OPERAND(b));

    if (lock)
    {
        LOCK_GOBJECT_EXTRA(ea);
        LOCK_GOBJECT_EXTRA(eb);
    }

    result = strcmp(a->alt_text, b->alt_text);

    if (result == 0)
    {
        class = G_ARCH_OPERAND_CLASS(g_known_imm_operand_parent_class);
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

static void g_known_imm_operand_print(const GKnownImmOperand *operand, GBufferLine *line)
{
    size_t len;                             /* Taille de l'élément inséré  */

    len = strlen(operand->alt_text);

    g_buffer_line_append_text(line, DLC_ASSEMBLY, operand->alt_text, len, RTT_IMMEDIATE, G_OBJECT(operand));

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

static guint g_known_imm_operand_hash(const GKnownImmOperand *operand, bool lock)
{
    guint result;                           /* Valeur à retourner          */
    immop_extra_data_t *extra;              /* Données insérées à consulter*/
    GArchOperandClass *class;               /* Classe parente normalisée   */

    extra = GET_IMM_OP_EXTRA(G_IMM_OPERAND(operand));

    if (lock)
        LOCK_GOBJECT_EXTRA(extra);

    class = G_ARCH_OPERAND_CLASS(g_known_imm_operand_parent_class);
    result = class->hash(G_ARCH_OPERAND(operand), false);

    result ^= g_str_hash(operand->alt_text);

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

static bool g_known_imm_operand_load(GKnownImmOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    rle_string str;                         /* Chaîne à charger            */

    parent = G_ARCH_OPERAND_CLASS(g_known_imm_operand_parent_class);

    result = parent->load(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
    {
        setup_empty_rle_string(&str);

        result = unpack_rle_string(&str, pbuf);

        if (result)
        {
            if (get_rle_string(&str) != NULL)
                operand->alt_text = strdup(get_rle_string(&str));

            exit_rle_string(&str);

        }

    }

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

static bool g_known_imm_operand_store(GKnownImmOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    rle_string str;                         /* Chaîne à conserver          */

    parent = G_ARCH_OPERAND_CLASS(g_known_imm_operand_parent_class);

    result = parent->store(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
    {
        init_static_rle_string(&str, operand->alt_text);

        result = pack_rle_string(&str, pbuf);

        exit_rle_string(&str);

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                           AFFICHAGE D'UN CONTENU RENOMME                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = operande à consulter.                              *
*                                                                             *
*  Description : Fournit un texte comme représentation alternative d'opérande.*
*                                                                             *
*  Retour      : Chaîne de caractère de représentation alternative.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static const char *g_known_imm_operand_get_text(const GKnownImmOperand *operand)
{
    const char *result;                     /* Texte à retourner           */

    result = operand->alt_text;

    return result;

}
