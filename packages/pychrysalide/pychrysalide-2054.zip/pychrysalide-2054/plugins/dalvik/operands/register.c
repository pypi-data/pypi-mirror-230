
/* Chrysalide - Outil d'analyse de fichiers binaires
 * register.c - opérandes visant un registre Dalvik
 *
 * Copyright (C) 2017-2018 Cyrille Bagard
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


#include "register.h"


#include <arch/operands/register-int.h>



/* Définition d'un opérande visant un registre Dalvik (instance) */
struct _GDalvikRegisterOperand
{
    GRegisterOperand parent;                /* Instance parente            */

};


/* Définition d'un opérande visant un registre Dalvik (classe) */
struct _GDalvikRegisterOperandClass
{
    GRegisterOperandClass parent;           /* Classe parente              */

};


/* Initialise la classe des opérandes de registre Dalvik. */
static void g_dalvik_register_operand_class_init(GDalvikRegisterOperandClass *);

/* Initialise une instance d'opérande de registre Dalvik. */
static void g_dalvik_register_operand_init(GDalvikRegisterOperand *);

/* Supprime toutes les références externes. */
static void g_dalvik_register_operand_dispose(GDalvikRegisterOperand *);

/* Procède à la libération totale de la mémoire. */
static void g_dalvik_register_operand_finalize(GDalvikRegisterOperand *);



/* Indique le type défini par la GLib pour un opérande de registre Dalvik. */
G_DEFINE_TYPE(GDalvikRegisterOperand, g_dalvik_register_operand, G_TYPE_REGISTER_OPERAND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des opérandes de registre Dalvik.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_register_operand_class_init(GDalvikRegisterOperandClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_dalvik_register_operand_dispose;
    object->finalize = (GObjectFinalizeFunc)g_dalvik_register_operand_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance d'opérande de registre Dalvik.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_dalvik_register_operand_init(GDalvikRegisterOperand *operand)
{

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

static void g_dalvik_register_operand_dispose(GDalvikRegisterOperand *operand)
{
    G_OBJECT_CLASS(g_dalvik_register_operand_parent_class)->dispose(G_OBJECT(operand));

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

static void g_dalvik_register_operand_finalize(GDalvikRegisterOperand *operand)
{
    G_OBJECT_CLASS(g_dalvik_register_operand_parent_class)->finalize(G_OBJECT(operand));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = flux de données à analyser.                        *
*                pos     = position courante dans ce flux. [OUT]              *
*                low     = position éventuelle des 4 bits visés. [OUT]        *
*                size    = taille de l'opérande, et donc du registre.         *
*                endian  = ordre des bits dans la source.                     *
*                                                                             *
*  Description : Crée un opérande visant un registre Dalvik.                  *
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_dalvik_register_operand_new(const GBinContent *content, vmpa2t *pos, bool *low, MemoryDataSize size, SourceEndian endian)
{
    GArchOperand *result;                   /* Structure à retourner       */
    uint8_t index8;                         /* Indice sur 8 bits           */
    uint16_t index16;                       /* Indice sur 16 bits          */
    bool test;                              /* Bilan de lecture            */
    GArchRegister *reg;                     /* Registre à représenter      */

    result = NULL;

    switch (size)
    {
        case MDS_4_BITS:
            test = g_binary_content_read_u4(content, pos, low, &index8);
            break;
        case MDS_8_BITS:
            test = g_binary_content_read_u8(content, pos, &index8);
            break;
        case MDS_16_BITS:
            test = g_binary_content_read_u16(content, pos, endian, &index16);
            break;
        default:
            test = false;
            break;
    }

    if (!test)
        goto gdron_exit;

    switch (size)
    {
        case MDS_4_BITS:
        case MDS_8_BITS:
            reg = g_dalvik_register_new(index8);
            break;
        case MDS_16_BITS:
            reg = g_dalvik_register_new(index16);
            break;
        default:
            reg = NULL;
            break;
    }

    if (reg != NULL)
    {
        result = g_dalvik_register_operand_new_from_existing(reg);

        if (result == NULL)
            g_object_unref(G_OBJECT(reg));

    }

    return result;

 gdron_exit:

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : reg = registre déjà en place.                                *
*                                                                             *
*  Description : Crée un opérande visant un registre Dalvik.                  *
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_dalvik_register_operand_new_from_existing(GArchRegister *reg)
{
    GDalvikRegisterOperand *result;         /* Structure à retourner       */

    result = g_object_new(G_TYPE_DALVIK_REGISTER_OPERAND, NULL);

    G_REGISTER_OPERAND(result)->reg = reg;

    return G_ARCH_OPERAND(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande représentant un registre.                 *
*                                                                             *
*  Description : Fournit le registre Dalvik associé à l'opérande.             *
*                                                                             *
*  Retour      : Représentation interne du registre.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const GDalvikRegister *g_dalvik_register_operand_get(const GDalvikRegisterOperand *operand)
{
    GDalvikRegister *result;                /* Instance à retourner        */

    result = G_DALVIK_REGISTER(G_REGISTER_OPERAND(operand)->reg);

    return result;

}
