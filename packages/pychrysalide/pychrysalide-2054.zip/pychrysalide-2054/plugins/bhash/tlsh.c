
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tlsh.c - calculs d'empreintes selon l'algorithme TLSH
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


#include "tlsh.h"


#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <sys/param.h>


#include <common/hex.h>
#include <common/pearson.h>


#define BUCKETS_COUNT 256

#define BUCKETS_USED 128

#define HASH_CODE_SIZE ((BUCKETS_USED * 2) / 8)

#define TLSH_STRING_LEN (2 + 2 + 2 + 2 + HASH_CODE_SIZE * 2)

#define TLSH_LENGTH_MULTIPLIER 12
#define TLSH_QRATIO_MULTIPLIER 12


/* Mémorisation des informations brutes */
typedef struct _tlsh_info_t
{
    phys_t data_length;                     /* Taille des données traitées */

    uint32_t buckets[BUCKETS_COUNT];        /* Bac pour compteurs          */
    uint8_t checksum;                       /* Empreinte globale           */

    uint32_t q1;                            /* Première valeur pivot (75%) */
    uint32_t q2;                            /* Deuxième valeur pivot (50%) */
    uint32_t q3;                            /* Troisième valeur pivot (25%)*/

    uint8_t q1_ratio : 4;                   /* Ratio de portion #1         */
    uint8_t q2_ratio : 4;                   /* Ratio de portion #2         */

    uint8_t captured_length;                /* Tranche associée à la taille*/

} tlsh_info_t;

/* Récupération des informations d'une empreinte */
typedef struct _recovered_tlsh_info_t
{
    uint8_t checksum;                       /* Empreinte globale           */

    uint8_t captured_length;                /* Tranche associée à la taille*/

    uint8_t q1_ratio : 4;                   /* Ratio de portion #1         */
    uint8_t q2_ratio : 4;                   /* Ratio de portion #2         */

    uint8_t code[HASH_CODE_SIZE];           /* Coeur de l'empreinte        */

} recovered_tlsh_info_t;


/* Détermine l'indice du compteur destiné à un triplet d'octets. */
static uint8_t define_tlsh_mapping(uint8_t, uint8_t, uint8_t, uint8_t);

/* Définit tous les compteurs associés aux triplets d'octets. */
static bool fill_tlsh_buckets(const GBinContent *, tlsh_info_t *);

/* Compare deux compteurs de triplets d'octets. */
static int compare_tlsh_buckets(const uint32_t *, const uint32_t *);

/* Détermine les points de pivot au sein des bacs de compteurs. */
static void find_tlsh_quartiles(tlsh_info_t *);

/* Construit une empreinte TLSH sur les bases calculées. */
static char *build_tlsh_hash(const tlsh_info_t *, bool);

/* Reconstruit les informations portées par une empreinte TLSH. */
static bool recover_tlsh_hash(const char *, recovered_tlsh_info_t *);

/* Calcule une différence entre deux valeurs selon deux axes. */
static int32_t diff_tlsh_values_two_way(uint32_t, uint32_t, uint32_t);

/* Calcule le degré de différence entre deux octets TLSH. */
static uint8_t diff_tlsh_bits(uint8_t, uint8_t);



/******************************************************************************
*                                                                             *
*  Paramètres  : salt = sel à intégrer à la préparation.                      *
*                b0   = premier octet à manipuler.                            *
*                b1   = deuxième octet à manipuler.                           *
*                b2   = troisième octet à manipuler.                          *
*                                                                             *
*  Description : Détermine l'indice du compteur destiné à un triplet d'octets.*
*                                                                             *
*  Retour      : Indice du bac de destination pour décompte.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static uint8_t define_tlsh_mapping(uint8_t salt, uint8_t b0, uint8_t b1, uint8_t b2)
{
    uint8_t result;                         /* Valeur à retourner          */
    const uint8_t *table;                   /* Permutations à utiliser     */

    table = (const uint8_t *)get_pearson_permutations();

    result = table[salt ^ b0];
    result = table[result ^ b1];
    result = table[result ^ b2];

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à consulter.                       *
*                info    = informations à constituer en partie. [OUT]         *
*                                                                             *
*  Description : Définit tous les compteurs associés aux triplets d'octets.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool fill_tlsh_buckets(const GBinContent *content, tlsh_info_t *info)
{
    bool result;                            /* Bilan à retourner           */
    phys_t len;                             /* Taille des données présentes*/
    vmpa2t start;                           /* Première position de donnée */
    const uint8_t *data;                    /* Données à parcourir         */
    phys_t i;                               /* Boucle de parcours          */
    uint8_t index;                          /* Indice de compteur visé     */

    result = false;

    len = g_binary_content_compute_size(content);

    if (len < 5)
        goto exit;

    g_binary_content_compute_start_pos(content, &start);
    data = g_binary_content_get_raw_access(content, &start, len);

    info->data_length = len;

    memset(info->buckets, 0, sizeof(uint32_t) * BUCKETS_COUNT);
    info->checksum = 0;

    for (i = 0; i <= (len - 5); i++)
    {
        info->checksum = define_tlsh_mapping(1, data[i + 4], data[i + 3], info->checksum);

        index = define_tlsh_mapping( 49, data[i + 4], data[i + 3], data[i + 2]);
        info->buckets[index]++;

        index = define_tlsh_mapping( 12, data[i + 4], data[i + 3], data[i + 1]);
        info->buckets[index]++;

        index = define_tlsh_mapping( 84, data[i + 4], data[i + 3], data[i + 0]);
        info->buckets[index]++;

        index = define_tlsh_mapping(178, data[i + 4], data[i + 2], data[i + 1]);
        info->buckets[index]++;

        index = define_tlsh_mapping(166, data[i + 4], data[i + 2], data[i + 0]);
        info->buckets[index]++;

        index = define_tlsh_mapping(230, data[i + 4], data[i + 1], data[i + 0]);
        info->buckets[index]++;

    }

    result = true;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier bacs de décompte à consulter.                    *
*                b = second bacs de décompte à consulter.                     *
*                                                                             *
*  Description : Compare deux compteurs de triplets d'octets.                 *
*                                                                             *
*  Retour      : Bilan de comparaison.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int compare_tlsh_buckets(const uint32_t *a, const uint32_t *b)
{
    int result;                             /* Bilan à retourner           */

    if (*a < *b)
        result = -1;

    else if (*a > *b)
        result = 1;

    else
        result = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = informations à constituer en partie. [OUT]            *
*                                                                             *
*  Description : Détermine les points de pivot au sein des bacs de compteurs. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void find_tlsh_quartiles(tlsh_info_t *info)
{
    uint32_t copy[BUCKETS_USED];           /* Copie modifiable            */

    memcpy(copy, info->buckets, BUCKETS_USED * sizeof(uint32_t));

    qsort(copy, BUCKETS_USED, sizeof(uint32_t), (__compar_fn_t)compare_tlsh_buckets);

    /**
     * q1 = quantité telle que 75% des buckets >= q1
     * q2 = quantité telle que 50% des buckets >= q2
     * q3 = quantité telle que 25% des buckets >= q3
     */

    info->q1 = copy[BUCKETS_USED / 4 - 1];

    info->q2 = copy[BUCKETS_USED / 2 - 1];

    info->q3 = copy[(3 * BUCKETS_USED) / 4 - 1];

}





#include <math.h>


#define LOG_1_5 0.4054651
#define LOG_1_3 0.26236426
#define LOG_1_1 0.095310180


unsigned char l_capturing(unsigned int len) {
    int i;
    if( len <= 656 ) {
        i = (int) floor( logf((float) len) / LOG_1_5 );
    } else if( len <= 3199 ) {
        i = (int) floor( logf((float) len) / LOG_1_3 - 8.72777 );
    } else {
        i = (int) floor( logf((float) len) / LOG_1_1 - 62.5472 );
    }

    return (unsigned char) (i & 0xFF);
}








/******************************************************************************
*                                                                             *
*  Paramètres  : info    = informations à consulter.                          *
*                version = affichage de la version ?                          *
*                                                                             *
*  Description : Construit une empreinte TLSH sur les bases calculées.        *
*                                                                             *
*  Retour      : Empreinte construite ou NULL en cas d'échec.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *build_tlsh_hash(const tlsh_info_t *info, bool version)
{
    char *result;                           /* Empreinte à retourner       */
    char *pos;                              /* Tête de lecture             */
    char tmp[HASH_CODE_SIZE * 2];           /* Stockage temporaire         */
    char *code;                             /* Empreinte des compteurs     */
    size_t i;                               /* Boucle de parcours          */
    size_t offset;                          /* Rang d'intervention         */

    static char hex_lookup[] = "0123456789ABCDEF";

    result = malloc(TLSH_STRING_LEN + 1);

    /* Indication de version ? */

    if (version)
    {
        result[0] = 'T';
        result[1] = '1';
        pos = result + 2;
    }
    else
        pos = result;

    /* Empreinte concise */

    *(pos++) = hex_lookup[info->checksum & 0xf];
    *(pos++) = hex_lookup[(info->checksum >> 4) & 0xf];

    /* Taille représentée */

    *(pos++) = hex_lookup[info->captured_length & 0xf];
    *(pos++) = hex_lookup[(info->captured_length >> 4) & 0xf];

    /* Ratios */

    *(pos++) = hex_lookup[info->q1_ratio];

    *(pos++) = hex_lookup[info->q2_ratio];

    /* Empreinte du contenu binaire */

    code = &tmp[HASH_CODE_SIZE - 1];

    for (i = 0; i < BUCKETS_USED; i++)
    {
        if ((i % 4) == 0)
            *code = 0;

        offset = (i % 4) * 2;

        if (info->buckets[i] <= info->q1)
            ;

        else if (info->buckets[i] <= info->q2)
            (*code) |= (1 << offset);

        else if (info->buckets[i] <= info->q3)
            (*code) |= (2 << offset);

        else
            (*code) |= (3 << offset);

        if (((i + 1) % 4) == 0)
            code--;

    }

    encode_hex(tmp, HASH_CODE_SIZE, false, pos);

    assert(pos + (HASH_CODE_SIZE * 2) < result + (TLSH_STRING_LEN + 1));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à consulter.                       *
*                version = affichage de la version ?                          *
*                                                                             *
*  Description : Calcule l'empreinte TLSH d'un contenu binaire.               *
*                                                                             *
*  Retour      : Empreinte TLSH calculée ou NULL en cas d'échec.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *compute_content_tlsh_hash(const GBinContent *content, bool version)
{
    char *result;                           /* Empreinte à retourner       */
    bool status;                            /* Bilan d'un appel            */
    tlsh_info_t info;                       /* Informations brutes         */

    result = NULL;

    status = fill_tlsh_buckets(content, &info);
    if (!status) goto exit;

    find_tlsh_quartiles(&info);

    if (info.q3 == 0)
        goto exit;

    info.q1_ratio = ((float)(info.q1 * 100) / (float)info.q3);
    info.q2_ratio = ((float)(info.q2 * 100) / (float)info.q3);

    info.captured_length = l_capturing(info.data_length);

    result = build_tlsh_hash(&info, version);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : h = chaîne de caratères à valider.                           *
*                                                                             *
*  Description : Indique si une chaîne représente à priori une empreinte TLSH.*
*                                                                             *
*  Retour      : Bilan de l'analyse.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool is_valid_tlsh_hash(const char *h)
{
    bool result;                            /* Bilan à renvoyer            */
    size_t len;                             /* Taille de la chaîne         */

    len = strlen(h);

    if (len == (TLSH_STRING_LEN - 2))
        result = true;

    else if (len == TLSH_STRING_LEN)
        result = (h[0] == 'T' && h[1] == '1');

    else
        result = false;

    // TODO check hex

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : h    = chaîne de caratères à consulter.                      *
*                info = informations portées par une empreinte TLSH.          *
*                                                                             *
*  Description : Reconstruit les informations portées par une empreinte TLSH. *
*                                                                             *
*  Retour      : Bilan de la reconstruction.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool recover_tlsh_hash(const char *h, recovered_tlsh_info_t *info)
{
    bool result;                            /* Bilan à renvoyer            */
    const char *pos;                        /* Tête de lecture             */
    uint8_t value;                          /* Valeur récupérée            */
    size_t i;                               /* Boucle de parcours          */

    result = is_valid_tlsh_hash(h);
    if (!result) goto exit;

    /* Indication de version ? */

    pos = (h[0] == 'T' ? h + 2 : h);

    /* Empreinte concise */

    result = decode_hex_digit(pos++, &value);
    assert(result);
    if (!result) goto exit;

    info->checksum = value;

    result = decode_hex_digit(pos++, &value);
    assert(result);
    if (!result) goto exit;

    info->checksum |= (value << 4);

    /* Taille représentée */

    result = decode_hex_digit(pos++, &value);
    assert(result);
    if (!result) goto exit;

    info->captured_length = value;

    result = decode_hex_digit(pos++, &value);
    assert(result);
    if (!result) goto exit;

    info->captured_length |= (value << 4);

    /* Ratios */

    result = decode_hex_digit(pos++, &value);
    assert(result);
    if (!result) goto exit;

    info->q1_ratio = value;

    result = decode_hex_digit(pos++, &value);
    assert(result);
    if (!result) goto exit;

    info->q2_ratio = value;

    /* Empreinte du contenu binaire */

    for (i = 0; i < HASH_CODE_SIZE; i++)
    {
        result = decode_hex_digit(pos++, &value);
        assert(result);
        if (!result) goto exit;

        info->code[HASH_CODE_SIZE - i - 1] = (value << 4);

        result = decode_hex_digit(pos++, &value);
        assert(result);
        if (!result) goto exit;

        info->code[HASH_CODE_SIZE - i - 1] |= value;

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a     = première valeur à analyser.                          *
*                b     = seconde valeur à analyser.                           *
*                range = espace de valeurs à considérer.                      *
*                                                                             *
*  Description : Calcule une différence entre deux valeurs selon deux axes.   *
*                                                                             *
*  Retour      : Différence déterminée entre les deux valeurs.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int32_t diff_tlsh_values_two_way(uint32_t a, uint32_t b, uint32_t range)
{
    int32_t result;                         /* Différence à retourner      */
    int32_t diff_1;                         /* Première différence         */
    int32_t diff_2;                         /* Seconde différence         */

    if (a < b)
    {
        diff_1 = b - a;
        diff_2 = range + a - b;
    }
    else
    {
        diff_1 = a - b;
        diff_2 = range + b - a;
    }

    result = MIN(diff_1, diff_2);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier octet à analyser.                                *
*                b = second octet à analyser.                                 *
*                                                                             *
*  Description : Calcule le degré de différence entre deux octets TLSH.       *
*                                                                             *
*  Retour      : Différence déterminée entre les deux octets.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static uint8_t diff_tlsh_bits(uint8_t a, uint8_t b)
{
    uint8_t result;                         /* Valeur à renvoyer           */
    uint8_t partial;                        /* Différence partielle        */

    result = 0;

    partial = abs(a % 4 - b % 4);
    result += (partial == 3 ? 6 : partial);

    a /= 4; b /= 4;

    partial = abs(a % 4 - b % 4);
    result += (partial == 3 ? 6 : partial);

    a /= 4; b /= 4;

    partial = abs(a % 4 - b % 4);
    result += (partial == 3 ? 6 : partial);

    a /= 4; b /= 4;

    partial = abs(a % 4 - b % 4);
    result += (partial == 3 ? 6 : partial);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : ha     = première chaîne de caratères à consulter.           *
*                hb     = première chaîne de caratères à consulter.           *
*                length = l'indication de taille doit être considérée ?       *
*                diff   = degré de différence relevé. [OUT]                   *
*                                                                             *
*  Description : Détermine la similarité entre deux empreintes TLSH.          *
*                                                                             *
*  Retour      : Validité de l'opération menée.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool compare_tlsh_hash(const char *ha, const char *hb, bool length, int32_t *diff)
{
    bool result;                            /* Validité à retourner        */
    recovered_tlsh_info_t info_a;           /* Empreinte à manipuler #0    */
    recovered_tlsh_info_t info_b;           /* Empreinte à manipuler #1    */
    int32_t partial;                        /* Différence calculée         */
    size_t i;                               /* Boucle de parcours          */

    result = recover_tlsh_hash(ha, &info_a);
    if (!result) goto exit;

    result = recover_tlsh_hash(hb, &info_b);
    if (!result) goto exit;

    *diff = 0;

    /* Empreinte concise */

    if (info_a.checksum != info_b.checksum)
        *diff += 1;

    /* Taille représentée */

    if (length)
    {
        partial = diff_tlsh_values_two_way(info_a.captured_length, info_b.captured_length, 2 << 8);

        if (partial > 1)
            partial *= TLSH_LENGTH_MULTIPLIER;

        *diff += partial;

    }

    /* Ratios */

    partial = diff_tlsh_values_two_way(info_a.q1_ratio, info_b.q1_ratio, 2 << 4);

    if (partial > 1)
        partial *= TLSH_QRATIO_MULTIPLIER;

    *diff += partial;

    partial = diff_tlsh_values_two_way(info_a.q2_ratio, info_b.q2_ratio, 2 << 4);

    if (partial > 1)
        partial *= TLSH_QRATIO_MULTIPLIER;

    *diff += partial;

    /* Empreinte du contenu binaire */

    for (i = 0; i < HASH_CODE_SIZE; i++)
        *diff += diff_tlsh_bits(info_a.code[i], info_b.code[i]);

 exit:

    return result;

}
