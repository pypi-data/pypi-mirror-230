
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rlestr.c - encodage par plage unique d'une chaîne de caractères
 *
 * Copyright (C) 2014-2019 Cyrille Bagard
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


#include "rlestr.h"


#include <malloc.h>
#include <sqlite3.h>
#include <string.h>


#include "../../../common/leb128.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : str  = représentation de chaîne à traiter.                   *
*                data = données à conserver en mémoire.                       *
*                                                                             *
*  Description : Définit une représentation de chaîne de caractères.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void init_dynamic_rle_string(rle_string *str, char *data)
{
    if (data != NULL)
    {
        str->data = data;
        str->length = strlen(data);
        str->dynamic = true;
    }
    else
    {
        str->data = NULL;
        str->length = 0;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str  = représentation de chaîne à traiter.                   *
*                data = données à conserver en mémoire.                       *
*                                                                             *
*  Description : Définit une représentation de chaîne de caractères constante.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void init_static_rle_string(rle_string *str, const char *data)
{
    if (data != NULL)
    {
        str->cst_data = data;
        str->length = strlen(data);
        str->dynamic = false;
    }
    else
    {
        str->data = NULL;
        str->length = 0;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str  = représentation de chaîne à traiter.                   *
*                data = données à conserver en mémoire.                       *
*                                                                             *
*  Description : Copie une chaîne de caractères existante.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void dup_into_rle_string(rle_string *str, const char *data)
{
    if (str->data != NULL)
        unset_rle_string(str);

    if (data != NULL)
    {
        str->data = strdup(data);
        str->length = strlen(data);
        str->dynamic = true;
    }
    else
    {
        str->data = NULL;
        str->length = 0;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str  = représentation de chaîne à traiter.                   *
*                data = données à conserver en mémoire.                       *
*                                                                             *
*  Description : Constitue une représentation de chaîne de caractères.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_dynamic_rle_string(rle_string *str, char *data)
{
    if (str->data != NULL)
        unset_rle_string(str);

    if (data != NULL)
    {
        str->data = data;
        str->length = strlen(data);
        str->dynamic = true;
    }
    else
    {
        str->data = NULL;
        str->length = 0;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str  = représentation de chaîne à traiter.                   *
*                data = données à conserver en mémoire.                       *
*                                                                             *
*  Description : Constitue une représentation de chaîne de caractères stable. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void set_static_rle_string(rle_string *str, const char *data)
{
    if (str->data != NULL)
        unset_rle_string(str);

    if (data != NULL)
    {
        str->cst_data = data;
        str->length = strlen(data);
        str->dynamic = false;
    }
    else
    {
        str->data = NULL;
        str->length = 0;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str = représentation de chaîne à traiter.                    *
*                                                                             *
*  Description : Libère la mémoire associée à la représentation.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unset_rle_string(rle_string *str)
{
    if (str->data != NULL)
    {
        if (str->dynamic)
            free(str->data);

        str->data = NULL;
        str->length = 0;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : s1 = première chaîne à comparer.                             *
*                s2 = seconde chaîne à comparer.                              *
*                                                                             *
*  Description : Effectue la comparaison entre deux chaînes de caractères.    *
*                                                                             *
*  Retour      : Résultat de la comparaison : -1, 0 ou 1.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_rle_string(const rle_string *s1, const rle_string *s2)
{
    int result;                             /* Bilan à retourner           */

    if (s1->length < s2->length)
        result = -1;

    else if (s1->length > s2->length)
        result = 1;

    else
    {
        if (s1->data == NULL && s2->data == NULL)
            result = 0;

        else if (s1->data != NULL && s2->data == NULL)
            result = 1;

        else if (s1->data == NULL && s2->data != NULL)
            result = -1;

        else
            result = strcmp(s1->data, s2->data);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str  = informations à constituer. [OUT]                      *
*                pbuf = paquet de données où venir puiser les infos.          *
*                                                                             *
*  Description : Importe la définition d'une chaîne de caractères.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool unpack_rle_string(rle_string *str, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    uleb128_t len;                          /* Quantité de caractères      */

    unset_rle_string(str);

    result = unpack_uleb128(&len, pbuf);

    if (result && len > 0)
    {
        str->length = len;

        str->data = malloc(str->length + 1);
        str->dynamic = true;

        result = extract_packed_buffer(pbuf, str->data, str->length + 1, false);

        if (!result)
            unset_rle_string(str);

        else
            str->data[str->length] = '\0';

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str  = informations à sauvegarder.                           *
*                pbuf = paquet de données où venir inscrire les infos.        *
*                                                                             *
*  Description : Exporte la définition d'une chaîne de caractères.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool pack_rle_string(const rle_string *str, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = pack_uleb128((uleb128_t []){ str->length }, pbuf);

    if (result && str->length > 0)
        result = extend_packed_buffer(pbuf, str->data, str->length + 1, false);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       MANIPULATIONS AVEC UNE BASE DE DONNEES                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : str    = chaîne de caractères à compléter.                   *
*                name   = désignation personnalisée du champ dans la BD.      *
*                values = tableau d'éléments à consulter.                     *
*                count  = nombre de descriptions renseignées.                 *
*                                                                             *
*  Description : Charge les valeurs utiles pour une chaîne de caractères.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_rle_string(rle_string *str, const char *name, const bound_value *values, size_t count)
{
    const bound_value *value;               /* Valeur à intégrer           */

    value = find_bound_value(values, count, name);
    if (value == NULL) return false;

    switch (value->type)
    {
        case SQLITE_TEXT:
            unset_rle_string(str);
            dup_into_rle_string(str, value->cstring);
            break;

        case SQLITE_NULL:
            unset_rle_string(str);
            break;

        default:
            return false;
            break;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str    = chaîne de caractères aux informations inutiles.     *
*                name   = désignation personnalisée du champ dans la BD.      *
*                values = couples de champs et de valeurs à lier. [OUT]       *
*                count  = nombre de ces couples. [OUT]                        *
*                                                                             *
*  Description : Constitue les champs destinés à une insertion / modification.*
*                                                                             *
*  Retour      : Bilan de l'opération : succès ou non.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool store_rle_string(const rle_string *str, const char *name, bound_value **values, size_t *count)
{
    bound_value *value;                     /* Valeur à éditer / définir   */

    *values = realloc(*values, ++(*count) * sizeof(bound_value));

    value = &(*values)[*count - 1];

    value->cname = name;
    value->built_name = false;

    value->has_value = (str != NULL);

    if (value->has_value)
        value->type = (get_rle_string(str) != NULL ? SQLITE_TEXT : SQLITE_NULL);
    else
        value->type = SQLITE_NATIVE;

    if (value->has_value)
    {
        value->cstring = get_rle_string(str);
        value->delete = SQLITE_STATIC;
    }

    return true;

}
