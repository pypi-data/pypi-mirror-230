
/* Chrysalide - Outil d'analyse de fichiers binaires
 * operand.c - gestion des operandes de l'architecture JVM
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


#include "operand.h"


#include "../operand-int.h"
#include "../../common/endianness.h"
#include "../../format/java/pool.h"


#include "../../format/exe_format.h" /* FIXME : remme */


/* ---------------------- COQUILLE VIDE POUR LES OPERANDES JVM ---------------------- */


/* Définition d'un opérande de la JVM (instance) */
struct _GJvmOperand
{
    GArchOperand parent;                    /* Instance parente            */

};


/* Définition d'un opérande de la JVM (classe) */
struct _GJvmOperandClass
{
    GArchOperandClass parent;               /* Classe parente              */

};


/* Initialise la classe des opérandes JVM de base. */
static void g_jvm_operand_class_init(GJvmOperandClass *);

/* Initialise une instance d'opérande de base pour la JVM. */
static void g_jvm_operand_init(GJvmOperand *);



/* --------------------- OPERANDES RENVOYANT VERS UNE REFERENCE --------------------- */


/* Définition d'un opérande de référence de la JVM (instance) */
struct _GJvmRefOperand
{
    GJvmOperand parent;                     /* Instance parente            */

    JvmOperandType type;                    /* Type de référence attendue  */
    uint16_t index;                         /* Indice dans la table Java   */

};


/* Définition d'un opérande de référence de la JVM (classe) */
struct _GJvmRefOperandClass
{
    GJvmOperandClass parent;                /* Classe parente              */

};


/* Initialise la classe des opérandes de référence JVM. */
static void g_jvm_ref_operand_class_init(GJvmRefOperandClass *);

/* Initialise une instance d'opérande de référence pour la JVM. */
static void g_jvm_ref_operand_init(GJvmRefOperand *);







/* ---------------------------------------------------------------------------------- */
/*                        COQUILLE VIDE POUR LES OPERANDES JVM                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour un opérande de JVM. */
G_DEFINE_TYPE(GJvmOperand, g_jvm_operand, G_TYPE_ARCH_OPERAND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des opérandes JVM de base.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_jvm_operand_class_init(GJvmOperandClass *klass)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance d'opérande de base pour la JVM.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_jvm_operand_init(GJvmOperand *operand)
{

}








/* ---------------------------------------------------------------------------------- */
/*                       OPERANDES RENVOYANT VERS UNE REFERENCE                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour un opérande de référence de JVM. */
G_DEFINE_TYPE(GJvmRefOperand, g_jvm_ref_operand, G_TYPE_JVM_OPERAND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des opérandes de référence JVM.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_jvm_ref_operand_class_init(GJvmRefOperandClass *klass)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : proc = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance d'opérande de référence pour la JVM. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_jvm_ref_operand_init(GJvmRefOperand *operand)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : data = flux de données à analyser.                           *
*                pos  = position courante dans ce flux. [OUT]                 *
*                len  = taille totale des données à analyser.                 *
*                type = type de l'opérande.                                   *
*                                                                             *
*  Description : Crée un opérande de référence pour la JVM.                   *
*                                                                             *
*  Retour      : Opérande mis en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GArchOperand *g_jvm_ref_operand_new(const bin_t *data, off_t *pos, off_t len, JvmOperandType type)
{
    GJvmRefOperand *result;                 /* Structure à retourner       */
    uint16_t index;                         /* Indice dans la table Java   */

    if (!read_u16(&index, data, pos, len, SRE_BIG))
        result = NULL;

    else
    {
        result = g_object_new(G_TYPE_JVM_REF_OPERAND, NULL);

        /* FIXME : faire attention au type */

        result->type = type;
        result->index = index;

    }

    return G_ARCH_OPERAND(result);

}


#if 0
/******************************************************************************
*                                                                             *
*  Paramètres  : operand = opérande à traiter.                                *
*                format  = format du binaire manipulé.                        *
*                                                                             *
*  Description : Traduit un opérande en version humainement lisible.          *
*                                                                             *
*  Retour      : Chaîne de caractères à libérer de la mémoire.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *g_jvm_ref_operand_get_text(const GJvmRefOperand *operand, const exe_format *format)
{
    char *result;                           /* Chaîne à retourner          */

    switch (operand->type)
    {
        case JOT_FIELD_REF:
            result = NULL;//build_reference_from_java_pool((const java_format *)format, operand->index, JRT_FIELD);
            break;
        case JOT_METHOD_REF:
            result = NULL;//build_reference_from_java_pool((const java_format *)format, operand->index, JRT_METHOD);
            break;
        default:
            result = NULL;
            break;
    }

    if (result == NULL)
        result = strdup("&lt;bad_reference&gt;");

    return result;

}
#endif







/* ---------------------------------------------------------------------------------- */
/*                           AIDE A LA CREATION D'OPERANDES                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : instr = instruction dont la définition est à compléter. [OUT]*
*                data  = flux de données à analyser.                          *
*                pos   = position courante dans ce flux. [OUT]                *
*                len   = taille totale des données à analyser.                *
*                type  = type de l'opérande.                                  *
*                ...   = éventuelle(s) information(s) complémentaire(s).      *
*                                                                             *
*  Description : Procède à la lecture d'un opérande donné.                    *
*                                                                             *
*  Retour      : Bilan de l'opération : true en cas de succès, false sinon.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool jvm_read_one_operand(GArchInstruction *instr, const bin_t *data, off_t *pos, off_t len, JvmOperandType type, ...)
{
    va_list ap;                             /* Liste des compléments       */
    GArchOperand *op;                       /* Opérande unique décodé      */

    va_start(ap, type);

    switch (type)
    {
        case JOT_FIELD_REF:
        case JOT_METHOD_REF:
            op = g_jvm_ref_operand_new(data, pos, len, type);
            break;

        default:
            op = NULL;
            break;
    }

    va_end(ap);

    if (op == NULL) return false;

    g_arch_instruction_attach_extra_operand(instr, op);

    return true;

}
