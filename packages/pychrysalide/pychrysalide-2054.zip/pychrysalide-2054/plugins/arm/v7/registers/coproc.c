
/* Chrysalide - Outil d'analyse de fichiers binaires
 * coproc.c - aides auxiliaires relatives aux registres de co-processeur ARMv7
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


#include "coproc.h"


#include <stdio.h>


#include <core/columns.h>


#include "../register-int.h"



/* ------------------------- GESTION UNITAIRE DES REGISTRES ------------------------- */


/* Représentation d'un registre de co-processeur ARMv7 (instance) */
struct _GArmV7CpRegister
{
    GArmV7Register parent;                  /* Instance parente            */

};


/* Représentation d'un registre de co-processeur ARMv7 (classe) */
struct _GArmV7CpRegisterClass
{
    GArmV7RegisterClass parent;             /* Classe parente              */

};


#define MAX_REGNAME_LEN 5


/* Initialise la classe des registres de co-processeur ARMv7. */
static void g_armv7_cp_register_class_init(GArmV7CpRegisterClass *);

/* Initialise une instance de registre de co-processeur ARMv7. */
static void g_armv7_cp_register_init(GArmV7CpRegister *);

/* Supprime toutes les références externes. */
static void g_armv7_cp_register_dispose(GArmV7CpRegister *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_cp_register_finalize(GArmV7CpRegister *);

/* Traduit un registre en version humainement lisible. */
static void g_armv7_cp_register_print(const GArmV7CpRegister *, GBufferLine *);

/* Crée une réprésentation de registre de co-processeur ARMv7. */
static GArchRegister *_g_armv7_cp_register_new(uint8_t);



/* ------------------------ GESTION SOUS FORME DE SINGLETONS ------------------------ */


/* Conservation des registres utilisés */
static GArchRegister **_armv7_cp_registers = NULL;
static size_t _av7_cp_reg_count = 0;
G_LOCK_DEFINE_STATIC(_av7_cp_reg_mutex);


/* Fournit le singleton associé à un registre de co-proc. ARMv7. */
static GArchRegister *get_armv7_cp_register(uint8_t);



/* ---------------------------------------------------------------------------------- */
/*                           GESTION UNITAIRE DES REGISTRES                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une représentation d'un registre de co-processeur ARMv7. */
G_DEFINE_TYPE(GArmV7CpRegister, g_armv7_cp_register, G_TYPE_ARMV7_REGISTER);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des registres de co-processeur ARMv7.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_cp_register_class_init(GArmV7CpRegisterClass *klass)
{
    GObjectClass *object_class;             /* Autre version de la classe  */
    GArchRegisterClass *reg_class;          /* Classe de haut niveau       */

    object_class = G_OBJECT_CLASS(klass);
    reg_class = G_ARCH_REGISTER_CLASS(klass);

    object_class->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_cp_register_dispose;
    object_class->finalize = (GObjectFinalizeFunc)g_armv7_cp_register_finalize;

    reg_class->print = (reg_print_fc)g_armv7_cp_register_print;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de registre de co-processeur ARMv7.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_cp_register_init(GArmV7CpRegister *reg)
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

static void g_armv7_cp_register_dispose(GArmV7CpRegister *reg)
{
    G_OBJECT_CLASS(g_armv7_cp_register_parent_class)->dispose(G_OBJECT(reg));

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

static void g_armv7_cp_register_finalize(GArmV7CpRegister *reg)
{
    G_OBJECT_CLASS(g_armv7_cp_register_parent_class)->finalize(G_OBJECT(reg));

}


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

static void g_armv7_cp_register_print(const GArmV7CpRegister *reg, GBufferLine *line)
{
    char key[MAX_REGNAME_LEN];              /* Mot clef principal          */
    size_t klen;                            /* Taille de ce mot clef       */

    switch (G_ARM_REGISTER(reg)->index)
    {
        case 0 ... 15:
            klen = snprintf(key, MAX_REGNAME_LEN, "cp%hhu", G_ARM_REGISTER(reg)->index);
            break;
        default:
            klen = snprintf(key, MAX_REGNAME_LEN, "cp??");
            break;
    }

    g_buffer_line_append_text(line, DLC_ASSEMBLY, key, klen, RTT_REGISTER, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : index = indice du registre correspondant.                    *
*                                                                             *
*  Description : Crée une réprésentation de registre de co-processeur ARMv7.  *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchRegister *_g_armv7_cp_register_new(uint8_t index)
{
    GArmV7CpRegister *result;                /* Structure à retourner       */

    if (index > 15)
        goto bad_index;

    result = g_object_new(G_TYPE_ARMV7_CP_REGISTER, NULL);

    G_ARM_REGISTER(result)->index = index;

    return G_ARCH_REGISTER(result);

 bad_index:

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : index = indice du registre correspondant.                    *
*                                                                             *
*  Description : Crée une réprésentation de registre de co-processeur ARMv7.  *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchRegister *g_armv7_cp_register_new(uint8_t index)
{
    GArchRegister *result;                  /* Structure à retourner       */

    result = get_armv7_cp_register(index);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          GESTION SOUS FORME DE SINGLETONS                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : index = indice du registre correspondant.                    *
*                                                                             *
*  Description : Fournit le singleton associé à un registre de co-proc. ARMv7.*
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchRegister *get_armv7_cp_register(uint8_t index)
{
    GArchRegister *result;                  /* Structure à retourner       */
    size_t new_count;                       /* Nouvelle taille à considérer*/
    size_t i;                               /* Boucle de parcours          */

    G_LOCK(_av7_cp_reg_mutex);

    if (index >= _av7_cp_reg_count)
    {
        /**
         * On valide déjà le fait que le registre puisse être créé
         * avant de réaliser une allocation potentiellement énorme
         * avec un indice démesuré.
         */

        result = _g_armv7_cp_register_new(index);

        if (result == NULL)
            goto bad_index;

        new_count = index + 1;

        _armv7_cp_registers = realloc(_armv7_cp_registers, new_count * sizeof(GArchRegister *));

        for (i = _av7_cp_reg_count; i < new_count; i++)
            _armv7_cp_registers[i] = NULL;

        _av7_cp_reg_count = new_count;

    }

    else
        result = NULL;

    if (_armv7_cp_registers[index] == NULL)
    {
        if (result != NULL)
            _armv7_cp_registers[index] = result;
        else
            _armv7_cp_registers[index] = _g_armv7_cp_register_new(index);
    }

    result = _armv7_cp_registers[index];

 bad_index:

    G_UNLOCK(_av7_cp_reg_mutex);

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Vide totalement le cache des registres ARMv7.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void clean_armv7_cp_register_cache(void)
{
    size_t i;                               /* Boucle de parcours          */

    G_LOCK(_av7_cp_reg_mutex);

    for (i = 0; i < _av7_cp_reg_count; i++)
        g_clear_object(&_armv7_cp_registers[i]);

    if (_armv7_cp_registers != NULL)
        free(_armv7_cp_registers);

    _armv7_cp_registers = NULL;
    _av7_cp_reg_count = 0;

    G_UNLOCK(_av7_cp_reg_mutex);

}
