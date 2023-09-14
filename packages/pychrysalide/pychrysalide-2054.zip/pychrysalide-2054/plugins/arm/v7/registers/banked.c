
/* Chrysalide - Outil d'analyse de fichiers binaires
 * banked.c - aides auxiliaires relatives aux registres de banque ARMv7
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


#include "banked.h"


#include <stdio.h>


#include <core/columns.h>


#include "../register-int.h"



/* ------------------------- GESTION UNITAIRE DES REGISTRES ------------------------- */


/* Représentation d'un registre de banque ARMv7 (instance) */
struct _GArmV7BankedRegister
{
    GArmV7Register parent;                  /* Instance parente            */

};

/* Représentation d'un registre de banque ARMv7 (classe) */
struct _GArmV7BankedRegisterClass
{
    GArmV7RegisterClass parent;             /* Classe parente              */

};


#define MAX_REGNAME_LEN 9


/* Initialise la classe des registres de banque ARMv7. */
static void g_armv7_banked_register_class_init(GArmV7BankedRegisterClass *);

/* Initialise une instance de registre de banque ARMv7. */
static void g_armv7_banked_register_init(GArmV7BankedRegister *);

/* Supprime toutes les références externes. */
static void g_armv7_banked_register_dispose(GArmV7BankedRegister *);

/* Procède à la libération totale de la mémoire. */
static void g_armv7_banked_register_finalize(GArmV7BankedRegister *);

/* Traduit un registre en version humainement lisible. */
static void g_armv7_banked_register_print(const GArmV7BankedRegister *, GBufferLine *);

/* Convertit en indice des paramètres d'encodage. */
static BankedRegisterTarget convert_r_sysm_to_target(uint8_t, uint8_t);

/* Crée une réprésentation de registre de banque ARMv7. */
static GArchRegister *_g_armv7_banked_register_new(BankedRegisterTarget);



/* ------------------------ GESTION SOUS FORME DE SINGLETONS ------------------------ */


/* Conservation des registres utilisés */
static GArchRegister **_armv7_banked_registers = NULL;
static size_t _av7_banked_reg_count = 0;
G_LOCK_DEFINE_STATIC(_av7_banked_reg_mutex);


/* Fournit le singleton associé à un registre de banque ARMv7. */
static GArchRegister *get_armv7_banked_register(BankedRegisterTarget);



/* ---------------------------------------------------------------------------------- */
/*                           GESTION UNITAIRE DES REGISTRES                           */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une représentation d'un registre de banque ARMv7. */
G_DEFINE_TYPE(GArmV7BankedRegister, g_armv7_banked_register, G_TYPE_ARMV7_REGISTER);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des registres de banque ARMv7.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_banked_register_class_init(GArmV7BankedRegisterClass *klass)
{
    GObjectClass *object_class;             /* Autre version de la classe  */
    GArchRegisterClass *reg_class;          /* Classe de haut niveau       */

    object_class = G_OBJECT_CLASS(klass);
    reg_class = G_ARCH_REGISTER_CLASS(klass);

    object_class->dispose = (GObjectFinalizeFunc/* ! */)g_armv7_banked_register_dispose;
    object_class->finalize = (GObjectFinalizeFunc)g_armv7_banked_register_finalize;

    reg_class->print = (reg_print_fc)g_armv7_banked_register_print;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = instance à initialiser.                                *
*                                                                             *
*  Description : Initialise une instance de registre de banque ARMv7.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_armv7_banked_register_init(GArmV7BankedRegister *reg)
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

static void g_armv7_banked_register_dispose(GArmV7BankedRegister *reg)
{
    G_OBJECT_CLASS(g_armv7_banked_register_parent_class)->dispose(G_OBJECT(reg));

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

static void g_armv7_banked_register_finalize(GArmV7BankedRegister *reg)
{
    G_OBJECT_CLASS(g_armv7_banked_register_parent_class)->finalize(G_OBJECT(reg));

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

static void g_armv7_banked_register_print(const GArmV7BankedRegister *reg, GBufferLine *line)
{
    BankedRegisterTarget target;            /* Registre ciblé              */
    char key[MAX_REGNAME_LEN];              /* Mot clef principal          */
    size_t klen;                            /* Taille de ce mot clef       */

    target = G_ARM_REGISTER(reg)->index;

    switch (target)
    {
        case BRT_R8_USR:
            klen = snprintf(key, MAX_REGNAME_LEN, "R8_usr");
            break;
        case BRT_R9_USR:
            klen = snprintf(key, MAX_REGNAME_LEN, "R9_usr");
            break;
        case BRT_R10_USR:
            klen = snprintf(key, MAX_REGNAME_LEN, "R10_usr");
            break;
        case BRT_R11_USR:
            klen = snprintf(key, MAX_REGNAME_LEN, "R11_usr");
            break;
        case BRT_R12_USR:
            klen = snprintf(key, MAX_REGNAME_LEN, "R12_usr");
            break;
        case BRT_SP_USR:
            klen = snprintf(key, MAX_REGNAME_LEN, "SP_usr");
            break;
        case BRT_LR_USR:
            klen = snprintf(key, MAX_REGNAME_LEN, "LR_usr");
            break;

        case BRT_R8_FIQ:
            klen = snprintf(key, MAX_REGNAME_LEN, "R8_fiq");
            break;
        case BRT_R9_FIQ:
            klen = snprintf(key, MAX_REGNAME_LEN, "R9_fiq");
            break;
        case BRT_R10_FIQ:
            klen = snprintf(key, MAX_REGNAME_LEN, "R10_fiq");
            break;
        case BRT_R11_FIQ:
            klen = snprintf(key, MAX_REGNAME_LEN, "R11_fiq");
            break;
        case BRT_R12_FIQ:
            klen = snprintf(key, MAX_REGNAME_LEN, "R12_fiq");
            break;
        case BRT_SP_FIQ:
            klen = snprintf(key, MAX_REGNAME_LEN, "SP_fiq");
            break;
        case BRT_LR_FIQ:
            klen = snprintf(key, MAX_REGNAME_LEN, "LR_fiq");
            break;

        case BRT_LR_IRQ:
            klen = snprintf(key, MAX_REGNAME_LEN, "LR_irq");
            break;
        case BRT_SP_IRQ:
            klen = snprintf(key, MAX_REGNAME_LEN, "SP_irq");
            break;
        case BRT_LR_SVC:
            klen = snprintf(key, MAX_REGNAME_LEN, "LR_svc");
            break;
        case BRT_SP_SVC:
            klen = snprintf(key, MAX_REGNAME_LEN, "SP_svc");
            break;
        case BRT_LR_ABT:
            klen = snprintf(key, MAX_REGNAME_LEN, "LR_abt");
            break;
        case BRT_SP_ABT:
            klen = snprintf(key, MAX_REGNAME_LEN, "SP_abt");
            break;
        case BRT_LR_UND:
            klen = snprintf(key, MAX_REGNAME_LEN, "LR_und");
            break;
        case BRT_SP_UND:
            klen = snprintf(key, MAX_REGNAME_LEN, "SP_und");
            break;

        case BRT_LR_MON:
            klen = snprintf(key, MAX_REGNAME_LEN, "LR_mon");
            break;
        case BRT_SP_MON:
            klen = snprintf(key, MAX_REGNAME_LEN, "SP_mon");
            break;
        case BRT_ELR_HYP:
            klen = snprintf(key, MAX_REGNAME_LEN, "ELR_hyp");
            break;
        case BRT_SP_HYP:
            klen = snprintf(key, MAX_REGNAME_LEN, "SP_hyp");
            break;

        case BRT_SPSR_IRQ:
            klen = snprintf(key, MAX_REGNAME_LEN, "SPSR_irq");
            break;
        case BRT_SPSR_SVC:
            klen = snprintf(key, MAX_REGNAME_LEN, "SPSR_svc");
            break;

        default:
            klen = snprintf(key, MAX_REGNAME_LEN, "???");
            break;

    }

    g_buffer_line_append_text(line, DLC_ASSEMBLY, key, klen, RTT_REGISTER, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : r    = premier champ à interpréter.                          *
*                sysm = second champ à interpréter.                           *
*                                                                             *
*  Description : Convertit en indice des paramètres d'encodage.               *
*                                                                             *
*  Retour      : Registre ciblé ou BRT_COUNT en cas d'invalidité.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static BankedRegisterTarget convert_r_sysm_to_target(uint8_t r, uint8_t sysm)
{
    BankedRegisterTarget result;            /* Cible effective à retourner */
    uint8_t sysm_20;                        /* Décomposition en bits #1    */
    uint8_t sysm_43;                        /* Décomposition en bits #2    */

    result = BRT_COUNT;

    sysm_20 = (sysm & 0x3);
    sysm_43 = (sysm & 0x18) >> 3;

    if (r == 0)
    {
        switch (sysm_43)
        {
            case 0b00:
                switch (sysm_20)
                {
                    case 0b000:
                        result = BRT_R8_USR;
                        break;
                    case 0b001:
                        result = BRT_R9_USR;
                        break;
                    case 0b010:
                        result = BRT_R10_USR;
                        break;
                    case 0b011:
                        result = BRT_R11_USR;
                        break;
                    case 0b100:
                        result = BRT_R12_USR;
                        break;
                    case 0b101:
                        result = BRT_SP_USR;
                        break;
                    case 0b110:
                        result = BRT_LR_USR;
                        break;
                }
                break;

            case 0b01:
                switch (sysm_20)
                {
                    case 0b000:
                        result = BRT_R8_FIQ;
                        break;
                    case 0b001:
                        result = BRT_R9_FIQ;
                        break;
                    case 0b010:
                        result = BRT_R10_FIQ;
                        break;
                    case 0b011:
                        result = BRT_R11_FIQ;
                        break;
                    case 0b100:
                        result = BRT_R12_FIQ;
                        break;
                    case 0b101:
                        result = BRT_SP_FIQ;
                        break;
                    case 0b110:
                        result = BRT_LR_FIQ;
                        break;
                }
                break;

            case 0b10:
                switch (sysm_20)
                {
                    case 0b000:
                        result = BRT_LR_IRQ;
                        break;
                    case 0b001:
                        result = BRT_SP_IRQ;
                        break;
                    case 0b010:
                        result = BRT_LR_SVC;
                        break;
                    case 0b011:
                        result = BRT_SP_SVC;
                        break;
                    case 0b100:
                        result = BRT_LR_ABT;
                        break;
                    case 0b101:
                        result = BRT_SP_ABT;
                        break;
                    case 0b110:
                        result = BRT_LR_UND;
                        break;
                    case 0b111:
                        result = BRT_SP_UND;
                        break;
                }
                break;

            case 0b11:
                switch (sysm_20)
                {
                    case 0b100:
                        result = BRT_LR_MON;
                        break;
                    case 0b101:
                        result = BRT_SP_MON;
                        break;
                    case 0b110:
                        result = BRT_ELR_HYP;
                        break;
                    case 0b111:
                        result = BRT_SP_HYP;
                        break;
                }
                break;

        }

    }

    else if (r == 1)
    {
        switch (sysm_43)
        {
            case 0b10:
                switch (sysm_20)
                {
                    case 0b000:
                        result = BRT_SPSR_IRQ;
                        break;
                    case 0b010:
                        result = BRT_SPSR_SVC;
                        break;
                }
                break;

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : target = registre effectivement ciblé.                       *
*                                                                             *
*  Description : Crée une réprésentation de registre de banque ARMv7.         *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchRegister *_g_armv7_banked_register_new(BankedRegisterTarget target)
{
    GArmV7BankedRegister *result;           /* Structure à retourner       */

    if (target >= BRT_COUNT)
        goto bad_values;

    result = g_object_new(G_TYPE_ARMV7_BANKED_REGISTER, NULL);

    G_ARM_REGISTER(result)->index = target;

    return G_ARCH_REGISTER(result);

 bad_values:

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : r    = premier champ à interpréter.                          *
*                sysm = second champ à interpréter.                           *
*                                                                             *
*  Description : Crée une réprésentation de registre de banque ARMv7.         *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchRegister *g_armv7_banked_register_new(uint8_t r, uint8_t sysm)
{
    GArchRegister *result;                  /* Structure à retourner       */
    BankedRegisterTarget target;            /* Registre effectivement ciblé*/

    target = convert_r_sysm_to_target(r, sysm);

    if (target >= BRT_COUNT)
        goto bad_values;

    result = get_armv7_banked_register(target);

    return result;

 bad_values:

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = registre à consulter.                                  *
*                                                                             *
*  Description : Fournit le registre de banque ciblé.                         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

BankedRegisterTarget g_armv7_banked_register_get_target(const GArmV7BankedRegister *reg)
{
    BankedRegisterTarget result;            /* Cible à retourner           */

    result = G_ARM_REGISTER(reg)->index;

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          GESTION SOUS FORME DE SINGLETONS                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : target = registre effectivement ciblé.                       *
*                                                                             *
*  Description : Fournit le singleton associé à un registre de banque ARMv7.  *
*                                                                             *
*  Retour      : Adresse de la structure mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GArchRegister *get_armv7_banked_register(BankedRegisterTarget target)
{
    GArchRegister *result;                  /* Structure à retourner       */
    size_t new_count;                       /* Nouvelle taille à considérer*/
    size_t i;                               /* Boucle de parcours          */

    G_LOCK(_av7_banked_reg_mutex);

    if (target >= _av7_banked_reg_count)
    {
        /**
         * On valide déjà le fait que le registre puisse être créé
         * avant de réaliser une allocation potentiellement énorme
         * avec un indice démesuré.
         */

        result = _g_armv7_banked_register_new(target);

        if (result == NULL)
            goto bad_values;

        new_count = target + 1;

        _armv7_banked_registers = realloc(_armv7_banked_registers, new_count * sizeof(GArchRegister *));

        for (i = _av7_banked_reg_count; i < new_count; i++)
            _armv7_banked_registers[i] = NULL;

        _av7_banked_reg_count = new_count;

    }

    else
        result = NULL;

    if (_armv7_banked_registers[target] == NULL)
    {
        if (result != NULL)
            _armv7_banked_registers[target] = result;
        else
            _armv7_banked_registers[target] = _g_armv7_banked_register_new(target);
    }

    result = _armv7_banked_registers[target];

 bad_values:

    G_UNLOCK(_av7_banked_reg_mutex);

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Vide totalement le cache des registres de banque ARMv7.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void clean_armv7_banked_register_cache(void)
{
    size_t i;                               /* Boucle de parcours          */

    G_LOCK(_av7_banked_reg_mutex);

    for (i = 0; i < _av7_banked_reg_count; i++)
        g_clear_object(&_armv7_banked_registers[i]);

    if (_armv7_banked_registers != NULL)
        free(_armv7_banked_registers);

    _armv7_banked_registers = NULL;
    _av7_banked_reg_count = 0;

    G_UNLOCK(_av7_banked_reg_mutex);

}
