
/* Chrysalide - Outil d'analyse de fichiers binaires
 * snapshot.c - encodage des informations utiles aux instantanés
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include "snapshot.h"


#include <string.h>
#include <openssl/rand.h>


#include "../../../core/logs.h"



/* ---------------------------------------------------------------------------------- */
/*                            IDENTIFIANTS DES INSTANTANES                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : id = identifiant d'instantané à initialiser. [OUT]           *
*                                                                             *
*  Description : Prépare un identifiant pour instantané à une définition.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void setup_empty_snapshot_id(snapshot_id_t *id)
{
    memset(id, 0, sizeof(snapshot_id_t));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id = identifiant d'instantané à initialiser. [OUT]           *
*                                                                             *
*  Description : Construit un identifiant pour instantané de base de données. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool init_snapshot_id(snapshot_id_t *id)
{
    bool result;                            /* Bilan à retourner           */
    int ret;                                /* Bilan d'une génération      */
    unsigned char rand[SNAP_ID_RAND_SZ];    /* Tirage aléatoire            */
    size_t i;                               /* Boucle de parcours          */

    static char *alphabet = "0123456789abcdef";

    ret = RAND_bytes(rand, SNAP_ID_RAND_SZ);

    if (ret != 1)
    {
        LOG_ERROR_OPENSSL;
        result = false;
    }

    else
    {
        for (i = 0; i < SNAP_ID_RAND_SZ; i++)
        {
            id->name[i * 2 + 0] = alphabet[rand[i] & 0xf];
            id->name[i * 2 + 1] = alphabet[(rand[i] >> 4) & 0xf];
        }

        id->name[i * 2] = '\0';

        result = true;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id   = identifiant d'instantané à initialiser. [OUT]         *
*                text = source de données pour la constitution.               *
*                                                                             *
*  Description : Construit un identifiant pour instantané de base de données. *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool init_snapshot_id_from_text(snapshot_id_t *id, const char *text)
{
    bool result;                            /* Bilan à retourner           */

    result = (strlen(text) == (SNAP_ID_HEX_SZ - 1));

    if (result)
        strcpy(id->name, text);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = destination de la copie d'indentifiant. [OUT]         *
*                src  = source de l'identifiant à copier.                     *
*                                                                             *
*  Description : Effectue une copie d'identifiant d'instantané.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void copy_snapshot_id(snapshot_id_t *dest, const snapshot_id_t *src)
{
    memcpy(dest->name, src->name, SNAP_ID_HEX_SZ);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id1 = premier identifiant à comparer.                        *
*                id2 = second identifiant à comparer.                         *
*                                                                             *
*  Description : Effectue la comparaison entre deux identifiants.             *
*                                                                             *
*  Retour      : Résultat de la comparaison : -1, 0 ou 1.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_snapshot_id(const snapshot_id_t *id1, const snapshot_id_t *id2)
{
    int result;                             /* Bilan à retourner           */

    result = memcmp(id1->name, id2->name, SNAP_ID_HEX_SZ);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id   = informations à constituer. [OUT]                      *
*                pbuf = paquet de données où venir puiser les infos.          *
*                                                                             *
*  Description : Importe la définition d'un identifiant d'instantané.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool unpack_snapshot_id(snapshot_id_t *id, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = extract_packed_buffer(pbuf, id->name, SNAP_ID_HEX_SZ, false);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : id   = informations à sauvegarder.                           *
*                pbuf = paquet de données où venir inscrire les infos.        *
*                                                                             *
*  Description : Exporte la définition d'un identifiant d'instantané.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool pack_snapshot_id(const snapshot_id_t *id, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = extend_packed_buffer(pbuf, id->name, SNAP_ID_HEX_SZ, false);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                             PROPRIETES DES INSTANTANES                             */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : info = description d'instantané à initialiser. [OUT]         *
*                                                                             *
*  Description : Prépare une description pour instantané à une définition.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void setup_empty_snapshot_info(snapshot_info_t *info)
{
    setup_empty_snapshot_id(&info->parent_id);

    setup_empty_snapshot_id(&info->id);

    setup_empty_timestamp(&info->created);

    info->name = NULL;
    info->desc = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = description d'instantané à initialiser. [OUT]         *
*                                                                             *
*  Description : Construit une description pour instantané de base de données.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool init_snapshot_info(snapshot_info_t *info)
{
    bool result;                            /* Bilan à retourner           */

    result = init_snapshot_id_from_text(&info->parent_id, NO_SNAPSHOT_ROOT);

    if (result)
        result = init_snapshot_id(&info->id);

    if (result)
        result = init_timestamp(&info->created);

    if (result)
    {
        info->name = NULL;
        info->desc = NULL;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info    = description d'instantané à initialiser. [OUT]      *
*                id      = source de données pour l'identifiant.              *
*                created = source de données pour la date de création.        *
*                name    = source de données éventuelle pour le nom.          *
*                desc    = source de données éventuelle pour la description.  *
*                                                                             *
*  Description : Construit une description pour instantané de base de données.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool init_snapshot_info_from_text(snapshot_info_t *info, const char *id, uint64_t created, const char *name, const char *desc)
{
    bool result;                            /* Bilan à retourner           */

    result = init_snapshot_id_from_text(&info->parent_id, NO_SNAPSHOT_ROOT);

    if (result)
        result = init_snapshot_id_from_text(&info->id, id);

    if (result)
        result = init_timestamp_from_value(&info->created, created);

    if (result)
    {
        if (name == NULL)
            info->name = NULL;
        else
            info->name = strdup(name);

        if (desc == NULL)
            info->desc = NULL;
        else
            info->desc = strdup(desc);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = description d'instantané à initialiser. [OUT]         *
*                                                                             *
*  Description : Libère la mémoire occupée par une description d'instantané.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void exit_snapshot_info(snapshot_info_t *info)
{
    if (info->name != NULL)
    {
        free(info->name);
        info->name = NULL;
    }

    if (info->desc != NULL)
    {
        free(info->desc);
        info->desc = NULL;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = destination de la copie de description. [OUT]         *
*                src  = source de la description à copier.                    *
*                                                                             *
*  Description : Effectue une copie de description d'instantané.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void copy_snapshot_info(snapshot_info_t *dest, const snapshot_info_t *src)
{
    exit_snapshot_info(dest);

    copy_snapshot_id(&dest->parent_id, &src->parent_id);

    copy_snapshot_id(&dest->id, &src->id);

    copy_timestamp(&dest->created, &src->created);

    if (src->name != NULL)
        dest->name = strdup(src->name);

    if (src->desc != NULL)
        dest->desc = strdup(src->desc);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = informations à constituer. [OUT]                      *
*                pbuf = paquet de données où venir puiser les infos.          *
*                                                                             *
*  Description : Importe la description d'un identifiant d'instantané.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool unpack_snapshot_info(snapshot_info_t *info, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    rle_string string;                      /* Chaîne à transmettre        */
    const char *text;                       /* Valeur textuelle obtenue    */

    result = unpack_snapshot_id(&info->parent_id, pbuf);

    if (result)
        result = unpack_snapshot_id(&info->id, pbuf);

    if (result)
        result = unpack_timestamp(&info->created, pbuf);

    if (result)
    {
        setup_empty_rle_string(&string);

        result = unpack_rle_string(&string, pbuf);

        if (result)
        {
            text = get_rle_string(&string);
            info->name = (text != NULL ? strdup(text) : NULL);
            exit_rle_string(&string);
        }

    }

    if (result)
    {
        setup_empty_rle_string(&string);

        result = unpack_rle_string(&string, pbuf);

        if (result)
        {
            text = get_rle_string(&string);
            info->desc = (text != NULL ? strdup(text) : NULL);
            exit_rle_string(&string);
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = informations à sauvegarder.                           *
*                pbuf = paquet de données où venir inscrire les infos.        *
*                                                                             *
*  Description : Exporte la description d'un identifiant d'instantané.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool pack_snapshot_info(const snapshot_info_t *info, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    rle_string string;                      /* Chaîne à transmettre        */

    result = pack_snapshot_id(&info->parent_id, pbuf);

    if (result)
        result = pack_snapshot_id(&info->id, pbuf);

    if (result)
        result = pack_timestamp(&info->created, pbuf);

    if (result)
    {
        init_static_rle_string(&string, info->name);

        result = pack_rle_string(&string, pbuf);

        exit_rle_string(&string);

    }

    if (result)
    {
        init_static_rle_string(&string, info->desc);

        result = pack_rle_string(&string, pbuf);

        exit_rle_string(&string);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = informations à mettre à jour.                         *
*                name = nouvelle désignation à considérer.                    *
*                                                                             *
*  Description : Change la désignation dans les informations d'un instantané. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_snapshot_info_name(snapshot_info_t *info, const char *name)
{
    if (info->name == NULL)
        free(info->name);

    if (name == NULL)
        info->name = NULL;
    else
        info->name = strdup(name);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = informations à mettre à jour.                         *
*                desc = nouvelle description à considérer.                    *
*                                                                             *
*  Description : Change la description dans les informations d'un instantané. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_snapshot_info_desc(snapshot_info_t *info, const char *desc)
{
    if (info->desc == NULL)
        free(info->desc);

    if (desc == NULL)
        info->desc = NULL;
    else
        info->desc = strdup(desc);

}
