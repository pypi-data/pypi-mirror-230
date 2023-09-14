
/* Chrysalide - Outil d'analyse de fichiers binaires
 * special.c - aides auxiliaires relatives aux registres spéciaux ARMv7
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


#include "special.h"


#include <stdio.h>


#include <core/columns.h>


#include "../register-int.h"



/* ------------------------- GESTION UNITAIRE DES REGISTRES ------------------------- */


/* Représentation d'un registre spécial ARMv7 (instance) */
struct _GArmV7SpecialRegister
{
    GArmV7Register parent;                  /* Instance parente            */

};

/* Représentation d'un registre spécial ARMv7 (classe) */
struct _GArmV7SpecialRegisterClass
{
    GArmV7RegisterClass parent;             /* Classe parente     -         */

};


#define MAX_REGNAME_LEN 12


/* Initialise la classe des registres spéciaux ARMv7. */
static void g_armv7_special_register_class_init(GArmV7SpecialRegisterClass *);

/* Initialise une instance de registre spécial ARMv7. */
static void g_armv7_special_register_init(GArmV7SpecialRegister *);

/* Supprime toutes les références externes. */
static void g_armv7_special_register_dispose(GArmV7SpecialRegister *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_special_register_finalize(GArmV7SpecialRegister *);

/* Traduit un registre en version humainement lisible. */
static void g_armv7_special_register_print(const GArmV7SpecialRegister *, GBufferLine *);

/* Crée une réprésentation de registre spécial ARMv7. */
static GArchRegister *_g_armv7_special_register_new(SpecRegTarget);



/* ------------------------ GESTION SOUS FORME DE SINGLETONS ------------------------ */


/* Conservation des registres utilisés */
static GArchRegister **_armv7_special_registers = NULL;
static size_t _av7_special_reg_count = 0;
G_LOCK_DEFINE_STATIC(_av7_special_reg_mutex);


/* Fournit le singleton associé à un registre spécial ARMv7. */
static GArchRegister *get_armv7_special_register(SpecRegTarget);



/* ---------------------------------------------------------------------------------- */
/*                           GESTION UNITAIRE DES REGISTRES                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une représentation d'un registre spécial ARMv7. */
G_DEFINE_TYPE(GArmV7SpecialRegister, g_armv7_special_register, G_TYPE_ARMV7_REGISTER);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des registres spéciaux ARMv7.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_special_register_class_init(GArmV7SpecialRegisterClass *klass)
{
    GObjectClass *object_class;             /* Autre version de la classe  */
    GArchRegisterClass *reg_class;          /* Classe de haut niveau       */

    object_class = G_OBJECT_CLASS(klass);
    reg_class = G_ARCH_REGISTER_CLASS(klass);

    object_class->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_special_register_dispose;
    object_class->finalize = (GObjectFinalizeFunc)g_armv7_special_register_finalize;

    reg_class->print = (reg_print_fc)g_armv7_special_register_print;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de registre spécial ARMv7.           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_special_register_init(GArmV7SpecialRegister *reg)
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

static void g_armv7_special_register_dispose(GArmV7SpecialRegister *reg)
{
    G_OBJECT_CLASS(g_armv7_special_register_parent_class)->dispose(G_OBJECT(reg));

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

static void g_armv7_special_register_finalize(GArmV7SpecialRegister *reg)
{
    G_OBJECT_CLASS(g_armv7_special_register_parent_class)->finalize(G_OBJECT(reg));

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

static void g_armv7_special_register_print(const GArmV7SpecialRegister *reg, GBufferLine *line)
{
    SpecRegTarget target;                   /* Registre ciblé              */
    char key[MAX_REGNAME_LEN];              /* Mot clef principal          */
    size_t klen;                            /* Taille de ce mot clef       */

    target = G_ARM_REGISTER(reg)->index;

    switch (target)
    {
        case SRT_APSR:
            klen = snprintf(key, MAX_REGNAME_LEN, "APSR");
            break;

        case SRT_CPSR:
            klen = snprintf(key, MAX_REGNAME_LEN, "CPSR");
            break;

        case SRT_SPSR:
            klen = snprintf(key, MAX_REGNAME_LEN, "SPSR");
            break;

        case SRT_APSR_NZCVQ:
            klen = snprintf(key, MAX_REGNAME_LEN, "APSR_nzcvq");
            break;

        case SRT_APSR_G:
            klen = snprintf(key, MAX_REGNAME_LEN, "APSR_g");
            break;

        case SRT_APSR_NZCVQG:
            klen = snprintf(key, MAX_REGNAME_LEN, "APSR_nzcvqg");
            break;

        case SRT_FPSID:
            klen = snprintf(key, MAX_REGNAME_LEN, "FPSID");
            break;

        case SRT_FPSCR:
            klen = snprintf(key, MAX_REGNAME_LEN, "FPSCR");
            break;

        case SRT_MVFR1:
            klen = snprintf(key, MAX_REGNAME_LEN, "MVFR1");
            break;

        case SRT_MVFR0:
            klen = snprintf(key, MAX_REGNAME_LEN, "MVFR0");
            break;

        case SRT_FPEXC:
            klen = snprintf(key, MAX_REGNAME_LEN, "FPEXC");
            break;

        default:
            klen = snprintf(key, MAX_REGNAME_LEN, "???");
            break;

    }

    g_buffer_line_append_text(line, DLC_ASSEMBLY, key, klen, RTT_REGISTER, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = registre effectivement ciblé.                       *
*                                                                             *
*  Description : Crée une réprésentation de registre spécial ARMv7.           *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchRegister *_g_armv7_special_register_new(SpecRegTarget target)
{
    GArmV7SpecialRegister *result;                 /* Structure à retourner       */

    if (target >= SRT_CPSR)
        goto bad_index;

    result = g_object_new(G_TYPE_ARMV7_SPECIAL_REGISTER, NULL);

    G_ARM_REGISTER(result)->index = target;

    return G_ARCH_REGISTER(result);

 bad_index:

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = registre effectivement ciblé.                       *
*                                                                             *
*  Description : Crée une réprésentation de registre spécial ARMv7.           *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchRegister *g_armv7_special_register_new(SpecRegTarget target)
{
    GArchRegister *result;                  /* Structure à retourner       */

    result = get_armv7_special_register(target);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          GESTION SOUS FORME DE SINGLETONS                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : target = registre effectivement ciblé.                       *
*                                                                             *
*  Description : Fournit le singleton associé à un registre spécial ARMv7.    *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchRegister *get_armv7_special_register(SpecRegTarget target)
{
    GArchRegister *result;                  /* Structure à retourner       */
    size_t new_count;                       /* Nouvelle taille à considérer*/
    size_t i;                               /* Boucle de parcours          */

    G_LOCK(_av7_special_reg_mutex);

    if (target >= _av7_special_reg_count)
    {
        /**
         * On valide déjà le fait que le registre puisse être créé
         * avant de réaliser une allocation potentiellement énorme
         * avec un indice démesuré.
         */

        result = _g_armv7_special_register_new(target);

        if (result == NULL)
            goto bad_index;

        new_count = target + 1;

        _armv7_special_registers = realloc(_armv7_special_registers, new_count * sizeof(GArchRegister *));

        for (i = _av7_special_reg_count; i < new_count; i++)
            _armv7_special_registers[i] = NULL;

        _av7_special_reg_count = new_count;

    }

    else
        result = NULL;

    if (_armv7_special_registers[target] == NULL)
    {
        if (result != NULL)
            _armv7_special_registers[target] = result;
        else
            _armv7_special_registers[target] = _g_armv7_special_register_new(target);
    }

    result = _armv7_special_registers[target];

 bad_index:

    G_UNLOCK(_av7_special_reg_mutex);

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Vide totalement le cache des registres spéciaux ARMv7.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void clean_armv7_special_register_cache(void)
{
    size_t i;                               /* Boucle de parcours          */

    G_LOCK(_av7_special_reg_mutex);

    for (i = 0; i < _av7_special_reg_count; i++)
        g_clear_object(&_armv7_special_registers[i]);

    if (_armv7_special_registers != NULL)
        free(_armv7_special_registers);

    _armv7_special_registers = NULL;
    _av7_special_reg_count = 0;

    G_UNLOCK(_av7_special_reg_mutex);

}
