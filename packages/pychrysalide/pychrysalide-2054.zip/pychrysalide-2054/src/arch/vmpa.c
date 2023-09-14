
/* Chrysalide - Outil d'analyse de fichiers binaires
 * vmpa.c - adressages virtuels ou physiques
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


#include "vmpa.h"


#include <inttypes.h>
#include <malloc.h>
#include <sqlite3.h>
#include <stdlib.h>
#include <string.h>


#include <i18n.h>


#include "../common/extstr.h"



/* ---------------------- DEFINITION D'UNE POSITION EN MEMOIRE ---------------------- */


/* Transforme une position physique en chaîne de caractères. */
static char *_phys_t_to_string(phys_t, MemoryDataSize, char [VMPA_MAX_LEN], size_t *);



/* ------------------------ DEFINITION D'UNE ZONE EN MEMOIRE ------------------------ */


/* Compare une couverture mémoire avec une localisation simple. */
static int _cmp_mrange_with_vmpa(const mrange_t *, const vmpa2t *, bool);



/* ---------------------------------------------------------------------------------- */
/*                        DEFINITION D'UNE POSITION EN MEMOIRE                        */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : addr = élément à initialiser. [OUT]                          *
*                phy  = position dans la mémoire physique.                    *
*                virt = adresse dans la mémoire virtuelle.                    *
*                                                                             *
*  Description : Initialise une localisation dans l'espace mémoire/physique.  *
*                                                                             *
*  Retour      : Adressage alloué en mémoire.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void init_vmpa(vmpa2t *addr, phys_t phy, virt_t virt)
{
    addr->physical = phy;
    addr->virtual = virt;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : phy  = position dans la mémoire physique.                    *
*                virt = adresse dans la mémoire virtuelle.                    *
*                                                                             *
*  Description : Crée une localisation dans l'adressage mémoire.              *
*                                                                             *
*  Retour      : Adressage alloué en mémoire.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

vmpa2t *make_vmpa(phys_t phy, virt_t virt)
{
    vmpa2t *result;                         /* Structure à retourner       */

    result = (vmpa2t *)calloc(1, sizeof(vmpa2t));

    init_vmpa(result, phy, virt);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : src = position à dupliquer.                                  *
*                                                                             *
*  Description : Copie une localisation dans l'adressage mémoire.             *
*                                                                             *
*  Retour      : Adressage alloué en mémoire.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

vmpa2t *dup_vmpa(const vmpa2t *src)
{
    vmpa2t *result;                         /* Structure à retourner       */

    result = make_vmpa(get_phy_addr(src), get_virt_addr(src));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr = position à traiter.                                   *
*                                                                             *
*  Description : Supprime une localisation de l'espace mémoire.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_vmpa(vmpa2t *addr)
{
    free(addr);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = structure de destination pour la copie.               *
*                src  = structure de source pour la copie.                    *
*                                                                             *
*  Description : Copie la définition d'un adressage dans un autre.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void copy_vmpa(vmpa2t *dest, const vmpa2t *src)
{
    dest->physical = src->physical;
    dest->virtual = src->virtual;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr = position à consulter.                                 *
*                                                                             *
*  Description : Calcule une empreinte de localisation dans l'espace mémoire. *
*                                                                             *
*  Retour      : Condensat déterminé pour la localisation.                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

uint32_t hash_vmpa(const vmpa2t *addr)
{
    uint32_t result;                        /* Empreinte à retourner       */

    result = addr->physical;
    result ^= (addr->physical >> 32);

    result ^= addr->virtual;
    result ^= (addr->virtual >> 32);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = première définition à analyser.                          *
*                b = seconde définition à analyser.                           *
*                                                                             *
*  Description : Compare entre elles deux adresses physiques.                 *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_vmpa_by_phy(const vmpa2t *a, const vmpa2t *b)
{
    int result;                             /* Bilan à retourner           */

    if (a->physical != VMPA_NO_PHYSICAL && b->physical != VMPA_NO_PHYSICAL)
    {
        if (a->physical < b->physical) result = -1;
        else if (a->physical > b->physical) result = 1;
        else result = 0;
    }
    else
    {
        if (a->physical == VMPA_NO_PHYSICAL && b->physical == VMPA_NO_PHYSICAL) result = 0;
        else if (a->physical == VMPA_NO_PHYSICAL) result = 1;
        else result = -1;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = première définition à analyser.                          *
*                b = seconde définition à analyser.                           *
*                                                                             *
*  Description : Compare entre elles deux adresses virtuelles.                *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_vmpa_by_virt(const vmpa2t *a, const vmpa2t *b)
{
    int result;                             /* Bilan à retourner           */

    if (a->virtual != VMPA_NO_VIRTUAL && b->virtual != VMPA_NO_VIRTUAL)
    {
        if (a->virtual < b->virtual) result = -1;
        else if (a->virtual > b->virtual) result = 1;
        else result = 0;
    }
    else
    {
        if (a->virtual == VMPA_NO_VIRTUAL && b->virtual == VMPA_NO_VIRTUAL) result = 0;
        else if (a->virtual == VMPA_NO_VIRTUAL) result = 1;
        else result = -1;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = première définition à analyser.                          *
*                b = seconde définition à analyser.                           *
*                                                                             *
*  Description : Compare deux localisations selon leurs parties définies.     *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1 (-1 par défaut).        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_vmpa(const vmpa2t *a, const vmpa2t *b)
{
    int result;                             /* Bilan à retourner           */
    bool compared;                          /* Comparaison effectuée       */

    if (a->physical == VMPA_NO_PHYSICAL && a->virtual == VMPA_NO_VIRTUAL
        && b->physical == VMPA_NO_PHYSICAL && b->virtual == VMPA_NO_VIRTUAL)
    {
        result = 0;

    }

    else if (a->physical == VMPA_NO_PHYSICAL && a->virtual == VMPA_NO_VIRTUAL)
    {
        result = 1;

    }

    else if (b->physical == VMPA_NO_PHYSICAL && b->virtual == VMPA_NO_VIRTUAL)
    {
        result = -1;

    }

    else
    {
        compared = false;

        if (a->physical != VMPA_NO_PHYSICAL && b->physical != VMPA_NO_PHYSICAL)
        {
            result = cmp_vmpa_by_phy(a, b);
            compared = true;
        }

        if (a->virtual != VMPA_NO_VIRTUAL && b->virtual != VMPA_NO_VIRTUAL
            && (!compared || (compared && result == 0)))
        {
            result = cmp_vmpa_by_virt(a, b);
            compared = true;
        }

        /* Cas particulier : les deux éléments n'ont aucun champ défini en commun ! */
        if (!compared)
            result = cmp_vmpa_by_phy(a, b);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr = élément à modifier.                                   *
*                qty  = quantité d'unités de décalage.                        *
*                                                                             *
*  Description : Décalle une position d'une certaine quantité.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void advance_vmpa(vmpa2t *addr, phys_t qty)
{
    if (addr->physical != VMPA_NO_PHYSICAL)
        addr->physical += qty;

    if (addr->virtual != VMPA_NO_VIRTUAL)
        addr->virtual += qty;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr = élément à modifier.                                   *
*                qty  = quantité d'unités de décalage.                        *
*                                                                             *
*  Description : Décalle une position d'une certaine quantité.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void deminish_vmpa(vmpa2t *addr, phys_t qty)
{
    /* On choisit de ne pas vérifier les débordements */

    if (addr->physical != VMPA_NO_PHYSICAL)
        addr->physical -= qty;

    if (addr->virtual != VMPA_NO_VIRTUAL)
        addr->virtual -= qty;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr  = élément à modifier.                                  *
*                bytes = nombre d'octets sur lequel aligner la position.      *
*                                                                             *
*  Description : Aligne une localisation sur un nombre d'octets donné.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void align_vmpa(vmpa2t *addr, phys_t bytes)
{
    if (bytes > 1)
    {
        if (addr->physical != VMPA_NO_PHYSICAL)
            addr->physical = (addr->physical + bytes - 1) & ~(bytes - 1);

        if (addr->virtual != VMPA_NO_VIRTUAL)
            addr->virtual = (addr->virtual + bytes - 1) & ~(bytes - 1);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = première élément à venir consulter.                      *
*                b = second élément à traiter en parallèle.                   *
*                                                                             *
*  Description : Calcule au mieux la distance entre deux coordonnées.         *
*                                                                             *
*  Retour      : Distance absolue entre deux localisations.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

phys_t compute_vmpa_diff(const vmpa2t *a, const vmpa2t *b)
{
    phys_t result;                          /* Valeur à retourner          */

    result = VMPA_NO_PHYSICAL;

    if (a->physical != VMPA_NO_PHYSICAL && b->physical != VMPA_NO_PHYSICAL)
        result = (b->physical > a->physical ? b->physical - a->physical : a->physical - b->physical);

    else if (a->virtual != VMPA_NO_VIRTUAL && b->virtual != VMPA_NO_VIRTUAL)
        result = (phys_t)(b->virtual > a->virtual ? b->virtual - a->virtual : a->virtual - b->virtual);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr = élément à venir lire. [OUT]                           *
*                pbuf = paquet de données où venir puiser les infos.          *
*                                                                             *
*  Description : Lit la définition d'une adresse depuis un tampon.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool unpack_vmpa(vmpa2t *addr, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = extract_packed_buffer(pbuf, (uint64_t *)&addr->physical, sizeof(uint64_t), true);

    if (result)
        result = extract_packed_buffer(pbuf, (uint64_t *)&addr->virtual, sizeof(uint64_t), true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr = élément à venir écrire.                               *
*                pbuf = paquet de données où venir inscrire les infos.        *
*                                                                             *
*  Description : Ecrit la définition d'une adresse dans un tampon.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool pack_vmpa(const vmpa2t *addr, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = extend_packed_buffer(pbuf, (uint64_t *)&addr->physical, sizeof(uint64_t), true);

    if (result)
        result = extend_packed_buffer(pbuf, (uint64_t *)&addr->virtual, sizeof(uint64_t), true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : phys   = position physique à traiter.                        *
*                msize  = taille de cette adresse, réelle ou désirée.         *
*                buffer = tampon de sortie utilisé à constituer. [OUT]        *
*                length = transmission de la taille du résultat ou NULL. [OUT]*
*                                                                             *
*  Description : Transforme une position physique en chaîne de caractères.    *
*                                                                             *
*  Retour      : Chaîne de caractères constituée.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *_phys_t_to_string(phys_t phys, MemoryDataSize msize, char buffer[VMPA_MAX_LEN], size_t *length)
{
    size_t ret;                             /* Retour de l'impression      */

	if (phys == VMPA_NO_PHYSICAL)
		ret = snprintf(buffer, VMPA_MAX_LEN, _("(none)"));

	else
        switch (msize)
        {
            case MDS_8_BITS:
                ret = snprintf(buffer, VMPA_MAX_LEN, "0x%02" PRIx64, phys);
                break;

            case MDS_16_BITS:
                ret = snprintf(buffer, VMPA_MAX_LEN, "0x%04" PRIx64, phys);
                break;

            case MDS_32_BITS:
                ret = snprintf(buffer, VMPA_MAX_LEN, "0x%08" PRIx64, phys);
                break;

            case MDS_64_BITS:
                ret = snprintf(buffer, VMPA_MAX_LEN, "0x%016" PRIx64, phys);
                break;

            default:
                ret = snprintf(buffer, VMPA_MAX_LEN, "0x%" PRIx64, phys);
                break;

        }

    if (length != NULL)
        *length = ret;

    return buffer;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr   = adresse virtuelle ou physique à traiter.            *
*                msize  = taille de cette adresse, réelle ou désirée.         *
*                buffer = tampon de sortie utilisé à constituer. [OUT]        *
*                length = transmission de la taille du résultat ou NULL. [OUT]*
*                                                                             *
*  Description : Transforme une adresse physique en chaîne de caractères.     *
*                                                                             *
*  Retour      : Chaîne de caractères constituée.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *vmpa2_phys_to_string(const vmpa2t *addr, MemoryDataSize msize, char buffer[VMPA_MAX_LEN], size_t *length)
{
    return _phys_t_to_string(addr->physical, msize, buffer, length);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr   = adresse virtuelle ou physique à traiter.            *
*                msize  = taille de cette adresse, réelle ou désirée.         *
*                buffer = tampon de sortie utilisé à constituer. [OUT]        *
*                length = transmission de la taille du résultat ou NULL. [OUT]*
*                                                                             *
*  Description : Transforme une adresse virtuelle en chaîne de caractères.    *
*                                                                             *
*  Retour      : Chaîne de caractères constituée.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *vmpa2_virt_to_string(const vmpa2t *addr, MemoryDataSize msize, char buffer[VMPA_MAX_LEN], size_t *length)
{
    size_t ret;                             /* Retour de l'impression      */

	if (addr->virtual == VMPA_NO_VIRTUAL)
		ret = snprintf(buffer, VMPA_MAX_LEN, _("(none)"));

	else
		switch (msize)
		{
            case MDS_8_BITS:
				ret = snprintf(buffer, VMPA_MAX_LEN, "0x%02" PRIx64, addr->virtual);
				break;

            case MDS_16_BITS:
				ret = snprintf(buffer, VMPA_MAX_LEN, "0x%04" PRIx64, addr->virtual);
				break;

            case MDS_32_BITS:
				ret = snprintf(buffer, VMPA_MAX_LEN, "0x%08" PRIx64, addr->virtual);
				break;

            case MDS_64_BITS:
				ret = snprintf(buffer, VMPA_MAX_LEN, "0x%016" PRIx64, addr->virtual);
				break;

            default:
				ret = snprintf(buffer, VMPA_MAX_LEN, "0x%" PRIx64, addr->virtual);
				break;

		}

    if (length != NULL)
        *length = ret;

    return buffer;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr   = adresse virtuelle ou physique à traiter.            *
*                msize  = taille de cette adresse, réelle ou désirée.         *
*                buffer = tampon de sortie utilisé à constituer. [OUT]        *
*                length = transmission de la taille du résultat ou NULL. [OUT]*
*                                                                             *
*  Description : Transforme une localisation en chaîne de caractères.         *
*                                                                             *
*  Retour      : Chaîne de caractères constituée.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *vmpa2_to_string(const vmpa2t *addr, MemoryDataSize msize, char buffer[VMPA_MAX_LEN], size_t *length)
{
    char *result;                           /* Résultat à retourner        */

    if (has_virt_addr(addr))
        result = vmpa2_virt_to_string(addr, msize, buffer, length);
    else
        result = vmpa2_phys_to_string(addr, msize, buffer, length);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : buffer = chaîne de caractères à consulter.                   *
*                                                                             *
*  Description : Transforme une chaîne de caractères en position physique.    *
*                                                                             *
*  Retour      : Adresse obtenue.                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

vmpa2t *string_to_vmpa_phy(const char *buffer)
{
    phys_t physical;                        /* Position à retrouver        */

    physical = strtoull(buffer, NULL, 16);

    return make_vmpa(physical, VMPA_NO_VIRTUAL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : buffer = chaîne de caractères à consulter.                   *
*                                                                             *
*  Description : Transforme une chaîne de caractères en adresse virtuelle.    *
*                                                                             *
*  Retour      : Adresse obtenue.                                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

vmpa2t *string_to_vmpa_virt(const char *buffer)
{
    virt_t virtual;                         /* Adresse à retrouver         */

    virtual = strtoull(buffer, NULL, 16);

    return make_vmpa(VMPA_NO_PHYSICAL, virtual);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : base = tronc commun pour les champs de la base de données.   *
*                                                                             *
*  Description : Donne les éléments requis pour la construction d'une table.  *
*                                                                             *
*  Retour      : Partie de requête à insérer dans la requête globale.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *create_vmpa_db_table(const char *base)
{
    char *result;                           /* Requête à retourner         */

    if (base != NULL)
    {
        result = strdup(base);
        result = stradd(result, "_");
    }
    else
        result = NULL;

    result = stradd(result, "phys INTEGER, ");

    if (base != NULL)
    {
        result = stradd(result, base);
        result = stradd(result, "_");
    }

    result = stradd(result, "virt INTEGER");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr   = localisation dont la définition est à définir.      *
*                base   = tronc commun pour les champs de la base de données. *
*                values = tableau d'éléments à consulter.                     *
*                count  = nombre de descriptions renseignées.                 *
*                                                                             *
*  Description : Charge les valeurs utiles pour une localisation.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_vmpa(vmpa2t *addr, const char *base, const bound_value *values, size_t count)
{
    char *name;                             /* Désignation complète        */
    const bound_value *value;               /* Valeur à intégrer           */

    asprintf(&name, "%s%sphys", base != NULL ? base : "", base != NULL ? "_" : "");

    value = find_bound_value(values, count, name);

    free(name);

    if (value == NULL) return false;

    switch (value->type)
    {
        case SQLITE_INT64:
            addr->physical = value->integer64;
            break;

        case SQLITE_NULL:
            addr->physical = VMPA_NO_PHYSICAL;
            break;

        default:
            return false;
            break;

    }

    asprintf(&name, "%s%svirt", base != NULL ? base : "", base != NULL ? "_" : "");

    value = find_bound_value(values, count, name);

    free(name);

    if (value == NULL) return false;

    switch (value->type)
    {
        case SQLITE_INT64:
            addr->virtual = value->integer64;
            break;

        case SQLITE_NULL:
            addr->virtual = VMPA_NO_VIRTUAL;
            break;

        default:
            return false;
            break;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr   = adresse virtuelle ou physique à traiter.            *
*                base   = tronc commun pour les champs de la base de données. *
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

bool store_vmpa(const vmpa2t *addr, const char *base, bound_value **values, size_t *count)
{
    bound_value *value;                     /* Valeur à éditer / définir   */

    *count += 2;
    *values = realloc(*values, *count * sizeof(bound_value));

    value = &(*values)[*count - 2];

    asprintf(&value->name, "%s%sphys", base != NULL ? base : "", base != NULL ? "_" : "");
    value->built_name = true;

    value->type = SQLITE_INT64;

    value->has_value = (addr != NULL);

    if (value->has_value)
        value->integer64 = addr->physical;

    value = &(*values)[*count - 1];

    asprintf(&value->name, "%s%svirt", base != NULL ? base : "", base != NULL ? "_" : "");
    value->built_name = true;

    value->type = SQLITE_INT64;

    value->has_value = (addr != NULL);

    if (value->has_value)
        value->integer64 = addr->virtual;

    return true;

}



/* ---------------------------------------------------------------------------------- */
/*                          AIDES FONCTIONNELLES AUXILIAIRES                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : label  = désignation humaine d'unn symbole de base.          *
*                offset = décalage déterminé à faie apparaître au besoin.     *
*                                                                             *
*  Description : Construit une désignation de symbole avec décalage.          *
*                                                                             *
*  Retour      : Chaîne de caractères constituée à libérer après usage.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *make_symbol_offset(const char *label, phys_t offset)
{
    char *result;                           /* Construction à retourner    */
    size_t length;                          /* Taille de désignation créée */

    if (offset == 0)
        result = strdup(label);

    else
    {
        length = strlen(label) + 1 + VMPA_MAX_LEN + 1;
        result = (char *)calloc(length, sizeof(char));

        snprintf(result, length, "%s+0x%llx", label, (unsigned long long)offset);

    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                          DEFINITION D'UNE ZONE EN MEMOIRE                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : range  = plage à initialiser. [OUT]                          *
*                addr   = position de départ dans la mémoire.                 *
*                length = taille de la plage à constituer.                    *
*                                                                             *
*  Description : Initialise une plage dans l'espace mémoire/physique.         *
*                                                                             *
*  Retour      : Place définie en mémoire.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void init_mrange(mrange_t *range, const vmpa2t *addr, phys_t length)
{
    copy_vmpa(&range->addr, addr);

    range->length = length;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dest = structure de destination pour la copie.               *
*                src  = structure de source pour la copie.                    *
*                                                                             *
*  Description : Copie la définition d'une plage mémoire dans une autre.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void copy_mrange(mrange_t *dest, const mrange_t *src)
{
    copy_vmpa(&dest->addr, &src->addr);

    dest->length = src->length;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = première définition à analyser.                          *
*                b = seconde définition à analyser.                           *
*                                                                             *
*  Description : Compare deux couvertures mémoire selon leurs propriétés.     *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1 (-1 par défaut).        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_mrange(const mrange_t *a, const mrange_t *b)
{
    int result;                             /* Bilan à retourner           */

    result = cmp_vmpa(&a->addr, &b->addr);

    if (result == 0)
    {
        if (a->length < b->length)
            result = -1;
        else if (a->length > b->length)
            result = 1;
        else
            result = 0;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a   = première définition à analyser.                        *
*                b   = seconde définition à analyser.                         *
*                inc = indique si l'adresse peut être une fin de zone.        *
*                                                                             *
*  Description : Compare une couverture mémoire avec une localisation simple. *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1 (-1 par défaut).        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int _cmp_mrange_with_vmpa(const mrange_t *a, const vmpa2t *b, bool inclusive)
{
    int result;                             /* Bilan à retourner           */
    phys_t diff;                            /* Espace entre deux adresses  */

    result = cmp_vmpa(b, &a->addr);

    if (result >= 0)
    {
        diff = compute_vmpa_diff(&a->addr, b);

        /**
         * On prend en compte le cas très particulier des couvertures vides.
         *
         * C'est typiquement le cas avec les espaces de symboles pendant la
         * phase de désassemblage, après laquelle ces espaces deviennent bornés.
         *
         */

        if (diff == 0 && a->length == 0)
            result = 0;

        /**
         * Sinon on regarde simplement si l'adresse est contenue.
         */

        else if (diff < a->length)
            result = 0;

        else if (diff == a->length && inclusive)
            result = 0;

        else
            result = 1;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = première définition à analyser.                          *
*                b = seconde définition à analyser.                           *
*                                                                             *
*  Description : Compare une couverture mémoire avec une localisation simple. *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1 (-1 par défaut).        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_mrange_with_vmpa(const mrange_t *a, const vmpa2t *b)
{
    int result;                             /* Bilan à retourner           */

    result = _cmp_mrange_with_vmpa(a, b, false);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a = première définition à analyser.                          *
*                b = seconde définition à analyser.                           *
*                                                                             *
*  Description : Compare une couverture mémoire avec une localisation simple. *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1 (-1 par défaut).        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int cmp_mrange_with_vmpa_inclusive(const mrange_t *a, const vmpa2t *b)
{
    int result;                             /* Bilan à retourner           */

    result = _cmp_mrange_with_vmpa(a, b, true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : range = zone mémoire à consulter.                            *
*                sub   = éventuelle sous-région à valider.                    *
*                                                                             *
*  Description : Indique si une zone en contient une autre ou non.            *
*                                                                             *
*  Retour      : Bilan de la comparaison : -1, 0 ou 1 (-1 par défaut).        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int mrange_includes_mrange(const mrange_t *range, const mrange_t *sub)
{
    int result;                             /* Bilan à retourner           */
    vmpa2t end;                             /* Seconde extrémité           */

    result = cmp_mrange_with_vmpa(range, get_mrange_addr(sub));

    if (result == 0)
    {
        compute_mrange_end_addr(sub, &end);

        result = cmp_mrange_with_vmpa_inclusive(range, &end);

    }

    return result;

}

/******************************************************************************
*                                                                             *
*  Paramètres  : range = zone mémoire à consulter.                            *
*                sub   = éventuelle sous-région à valider.                    *
*                                                                             *
*  Description : Indique si une zone en contient une autre ou non.            *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool mrange_contains_mrange(const mrange_t *range, const mrange_t *sub)
{
    bool result;                            /* Bilan à retourner           */
    phys_t start;                           /* Point de départ             */

    result = mrange_contains_addr(range, get_mrange_addr(sub));

    if (result)
    {
        start = compute_vmpa_diff(get_mrange_addr(range), get_mrange_addr(sub));
        result = (start + get_mrange_length(sub) <= get_mrange_length(range));
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : range = zone mémoire à consulter.                            *
*                addr  = localisation mémoire à analyser.                     *
*                                                                             *
*  Description : Indique si une localisation est incluse dans une zone ou non.*
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool mrange_contains_addr(const mrange_t *range, const vmpa2t *addr)
{
    bool result;                            /* Bilan à retourner           */
    int ret;                                /* Bilan d'une comparaison     */
    phys_t diff;                            /* Espace entre deux adresses  */

    ret = cmp_vmpa(&range->addr, addr);

    if (ret < 0)
    {
        diff = compute_vmpa_diff(&range->addr, addr);

        if (diff != VMPA_NO_PHYSICAL)
            result = (diff < range->length);
        else
            result = false;

    }

    else if (ret == 0)
        result = true;

    else
        result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : range = zone mémoire à consulter.                            *
*                addr  = localisation mémoire à analyser.                     *
*                                                                             *
*  Description : Indique si une localisation est incluse dans une zone ou non.*
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool mrange_contains_addr_inclusive(const mrange_t *range, const vmpa2t *addr)
{
    bool result;                            /* Bilan à retourner           */
    int ret;                                /* Bilan d'une comparaison     */
    phys_t diff;                            /* Espace entre deux adresses  */

    ret = cmp_vmpa(&range->addr, addr);

    if (ret <= -1)
    {
        diff = compute_vmpa_diff(&range->addr, addr);

        if (diff != VMPA_NO_PHYSICAL)
            result = (diff <= range->length);
        else
            result = false;

    }

    else if (ret == 0)
        result = true;

    else
        result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : range = zone mémoire à consulter.                            *
*                other = autre zone mémoire à manipuler.                      *
*                                                                             *
*  Description : Détermine si deux zones mémoire se chevauchent ou non.       *
*                                                                             *
*  Retour      : Bilan de la consultation.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool mrange_intersects_mrange(const mrange_t *range, const mrange_t *other)
{
    bool result;                            /* Bilan à retourner           */
    vmpa2t end;                             /* Fin d'une zone mémoire      */

    result = false;

    result |= mrange_contains_addr(range, &other->addr);
    result |= mrange_contains_addr(other, &range->addr);

    if (get_mrange_length(other) > 0)
    {
        compute_mrange_end_addr(other, &end);
        deminish_vmpa(&end, 1);
        result |= mrange_contains_addr(range, &end);
    }

    if (get_mrange_length(range) > 0)
    {
        compute_mrange_end_addr(range, &end);
        deminish_vmpa(&end, 1);
        result |= mrange_contains_addr(other, &end);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : range = zone mémoire à consulter.                            *
*                addr  = localisation mémoire à déterminer.                   *
*                                                                             *
*  Description : Calcule la position extérieure finale d'une couverture.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void compute_mrange_end_addr(const mrange_t *range, vmpa2t *addr)
{
    copy_vmpa(addr, &range->addr);
    advance_vmpa(addr, range->length);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : range = élément à venir lire. [OUT]                          *
*                pbuf  = paquet de données où venir puiser les infos.         *
*                                                                             *
*  Description : Lit la définition d'une couverture depuis un tampon.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool unpack_mrange(mrange_t *range, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = unpack_vmpa(&range->addr, pbuf);

    if (result)
        result = extract_packed_buffer(pbuf, (uint64_t *)&range->length, sizeof(uint64_t), true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : range = élément à venir écrire.                              *
*                pbuf  = paquet de données où venir inscrire les infos.       *
*                                                                             *
*  Description : Ecrit la définition d'une couverture dans un tampon.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool pack_mrange(const mrange_t *range, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */

    result = pack_vmpa(&range->addr, pbuf);

    if (result)
        result = extend_packed_buffer(pbuf, (uint64_t *)&range->length, sizeof(uint64_t), true);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rane   = emplacement virtuel ou physique à traiter.          *
*                msize  = taille de cette adresse, réelle ou désirée.         *
*                start  = indique si le début ou la fin est à imprimer.       *
*                buffer = tampon de sortie utilisé à constituer. [OUT]        *
*                length = transmission de la taille du résultat ou NULL. [OUT]*
*                                                                             *
*  Description : Transforme un emplacement physique en chaîne de caractères.  *
*                                                                             *
*  Retour      : Chaîne de caractères constituée.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *mrange_phys_to_string(const mrange_t *range, MemoryDataSize msize, bool start, char buffer[VMPA_MAX_LEN], size_t *length)
{
    vmpa2t tmp;

    if (start)
        vmpa2_phys_to_string(&range->addr, msize, buffer, length);

    else
    {
        copy_vmpa(&tmp, &range->addr);
        advance_vmpa(&tmp, range->length);

        vmpa2_phys_to_string(&tmp, msize, buffer, length);

    }

    return buffer;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rane   = emplacement virtuel ou physique à traiter.          *
*                msize  = taille de cette adresse, réelle ou désirée.         *
*                start  = indique si le début ou la fin est à imprimer.       *
*                buffer = tampon de sortie utilisé à constituer. [OUT]        *
*                length = transmission de la taille du résultat ou NULL. [OUT]*
*                                                                             *
*  Description : Transforme un emplacement virtuel en chaîne de caractères.   *
*                                                                             *
*  Retour      : Chaîne de caractères constituée.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *mrange_virt_to_string(const mrange_t *range, MemoryDataSize msize, bool start, char buffer[VMPA_MAX_LEN], size_t *length)
{
    vmpa2t tmp;

    if (start)
        vmpa2_virt_to_string(&range->addr, msize, buffer, length);

    else
    {
        copy_vmpa(&tmp, &range->addr);
        advance_vmpa(&tmp, range->length);

        vmpa2_virt_to_string(&tmp, msize, buffer, length);

    }

    return buffer;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rane   = emplacement virtuel ou physique à traiter.          *
*                msize  = taille de cette adresse, réelle ou désirée.         *
*                buffer = tampon de sortie utilisé à constituer. [OUT]        *
*                length = transmission de la taille du résultat ou NULL. [OUT]*
*                                                                             *
*  Description : Transforme une taille d'emplacement en chaîne de caractères. *
*                                                                             *
*  Retour      : Chaîne de caractères constituée.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *mrange_length_to_string(const mrange_t *range, MemoryDataSize msize, char buffer[VMPA_MAX_LEN], size_t *length)
{
    return _phys_t_to_string(range->length, msize, buffer, length);

}
