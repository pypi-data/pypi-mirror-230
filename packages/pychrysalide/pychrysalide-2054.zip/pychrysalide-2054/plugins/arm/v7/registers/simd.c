
/* Chrysalide - Outil d'analyse de fichiers binaires
 * simd.c - aides auxiliaires relatives aux registres SIMD ARMv7
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "simd.h"


#include <assert.h>
#include <stdio.h>


#include <core/columns.h>


#include "../register-int.h"



/* ------------------------- GESTION UNITAIRE DES REGISTRES ------------------------- */


/* Représentation d'un registre ARMv7 (instance) */
struct _GArmV7SIMDRegister
{
    GArmV7Register parent;                  /* Instance parente            */

    SIMDRegisterMapping mapping;            /* Type de registre            */

};

/* Représentation d'un registre ARMv7 (classe) */
struct _GArmV7SIMDRegisterClass
{
    GArmV7RegisterClass parent;             /* Classe parente              */

};


#define MAX_REGNAME_LEN 4


/* Initialise la classe des registres SIMD ARMv7. */
static void g_armv7_simd_register_class_init(GArmV7SIMDRegisterClass *);

/* Initialise une instance de registre SIMD ARMv7. */
static void g_armv7_simd_register_init(GArmV7SIMDRegister *);

/* Supprime toutes les références externes. */
static void g_armv7_simd_register_dispose(GArmV7SIMDRegister *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_simd_register_finalize(GArmV7SIMDRegister *);

/* Crée une réprésentation de registre SIMD ARMv7. */
static GArchRegister *_g_armv7_simd_register_new(SIMDRegisterMapping, uint8_t);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */

/* Traduit un registre en version humainement lisible. */
static void g_armv7_simd_register_print(const GArmV7SIMDRegister *, GBufferLine *);

/* Charge un contenu depuis une mémoire tampon. */
static bool g_armv7_simd_register_load(GArmV7SIMDRegister *, GObjectStorage *, packed_buffer_t *);

/* Sauvegarde un contenu dans une mémoire tampon. */
static bool g_armv7_simd_register_store(GArmV7SIMDRegister *, GObjectStorage *, packed_buffer_t *);



/* ------------------------ GESTION SOUS FORME DE SINGLETONS ------------------------ */


/* Conservation des registres utilisés */
static GArchRegister **_armv7_simd_registers[SRM_COUNT] = { NULL, NULL, NULL };
static size_t _av7_simd_reg_count[SRM_COUNT] = { 0, 0, 0 };
G_LOCK_DEFINE_STATIC(_av7_simd_reg_mutex);


/* Fournit le singleton associé à un registre SIMD ARMv7. */
static GArchRegister *get_armv7_simd_register(SIMDRegisterMapping, uint8_t);



/* ---------------------------------------------------------------------------------- */
/*                           GESTION UNITAIRE DES REGISTRES                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une représentation d'un registre SIMD ARMv7. */
G_DEFINE_TYPE(GArmV7SIMDRegister, g_armv7_simd_register, G_TYPE_ARMV7_REGISTER);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des registres SIMD ARMv7.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_simd_register_class_init(GArmV7SIMDRegisterClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GArchRegisterClass *reg;                /* Classe de haut niveau       */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_simd_register_dispose;
    object->finalize = (GObjectFinalizeFunc)g_armv7_simd_register_finalize;

    reg = G_ARCH_REGISTER_CLASS(klass);

    reg->print = (reg_print_fc)g_armv7_simd_register_print;

    reg->load = (load_register_fc)g_armv7_simd_register_load;
    reg->store = (store_register_fc)g_armv7_simd_register_store;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de registre SIMD ARMv7.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_simd_register_init(GArmV7SIMDRegister *reg)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_simd_register_dispose(GArmV7SIMDRegister *reg)
{
    G_OBJECT_CLASS(g_armv7_simd_register_parent_class)->dispose(G_OBJECT(reg));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance d'objet GLib à traiter.                       *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_simd_register_finalize(GArmV7SIMDRegister *reg)
{
    G_OBJECT_CLASS(g_armv7_simd_register_parent_class)->finalize(G_OBJECT(reg));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : mapping = type de registre demandé.                          *
*                index   = indice du registre correspondant.                  *
*                                                                             *
*  Description : Crée une réprésentation de registre SIMD ARMv7.              *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchRegister *_g_armv7_simd_register_new(SIMDRegisterMapping mapping, uint8_t index)
{
    GArmV7SIMDRegister *result;             /* Structure à retourner       */
    uint8_t max;                            /* Borne supérieure de limite  */

    switch (mapping)
    {
        case SRM_SINGLE_WORD:
            max = 31;
            break;

        case SRM_DOUBLE_WORD:
            max = 31;
            break;

        case SRM_QUAD_WORD:
            max = 15;
            break;

        default:
            assert(false);
            goto bad_mapping;
            break;

    }

    if (index > max)
        goto bad_index;

    result = g_object_new(G_TYPE_ARMV7_SIMD_REGISTER, NULL);

    G_ARM_REGISTER(result)->index = index;

    result->mapping = mapping;

    return G_ARCH_REGISTER(result);

 bad_mapping:
 bad_index:

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : mapping = type de registre demandé.                          *
*                index   = indice du registre correspondant.                  *
*                                                                             *
*  Description : Crée une réprésentation de registre SIMD ARMv7.              *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchRegister *g_armv7_simd_register_new(SIMDRegisterMapping mapping, uint8_t index)
{
    GArchRegister *result;                  /* Structure à retourner       */

    result = get_armv7_simd_register(mapping, index);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : reg  = registre à transcrire.                                *
*                line = ligne tampon où imprimer l'opérande donné.            *
*                                                                             *
*  Description : Traduit un registre en version humainement lisible.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_simd_register_print(const GArmV7SIMDRegister *reg, GBufferLine *line)
{
    char key[MAX_REGNAME_LEN];              /* Mot clef principal          */
    size_t klen;                            /* Taille de ce mot clef       */

    switch (reg->mapping)
    {
        case SRM_SINGLE_WORD:
            klen = snprintf(key, MAX_REGNAME_LEN, "s%hhu", G_ARM_REGISTER(reg)->index);
            break;

        case SRM_DOUBLE_WORD:
            klen = snprintf(key, MAX_REGNAME_LEN, "d%hhu", G_ARM_REGISTER(reg)->index);
            break;

        case SRM_QUAD_WORD:
            klen = snprintf(key, MAX_REGNAME_LEN, "q%hhu", G_ARM_REGISTER(reg)->index);
            break;

        default:
            assert(false);
            klen = snprintf(key, MAX_REGNAME_LEN, "x??");
            break;

    }

    g_buffer_line_append_text(line, DLC_ASSEMBLY, key, klen, RTT_REGISTER, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg     = élément GLib à constuire.                          *
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

static bool g_armv7_simd_register_load(GArmV7SIMDRegister *reg, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchRegisterClass *parent;             /* Classe parente à consulter  */
    uleb128_t value;                        /* Valeur à charger            */

    parent = G_ARCH_REGISTER_CLASS(g_armv7_simd_register_parent_class);

    result = parent->load(G_ARCH_REGISTER(reg), storage, pbuf);

    if (result)
    {
        result = unpack_uleb128(&value, pbuf);

        if (result)
            reg->mapping = value;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg     = élément GLib à consulter.                          *
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

static bool g_armv7_simd_register_store(GArmV7SIMDRegister *reg, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GArchRegisterClass *parent;             /* Classe parente à consulter  */

    parent = G_ARCH_REGISTER_CLASS(g_armv7_simd_register_parent_class);

    result = parent->store(G_ARCH_REGISTER(reg), storage, pbuf);

    if (result)
        result = pack_uleb128((uleb128_t []){ reg->mapping }, pbuf);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          GESTION SOUS FORME DE SINGLETONS                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : mapping = type de registre demandé.                          *
*                index   = indice du registre correspondant.                  *
*                                                                             *
*  Description : Fournit le singleton associé à un registre SIMD ARMv7.       *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchRegister *get_armv7_simd_register(SIMDRegisterMapping mapping, uint8_t index)
{
    GArchRegister *result;                  /* Structure à retourner       */
    size_t new_count;                       /* Nouvelle taille à considérer*/
    size_t i;                               /* Boucle de parcours          */

    assert(mapping < SRM_COUNT);

    G_LOCK(_av7_simd_reg_mutex);

    if (index >= _av7_simd_reg_count[mapping])
    {
        /**
         * On valide déjà le fait que le registre puisse être créé
         * avant de réaliser une allocation potentiellement énorme
         * avec un indice démesuré.
         */

        result = _g_armv7_simd_register_new(mapping, index);

        if (result == NULL)
            goto bad_index;

        new_count = index + 1;

        _armv7_simd_registers[mapping] = realloc(_armv7_simd_registers[mapping],
                                                 new_count * sizeof(GArchRegister *));

        for (i = _av7_simd_reg_count[mapping]; i < new_count; i++)
            _armv7_simd_registers[mapping][i] = NULL;

        _av7_simd_reg_count[mapping] = new_count;

    }

    else
        result = NULL;

    if (_armv7_simd_registers[mapping][index] == NULL)
    {
        if (result != NULL)
            _armv7_simd_registers[mapping][index] = result;
        else
            _armv7_simd_registers[mapping][index] = _g_armv7_simd_register_new(mapping, index);
    }

    result = _armv7_simd_registers[mapping][index];

 bad_index:

    G_UNLOCK(_av7_simd_reg_mutex);

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Vide totalement le cache des registres SIMD ARMv7.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void clean_armv7_simd_register_cache(void)
{
    SIMDRegisterMapping i;                  /* Boucle de parcours #1       */
    size_t k;                               /* Boucle de parcours #2       */

    G_LOCK(_av7_simd_reg_mutex);

    for (i = 0; i < SRM_COUNT; i++)
    {
        for (k = 0; k < _av7_simd_reg_count[i]; k++)
            g_clear_object(&_armv7_simd_registers[i][k]);

        if (_armv7_simd_registers[i] != NULL)
            free(_armv7_simd_registers[i]);

        _armv7_simd_registers[i] = NULL;
        _av7_simd_reg_count[i] = 0;

    }

    G_UNLOCK(_av7_simd_reg_mutex);

}
