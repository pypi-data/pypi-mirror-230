
/* Chrysalide - Outil d'analyse de fichiers binaires
 * manager.c - compréhension et manipulation des champs de bits
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#include "manager.h"


#include <assert.h>
#include <inttypes.h>
#include <malloc.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>


#include "../helpers.h"



/* --------------------------- GESTION DES CHAMPS DE BITS --------------------------- */


/* Elément d'un mot décodé */
struct _raw_bitfield
{
    char *name;                             /* Désignation humaine         */
    unsigned int start;                     /* Position de départ          */
    unsigned int length;                    /* Taille du champ             */

    bool used;                              /* Champ défini & utilisé      */

};




/* Représentation de l'ensemble des bits de codage */
struct _coding_bits
{
    raw_bitfield *fields;                   /* Champs de bits détectés     */
    size_t bf_count;                        /* Nombre de ces champs        */
    uint64_t bits;                          /* Bits invariables            */
    uint64_t mask;                          /* Emplacement de ces bits     */
    unsigned int curpos;                    /* Position pendant l'analyse  */

};














/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à consulter.                           *
*                                                                             *
*  Description : Indique le nombre de bits utilisés par le champ.             *
*                                                                             *
*  Retour      : Nombre de bits considérés.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unsigned int get_raw_bitfield_length(const raw_bitfield *field)
{
    return field->length;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à traiter.                             *
*                                                                             *
*  Description : Marque un champ de bits comme étant utile.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void mark_raw_bitfield_as_used(raw_bitfield *field)
{
    field->used = true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : field = champ de bits à traiter.                             *
*                fd    = descripteur d'un flux ouvert en écriture.            *
*                                                                             *
*  Description : Imprime la désignation d'un champ de bits dans du code.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void write_raw_bitfield(const raw_bitfield *field, int fd)
{
    dprintf(fd, "raw_%s", field->name);

}










/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un nouveau gestionnaire des bits d'encodage brut.       *
*                                                                             *
*  Retour      : Nouvelle structure prête à emploi.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

coding_bits *create_coding_bits(void)
{
    coding_bits *result;                    /* Définition vierge à renvoyer*/

    result = (coding_bits *)calloc(1, sizeof(coding_bits));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bits = gestionnaire d'un ensemble de bits à libérer.         *
*                                                                             *
*  Description : Supprime de la mémoire un gestionnaire de bits d'encodage.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_coding_bits(coding_bits *bits)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < bits->bf_count; i++)
        free(bits->fields[i].name);

    if (bits->fields != NULL)
        free(bits->fields);

    free(bits);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bits   = gestionnaire de bits d'encodage brut à consulter.   *
*                name   = désignation humaine du champ remarqué.              *
*                length = taille du champ à mémoriser.                        *
*                                                                             *
*  Description : Note la présence d'un champ remarquable dans une définition. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_named_field_in_bits(coding_bits *bits, char *name, unsigned int length)
{
    raw_bitfield *field;                    /* Nouveau champ à constituer  */

    assert((bits->curpos + length) < 64);

    bits->fields = (raw_bitfield *)realloc(bits->fields,
                                              ++bits->bf_count * sizeof(raw_bitfield));

    field = &bits->fields[bits->bf_count - 1];

    field->name = make_string_lower(name);
    field->start = bits->curpos;
    field->length = length;

    bits->curpos += length;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bits = gestionnaire de bits d'encodage brut à consulter.     *
*                val  = valeur du bit à prendre en compte.                    *
*                                                                             *
*  Description : Note la présence d'un bit invariable dans une définition.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void register_bit_in_bits(coding_bits *bits, int val)
{
    assert(bits->curpos < 64);

    bits->bits |= (val ? 1 : 0) << bits->curpos;
    bits->mask |= 1 << bits->curpos;

    bits->curpos++;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bits = gestionnaire de bits d'encodage brut à consulter.     *
*                                                                             *
*  Description : Indique le nombre de bits traités.                           *
*                                                                             *
*  Retour      : Quantité, positive ou nulle.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

unsigned int count_coded_bits(const coding_bits *bits)
{
    return bits->curpos;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bits = gestionnaire d'encodage brut à consulter.             *
*                name = désignation humaine du champ à retrouver.             *
*                                                                             *
*  Description : Recherche un champ donné dans un ensemble de champs de bits. *
*                                                                             *
*  Retour      : Structure associée au champ trouvé ou NULL en cas d'échec.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

raw_bitfield *find_named_field_in_bits(const coding_bits *bits, const char *name)
{
    raw_bitfield *result;                   /* Champ de bits à retourner   */
    size_t i;                               /* Boucle de parcours          */

    result = NULL;

    for (i = 0; i < bits->bf_count && result == NULL; i++)
        if (strcmp(bits->fields[i].name, name) == 0)
            result = &bits->fields[i];

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec = spécification servant de base à l'opération.          *
*                fd   = descripteur d'un flux ouvert en écriture.             *
*                wide = taille des mots manipulés (en bits).                  *
*                                                                             *
*  Description : Déclare les variables C associées aux champs de bits.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool declare_used_bits_fields(const coding_bits *bits, int fd)
{
    unsigned int wide;                      /* Taille des mots             */
    size_t i;                               /* Boucle de parcours          */
    off_t start;                            /* Point de départ dans le code*/
    off_t end;                              /* Point d'arrivée dans le code*/

    wide = count_coded_bits(bits);

    for (i = 0; i < bits->bf_count; i++)
        if (bits->fields[i].used)
        {
            start = lseek(fd, 0, SEEK_CUR);

            dprintf(fd, "\tuint%u_t ", wide);
            write_raw_bitfield(&bits->fields[i], fd);
            dprintf(fd, ";");

            end = lseek(fd, 0, SEEK_CUR);

            dprintf(fd, "%*s", 42 - (int)(end - start), "/");
            dprintf(fd, "* Champ brut à décoder        */\n");

        }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec = spécification servant de base à l'opération.          *
*                fd   = descripteur d'un flux ouvert en écriture.             *
*                                                                             *
*  Description : Vérifie que les bits fixes correspondent au masque attendu.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool check_bits_correctness(const coding_bits *bits, int fd)
{
    switch (bits->curpos)
    {
        case 8:
            dprintf(fd, "\tif ((raw & 0x%" PRIx8 ") != 0x%" PRIx8 ") return NULL;\n",
                    (uint8_t)bits->mask, (uint8_t)bits->bits);
            break;

        case 16:
            dprintf(fd, "\tif ((raw & 0x%" PRIx16 ") != 0x%" PRIx16 ") return NULL;\n",
                    (uint16_t)bits->mask, (uint16_t)bits->bits);
            break;

        case 32:
            dprintf(fd, "\tif ((raw & 0x%" PRIx32 ") != 0x%" PRIx32 ") return NULL;\n",
                    (uint32_t)bits->mask, (uint32_t)bits->bits);
            break;

        case 64:
            dprintf(fd, "\tif ((raw & 0x%" PRIx64 ") != 0x%" PRIx64 ") return NULL;\n",
                    bits->mask, bits->bits);
            break;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : spec = spécification servant de base à l'opération.          *
*                fd   = descripteur d'un flux ouvert en écriture.             *
*                                                                             *
*  Description : Définit les variables C associées aux champs de bits.        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool define_used_bits_fields(const coding_bits *bits, int fd)
{
    bool got_one;                           /* Suit le nombre d'impressions*/
    size_t i;                               /* Boucle de parcours          */
    raw_bitfield *rf;                       /* Accès confortable à un champ*/

    got_one = false;

    for (i = 0; i < bits->bf_count; i++)
    {
        rf = &bits->fields[i];
        if (!rf->used) continue;

        dprintf(fd, "\t");
        write_raw_bitfield(rf, fd);
        dprintf(fd, " = (raw >> %u) & 0x%llx;\n", rf->start, (1ull << rf->length) - 1);

        got_one = true;

    }

    if (got_one)
        dprintf(fd, "\n");

    return true;

}
