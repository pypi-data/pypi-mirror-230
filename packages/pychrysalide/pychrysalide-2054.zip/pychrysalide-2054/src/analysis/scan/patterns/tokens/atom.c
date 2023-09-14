
/* Chrysalide - Outil d'analyse de fichiers binaires
 * atom.c - détermination d'atomes à partir de motifs
 *
 * Copyright (C) 2023 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "atom.h"


#include <assert.h>
#include <malloc.h>



/**
 * Remplacement des fonctions de <ctypes.h> dans support des locales.
 */

#define IS_CH_LETTER(ch) (('A' <= ch && ch <= 'Z') || ('a' <= ch && ch <= 'z'))

#define MAKE_CH_UPPER(ch) (ch & 0xdf)
#define MAKE_CH_LOWER(ch) (ch | 0x20)



/******************************************************************************
*                                                                             *
*  Paramètres  : ch      = octet dont la valeur est à analyser.               *
*                seen    = suivi des octets déjà rencontrés. [OUT]            * 
*                letters = nombre de lettres rencontrées. [OUT]               *
*                                                                             *
*  Description : Note l'intêret de rechercher un octet particulier.           *
*                                                                             *
*  Retour      : Note positive ou négative.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int rate_byte_quality(bin_t ch, bitfield_t *seen, size_t *letters)
{
    int result;                             /* Note à retourner            */

    switch (ch)
    {
        case 0x00:
        case 0x20:
        case 0x90:
        case 0xcc:
        case 0xff:
            result = 12;
            break;

        case 'A' ... 'Z':
        case 'z' ... 'z':
            if (letters == NULL)
                result = 20;
            else
            {
                result = 18;
                (*letters)++;
            }
            break;

        default:
            result = 20;
            break;

    }

    set_in_bit_field(seen, ch, 1);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : seen = suivi des octets déjà rencontrés.                     * 
*                max  = nombre d'octets considérés à la base.                 *
*                                                                             *
*  Description : Termine la notation d'un ensemble d'octets.                  *
*                                                                             *
*  Retour      : Note positive ou négative.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int finish_quality_rating(const bitfield_t *seen, size_t max)
{
    int result;                             /* Note à retourner            */
    size_t uniq;                            /* Quantié d'octets uniques    */
    bool bad;                               /* Indice de mauvaise qualité  */

    uniq = popcount_for_bit_field(seen);

    if (uniq == 1)
    {
        bad = test_in_bit_field(seen, 0x00)
            || test_in_bit_field(seen, 0x20)
            || test_in_bit_field(seen, 0x90)
            || test_in_bit_field(seen, 0xcc)
            || test_in_bit_field(seen, 0xff);

        result = (bad ? -10 * max : 2);

    }

    else
        result = uniq * 2;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw     = définition de la bribe à enregistrer.              *
*                maxsize = taille max. des atomes (mise en commun optimisée). *
*                atom    = informations de suivi constituées. [OUT]           *
*                letters = nombre de lettres rencontrées. [OUT]               *
*                                                                             *
*  Description : Détermine la portion idéale de recherche.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void find_best_atom(const sized_binary_t *raw, size_t maxsize, tracked_scan_atom_t *atom, size_t *letters)
{
    size_t i;                               /* Boucle de parcours #1       */
    bin_t ch;                               /* Octets à étudier            */
    size_t best_letters;                    /* Mémorisation de décompte    */
    size_t *ptr_letters;                    /* Pointeur vers le décompte   */
    int best_rating;                        /* Meilleur notation obtenue   */
    bitfield_t *seen;                       /* Mémorise les octets déjà vus*/
    size_t max_loop;                        /* Limitation des itérations   */
    size_t k;                               /* Boucle de parcours #2       */
    size_t local_letters;                   /* Décompte courant des lettres*/
    int local_rating;                       /* Notation courante           */

    /* Si la chaîne fournie est plus petite que la taille d'un atome... */
    if (raw->len <= maxsize)
    {
        atom->pos = 0;
        atom->len = raw->len;
        atom->rem = 0;

        if (letters != NULL)
        {
            *letters = 0;

            for (i = 0; i < raw->len; i++)
            {
                ch = raw->data[i];

                if (IS_CH_LETTER(ch))
                    (*letters)++;

            }

        }

    }

    /* ... ou si une sélection doit s'opérer */
    else
    {
        /* Etablissement d'une mesure de référence à la position 0 */

        atom->pos = 0;
        atom->len = maxsize;

        ptr_letters = (letters != NULL ? &best_letters : NULL);

        best_letters = 0;
        best_rating = 0;

        seen = create_bit_field(256, false);

        for (k = 0; k < maxsize; k++)
            best_rating += rate_byte_quality(raw->data[k], seen, ptr_letters);

        best_rating += finish_quality_rating(seen, maxsize);

        /* Parcours du reste du contenu */

        max_loop = (raw->len - maxsize);

        ptr_letters = (letters != NULL ? &local_letters : NULL);

        for (i = 1; i < max_loop; i++)
        {
            local_letters = 0;
            local_rating = 0;

            reset_all_in_bit_field(seen);

            for (k = 0; k < maxsize; k++)
                local_rating += rate_byte_quality(raw->data[i + k], seen, ptr_letters);

            local_rating += finish_quality_rating(seen, maxsize);

            if (local_rating > best_rating)
            {
                atom->pos = i;

                best_letters = local_letters;
                best_rating = local_rating;

            }

        }

        /* Conclusion */

        delete_bit_field(seen);

        atom->rem = raw->len - atom->pos - maxsize;

        if (letters != NULL)
            *letters = best_letters;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : src   = chaîne ed référence à dupliquer.                     *
*                atom  = préselection opérée en amont.                        *
*                count = nombre de lettres présentes.                         *
*                                                                             *
*  Description : Etablit la liste des cas de figures ignorant la casse.       *
*                                                                             *
*  Retour      : Liste de toutes les combinaisons possibles.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

sized_binary_t *make_atoms_case_insensitive(const sized_binary_t *src, const tracked_scan_atom_t *atom, size_t count)
{
    sized_binary_t *result;                 /* Liste à retourner           */
    size_t i;                               /* Boucle de parcours #1       */
    size_t replaced;                        /* 2^(alternatives créées)     */
#ifndef NDEBUG
    size_t check;                           /* Validation du compte max.   */
#endif
    bin_t ch;                               /* Octet à recopier            */
    size_t k;                               /* Boucle de parcours #2       */
    size_t divisor;                         /* Taille de la découpe        */
    size_t quotient;                        /* Reste de la position        */

    /* Création du réceptacle */

    result = malloc(count * sizeof(tracked_scan_atom_t));

    assert(src->len == (atom->pos + atom->len + atom->rem));

    for (i = 0; i < count; i++)
    {
        result[i].data = malloc(src->len);
        result[i].len = src->len;

        memcpy(result[i].data, src->data, atom->pos);
        memcpy(&result[i].data[atom->pos + atom->len], &src->data[atom->pos + atom->len], atom->rem);

    }

    /* Remplissage */

    replaced = 2;

#ifndef NDEBUG
    check = 1;
#endif

    for (i = atom->pos; i < (atom->pos + atom->len); i++)
    {
        ch = src->data[i];

        if (IS_CH_LETTER(ch))
        {
            for (k = 0; k < count; k++)
            {
                divisor = count / replaced;
                quotient = k / divisor;

                if ((quotient % 2) == 0)
                    result[k].data[i] = MAKE_CH_UPPER(ch);
                else
                    result[k].data[i] = MAKE_CH_LOWER(ch);

            }

            replaced *= 2;

#ifndef NDEBUG
            check *= 2;
            assert(check <= count);
#endif

        }
        else
            for (k = 0; k < count; k++)
                result[k].data[i] = ch;

    }

    assert(check == count);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : byte     = octet partiel à interpréter.                      *
*                mask     = valeur du masque à appliquer.                     *
*                produced = nombre de contenus générés. [OUT]                 *
*                                                                             *
*  Description : Etablit la liste des cas de figures avec un octet partiel.   *
*                                                                             *
*  Retour      : Liste de toutes les combinaisons possibles.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

sized_binary_t *make_atoms_from_masked_byte(bin_t value, bin_t mask, size_t *produced)
{
    sized_binary_t *result;                 /* Liste à retourner           */
    size_t i;                               /* Boucle de parcours #1       */

    *produced = 16;

    /* Création du réceptacle */

    result = malloc(16 * sizeof(tracked_scan_atom_t));

    /* Remplissage */

    for (i = 0; i < 16; i++)
    {
        result[i].data = malloc(1);
        result[i].len = 1;

        if (mask == 0x0f)
            result[i].data[0] = value | (i << 4);
        else
            result[i].data[0] = value | i;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : raw     = définition de la bribe à enregistrer.              *
*                context = contexte de l'analyse à mener.                     *
*                backend = moteur de recherche à préchauffer.                 *
*                atom    = informations de suivi constituées. [OUT]           *
*                                                                             *
*  Description : Enregistre l'atome déterminé d'une série d'octets.           *
*                                                                             *
*  Retour      : Bilan de l'opération à renvoyer.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool enroll_prepared_atom(const sized_binary_t *raw, GScanContext *context, GEngineBackend *backend, tracked_scan_atom_t *atom)
{
    bool result;                            /* Statut à retourner          */
    const bin_t *data;                      /* Données à rechercher        */

    data = raw->data + atom->pos;

    atom->pid = g_engine_backend_enroll_plain_pattern(backend, context, data, atom->len);

    result = (atom->pid != INVALID_PATTERN_ID);

    return result;

}
