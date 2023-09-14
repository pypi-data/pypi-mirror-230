
/* Chrysalide - Outil d'analyse de fichiers binaires
 * operand-int.c - définition générique interne des opérandes
 *
 * Copyright (C) 2021 Cyrille Bagard
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


#include "operand-int.h"



/* ---------------------------------------------------------------------------------- */
/*                      CONSERVATION ET RECHARGEMENT DES DONNEES                      */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à consulter.                           *
*                count   = quantité d'opérandes à extraire du tampon.         *
*                                                                             *
*  Description : Charge une série d'opérandes internes depuis un tampon.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _g_arch_operand_load_inner_instances(GArchOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf, size_t count)
{
    bool result;                            /* Bilan à retourner           */
    GArchOperand **instances;               /* Liste d'opérandes à charger */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    instances = calloc(count, sizeof(GArchOperand *));

    for (i = 0; i < count && result; i++)
        result = g_object_storage_unpack_object_2(storage, "operands", pbuf, G_TYPE_ARCH_OPERAND, &instances[i]);

    if (result)
        g_arch_operand_update_inner_instances(operand, instances, count);

    for (i = 0; i < count; i++)
        g_clear_object(&instances[i]);

    free(instances);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à consulter.                           *
*                                                                             *
*  Description : Charge une série d'opérandes internes depuis un tampon.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_operand_load_generic_fixed_1(GArchOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GType type;                             /* Type d'opérande manipulé    */
    GArchOperandClass *parent;              /* Classe parente à consulter  */

    type = G_TYPE_FROM_INSTANCE(operand);

    parent = g_type_class_peek_parent(g_type_class_peek(type));

    result = parent->load(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
        result = _g_arch_operand_load_inner_instances(operand, storage, pbuf, 1);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à consulter.                           *
*                                                                             *
*  Description : Charge une série d'opérandes internes depuis un tampon.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_operand_load_generic_fixed_3(GArchOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GType type;                             /* Type d'opérande manipulé    */
    GArchOperandClass *parent;              /* Classe parente à consulter  */

    type = G_TYPE_FROM_INSTANCE(operand);

    parent = g_type_class_peek_parent(g_type_class_peek(type));

    result = parent->load(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
        result = _g_arch_operand_load_inner_instances(operand, storage, pbuf, 3);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à consulter.                           *
*                                                                             *
*  Description : Charge une série d'opérandes internes depuis un tampon.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_operand_load_generic_variadic(GArchOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GType type;                             /* Type d'opérande manipulé    */
    GArchOperandClass *parent;              /* Classe parente à consulter  */
    uleb128_t value;                        /* Valeur ULEB128 à charger    */

    type = G_TYPE_FROM_INSTANCE(operand);

    parent = g_type_class_peek_parent(g_type_class_peek(type));

    result = parent->load(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
        result = unpack_uleb128(&value, pbuf);

    if (result)
        result = _g_arch_operand_load_inner_instances(operand, storage, pbuf, value);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                fixed   = précise si le nombre d'opérande est fixe ou non.   *
*                                                                             *
*  Description : Sauvegarde une série d'opérandes internes dans un tampon.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _g_arch_operand_store_inner_instances(GArchOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf, bool fixed)
{
    bool result;                            /* Bilan à retourner           */
    size_t count;                           /* Nombre d'opérandes listées  */
    GArchOperand **instances;               /* Liste d'opérandes à traiter */
    size_t i;                               /* Boucle de parcours          */
    GSerializableObject *obj;               /* Objet à conserver           */

    result = true;

    instances = g_arch_operand_list_inner_instances(operand, &count);

    if (!fixed)
        result = pack_uleb128((uleb128_t []){ count }, pbuf);

    if (instances != NULL)
    {
        for (i = 0; i < count && result; i++)
        {
            if (instances[i] == NULL)
                result = g_object_storage_pack_object(storage, "operands", NULL, pbuf);

            else
            {
                obj = G_SERIALIZABLE_OBJECT(instances[i]);

                result = g_object_storage_pack_object(storage, "operands", obj, pbuf);

                g_object_unref(G_OBJECT(instances[i]));

            }

        }

        for (; i < count && result; i++)
            g_clear_object(&instances[i]);

        free(instances);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                fixed   = précise si le nombre d'opérande est fixe ou non.   *
*                                                                             *
*  Description : Sauvegarde un opérande dans un tampon de façon générique.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_operand_store_generic_fixed(GArchOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GType type;                             /* Type d'opérande manipulé    */
    GArchOperandClass *parent;              /* Classe parente à consulter  */

    type = G_TYPE_FROM_INSTANCE(operand);

    parent = g_type_class_peek_parent(g_type_class_peek(type));

    result = parent->store(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
        result = _g_arch_operand_store_inner_instances(operand, storage, pbuf, true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : operand = élément GLib à consulter.                          *
*                storage = conservateur de données à manipuler ou NULL.       *
*                pbuf    = zone tampon à remplir.                             *
*                fixed   = précise si le nombre d'opérande est fixe ou non.   *
*                                                                             *
*  Description : Sauvegarde un opérande dans un tampon de façon générique.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_arch_operand_store_generic_variadic(GArchOperand *operand, GObjectStorage *storage, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    GType type;                             /* Type d'opérande manipulé    */
    GArchOperandClass *parent;              /* Classe parente à consulter  */

    type = G_TYPE_FROM_INSTANCE(operand);

    parent = g_type_class_peek_parent(g_type_class_peek(type));

    result = parent->store(G_ARCH_OPERAND(operand), storage, pbuf);

    if (result)
        result = _g_arch_operand_store_inner_instances(operand, storage, pbuf, false);

    return result;

}
