
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rlestr.c - encodage par plage unique d'une chaîne de caractères
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#include "timestamp.h"


#include <malloc.h>
#include <sqlite3.h>
#include <time.h>


#include "../../../core/logs.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : timestamp = horodatage à initialiser. [OUT]                  *
*                                                                             *
*  Description : Prépare un horodatage à une définition.                      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void setup_empty_timestamp(timestamp_t *timestamp)
{
    *timestamp = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : timestamp = horodatage à initialiser. [OUT]                  *
*                                                                             *
*  Description : Obtient un horodatage initialisé au moment même.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool init_timestamp(timestamp_t *timestamp)
{
    bool result;                            /* Bilan à retourner           */
    struct timespec info;                   /* Détails sur l'époque        */
    int ret;                                /* Bilan de la récupération    */

    ret = clock_gettime(CLOCK_REALTIME, &info);

    if (ret != 0)
    {
        LOG_ERROR_N("clock_gettime");
        result = false;
    }

    else
    {
        *timestamp = info.tv_sec * 1000000 + info.tv_nsec / 1000;
        result = true;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : timestamp = horodatage à initialiser. [OUT]                  *
*                value     = valeur d'initialisation.                         *
*                                                                             *
*  Description : Obtient un horodatage initialisé avec une valeur donnée.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool init_timestamp_from_value(timestamp_t *timestamp, uint64_t value)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    *timestamp = value;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stamp = horodatage d'un élément à tester.                    *
*                limit = horodatage en limite d'activité (incluse).           *
*                                                                             *
*  Description : Définit si un horodatage est plus récent qu'un autre ou non. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool timestamp_is_younger(timestamp_t stamp, timestamp_t limit)
{
    bool result;                            /* Bilan à retourner           */

    result = (stamp <= limit);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = destination de la copie d'horodatage. [OUT]           *
*                src  = source de l'horodatage à copier.                      *
*                                                                             *
*  Description : Effectue une copie d'horodatage.                             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void copy_timestamp(timestamp_t *dest, const timestamp_t *src)
{
    *dest = *src;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : t1 = premier horodatage à comparer.                          *
*                t2 = second horodatage à comparer.                           *
*                                                                             *
*  Description : Effectue la comparaison entre deux horodatages.              *
*                                                                             *
*  Retour      : Résultat de la comparaison : -1, 0 ou 1.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_timestamp(const timestamp_t *t1, const timestamp_t *t2)
{
    int result;                             /* Bilan à retourner           */

    if (*t1 < *t2)
        result = -1;

    else if (*t1 > *t2)
        result = 1;

    else
        result = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : timestamp = informations à constituer. [OUT]                 *
*                pbuf      = paquet de données où venir puiser les infos.     *
*                                                                             *
*  Description : Importe la définition d'un horodatage.                       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool unpack_timestamp(timestamp_t *timestamp, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = extract_packed_buffer(pbuf, (uint64_t *)timestamp, sizeof(uint64_t), true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : timestamp = informations à sauvegarder.                      *
*                pbuf      = paquet de données où venir inscrire les infos.   *
*                                                                             *
*  Description : Exporte la définition d'un horodatage.                       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool pack_timestamp(const timestamp_t *timestamp, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = extend_packed_buffer(pbuf, (uint64_t *)timestamp, sizeof(uint64_t), true);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       MANIPULATIONS AVEC UNE BASE DE DONNEES                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : timestamp = horodatage à compléter.                          *
*                name      = désignation personnalisée du champ dans la BD.   *
*                values    = tableau d'éléments à consulter.                  *
*                count     = nombre de descriptions renseignées.              *
*                                                                             *
*  Description : Charge les valeurs utiles pour un horodatage.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_timestamp(timestamp_t *timestamp, const char *name, const bound_value *values, size_t count)
{
    const bound_value *value;               /* Valeur à intégrer           */

    value = find_bound_value(values, count, name);
    if (value == NULL) return false;
    if (value->type != SQLITE_INT64) return false;

    *timestamp = value->integer64;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : timestamp = horodatage aux informations inutiles.            *
*                name      = désignation personnalisée du champ dans la BD.   *
*                values    = couples de champs et de valeurs à lier. [OUT]    *
*                count     = nombre de ces couples. [OUT]                     *
*                                                                             *
*  Description : Constitue les champs destinés à une insertion / modification.*
*                                                                             *
*  Retour      : Bilan de l'opération : succès ou non.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool store_timestamp(const timestamp_t *timestamp, const char *name, bound_value **values, size_t *count)
{
    bound_value *value;                     /* Valeur à éditer / définir   */

    *values = realloc(*values, ++(*count) * sizeof(bound_value));

    value = &(*values)[*count - 1];

    value->cname = name;
    value->built_name = false;
    value->type = SQLITE_INT64;

    value->has_value = (timestamp != NULL);

    if (value->has_value)
        value->integer64 = *timestamp;

    return true;

}
