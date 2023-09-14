
/* Chrysalide - Outil d'analyse de fichiers binaires
 * build.c - collecte des informations à enregistrer
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#include "build.h"


#include <malloc.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>



/* ----------------------------- GESTION DES ETIQUETTES ----------------------------- */


/* Empreinte d'une étiquette */
typedef struct _govm_label
{
    char *name;                             /* Désignation humaine         */

    uint16_t offset;                        /* Position dans le code       */

    uint16_t *references;                   /* Emplacement d'utilisations  */
    size_t ref_count;                       /* Quantité d'emplacements     */

} govm_label;


#define INVALID_OFFSET 0xffff


/* Met en place une mémoire destinée à une étiquette. */
static govm_label *create_govm_label(const char *);

/* Libère la mémoire occupée par une étiquette. */
static void delete_govm_label(govm_label *);

/* Recherche une étiquette correspondant à un nom donné. */
static govm_label *find_govm_label_in_list(govm_label **, size_t, const char *);

/* Inscrit un nouvel emplacement à modifier après coup. */
static void attach_new_ref_to_govm_label(govm_label *, uint16_t);

/* Met à jour tous les détournements de flot liés à l'étiquette. */
static bool resolve_all_refs_of_govm_label(const govm_label *, uint16_t *, govm_info *);



/* -------------------------- PROCEDURES POUR L'ASSEMBLAGE -------------------------- */


/* Regroupement des informations à enregistrer */
struct _govm_info
{
    bool little;                            /* Architecture choisie        */

    uint16_t csize;                         /* Taille du code              */
    uint16_t dsize;                         /* Taille des données          */
    uint16_t isize;                         /* ???                         */
    uint16_t bsize;                         /* ???                         */

    uint16_t start;                         /* Position de départ          */

    bin_t *code;                            /* Code binaire                */
    size_t allocated;                       /* Taille allouée en mémoire   */

    govm_label **labels;                    /* Nombre d'étiquettes utiles  */
    size_t labels_count;                    /* Quantité de ces étiquettes  */

    bool warn;                              /* Affichage d'avertissements  */

};


#define ALLOC_CHUCK     20


/* Ajoute une instruction aux informations à enregistrer. */
static bool add_govm_instruction_code(govm_info *, bin_t);

/* Inscrit une nouvelle étiquette vierge. */
static govm_label *insert_new_govm_label(govm_info *, const char *);



/* ---------------------------------------------------------------------------------- */
/*                               GESTION DES ETIQUETTES                               */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : name = désignation humaine de l'étiquette.                   *
*                                                                             *
*  Description : Met en place une mémoire destinée à une étiquette.           *
*                                                                             *
*  Retour      : Structure de représentation initialisée.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static govm_label *create_govm_label(const char *name)
{
    govm_label *result;                     /* Structure à retourner       */
    size_t len;                             /* Taille du nom pour analyse  */

    result = (govm_label *)calloc(1, sizeof(govm_label));

    result->name = strdup(name);

    len = strlen(name);
    if (name[len - 1] == ':') result->name[len - 1] = '\0';

    result->offset = INVALID_OFFSET;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : label = étiquette à supprimer de la mémoire.                 *
*                                                                             *
*  Description : Libère la mémoire occupée par une étiquette.                 *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void delete_govm_label(govm_label *label)
{
    free(label->name);

    if (label->references != NULL)
        free(label->references);

    free(label);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : list  = liste d'éléments à parcourir.                        *
*                count = taille de la liste.                                  *
*                name  = nom de l'étiquette à chercher.                       *
*                                                                             *
*  Description : Recherche une étiquette correspondant à un nom donné.        *
*                                                                             *
*  Retour      : Adresse de l'étiquette trouvée ou NULL.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static govm_label *find_govm_label_in_list(govm_label **list, size_t count, const char *name)
{
    govm_label *result;                     /* Résultat à renvoyer         */
    size_t len;                             /* Longueur de comparaison     */
    size_t i;                               /* Boucle de parcours          */

    result = NULL;

    len = strlen(name);
    if (name[len - 1] == ':') len--;

    for (i = 0; i < count && result == NULL; i++)
    {
        if (list[i]->name == NULL) continue;

        if (strncmp(list[i]->name, name, len) == 0)
            result = list[i];

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : label = élément à compléter.                                 *
*                count = taille de la liste.                                  *
*                name  = nom de l'étiquette à chercher.                       *
*                                                                             *
*  Description : Inscrit un nouvel emplacement à modifier après coup.         *
*                                                                             *
*  Retour      : Adresse de l'étiquette trouvée ou NULL.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void attach_new_ref_to_govm_label(govm_label *label, uint16_t ref)
{
    label->references = (uint16_t *)realloc(label->references,
                                            ++label->ref_count * sizeof(uint16_t));

    label->references[label->ref_count - 1] = ref;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : label = élément à manipuler.                                 *
*                pc    = emplacement de la tête d'écriture à modifier.        *
*                info  = informations globales pour l'ajout.                  *
*                                                                             *
*  Description : Met à jour tous les détournements de flot liés à l'étiquette.*
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool resolve_all_refs_of_govm_label(const govm_label *label, uint16_t *pc, govm_info *info)
{
    bool result;                            /* Bilan à retourner           */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    if (label->offset == INVALID_OFFSET)
    {
        fprintf(stderr, "Label '%s' used, but never defined !\n", label->name);
        return false;
    }

    if (label->ref_count == 0 && info->warn && strcmp(label->name, "start") != 0)
        fprintf(stderr, "Label '%s' defined, but never used !\n", label->name);

    for (i = 0; i < label->ref_count && result; i++)
    {
        *pc = label->references[i];
        result = encode_govm_number(info, label->offset);
    }

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                            PROCEDURES POUR L'ASSEMBLAGE                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : little = architecture en petit boutisme ?                    *
*                warn   = affichage des avertissements ?                      *
*                                                                             *
*  Description : Met en place une future collecte d'informations.             *
*                                                                             *
*  Retour      : Ensemble d'informations initialisées.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

govm_info *create_govm_info(bool little, bool warn)
{
    govm_info *result;                      /* Structure à retourner       */

    result = (govm_info *)calloc(1, sizeof(govm_info));

    result->little = little;
    result->warn = warn;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = informations à libérer de la mémoire.                 *
*                                                                             *
*  Description : Supprime de la mémoire toutes les informations collectées.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_govm_info(govm_info *info)
{
    size_t i;                               /* Boucle de parcours          */

    if (info->allocated > 0)
        free(info->code);

    if (info->labels_count > 0)
    {
        for (i = 0; i < info->labels_count; i++)
            delete_govm_label(info->labels[i]);

        free(info->labels);

    }

    free(info);

}








bool write_u16(int fd, uint16_t val);

bool write_u16(int fd, uint16_t val)
{
    ssize_t len;                            /* Quantité de données écrites */

    len = write(fd, &val, 2);

    return (len == 2);

}









/******************************************************************************
*                                                                             *
*  Paramètres  : info  = ensemble à mettre à jour.                            *
*                value = valeur à ajouter à la section de code.               *
*                                                                             *
*  Description : Ajoute une instruction aux informations à enregistrer.       *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool add_govm_instruction_code(govm_info *info, bin_t value)
{
    bool even;                              /* Zone pour le demi-octet     */

    if (info->csize / 2 == info->allocated)
    {
        info->allocated += ALLOC_CHUCK;
        info->code = (bin_t *)realloc(info->code, info->allocated * sizeof(bin_t));
        memset(&info->code[info->csize / 2], 0, ALLOC_CHUCK * sizeof(bin_t));
    }

    even = (info->csize % 2 == 0);
    if (info->little) even = !even;

    if (even)
        info->code[info->csize / 2] |= (value & 0x0f) << 4;
    else
        info->code[info->csize / 2] |= (value & 0x0f);

    info->csize++;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble à mettre à jour.                             *
*                id   = identifiant de l'instruction à exporter.              *
*                                                                             *
*  Description : Ajoute une instruction aux informations à enregistrer.       *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool encode_govm_instruction(govm_info *info, GoVMOpcodes id)
{
    bool result;                            /* Bilan à renvoyer            */
    bin_t opcode;                           /* Octet d'encodage à écrire   */

    opcode = get_govm_instruction_opcode(id);

    if (opcode >= 0x08)
    {
        result = add_govm_instruction_code(info, (opcode & 0x0f) | 0x08);
        result &= add_govm_instruction_code(info, opcode >> 3);
    }
    else
        result = add_govm_instruction_code(info, opcode);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info  = ensemble à mettre à jour.                            *
*                value = valeur à placer directement dans le code.            *
*                                                                             *
*  Description : Ajoute une valeur entière dans le code même.                 *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool encode_govm_number(govm_info *info, uint16_t value)
{
    bool result;                            /* Bilan à renvoyer            */
    size_t i;                               /* Boucle de parcours          */

    result = true;

    if (info->little)
        for (i = 0; i < 16 && result; i += 4)
            result = add_govm_instruction_code(info, (value >> i) & 0x0f);
    else
        for (i = 16; i > 0 && result; i -= 4)
            result = add_govm_instruction_code(info, (value >> (i - 4)) & 0x0f);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble à mettre à jour.                             *
*                name = désignation humaine de la nouvelle étiquette.         *
*                                                                             *
*  Description : Inscrit une nouvelle étiquette vierge.                       *
*                                                                             *
*  Retour      : Adresse de l'étiquette créée.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static govm_label *insert_new_govm_label(govm_info *info, const char *name)
{
    govm_label *result;                     /* Etiquette à retourner       */

    result = create_govm_label(name);

    info->labels = (govm_label **)realloc(info->labels, ++info->labels_count * sizeof(govm_label *));
    info->labels[info->labels_count - 1] = result;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble à mettre à jour.                             *
*                name = désignation humaine de la nouvelle étiquette.         *
*                                                                             *
*  Description : Enregistre un nouvel emplacement d'étiquette.                *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool register_govm_label(govm_info *info, const char *name)
{
    govm_label *label;                      /* Etiquette à créer           */

    label = find_govm_label_in_list(info->labels, info->labels_count, name);

    if (label == NULL)
        label = insert_new_govm_label(info, name);

    if (label->offset != INVALID_OFFSET)
    {
        fprintf(stderr, "Label '%s' already defined !", label->name);
        return false;
    }

    label->offset = info->csize;

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble à mettre à jour.                             *
*                id   = identifiant de l'instruction à utiliser.              *
*                name = désignation humaine de l'étiquette visée.             *
*                                                                             *
*  Description : Exécute un détournement de flot via une étiquette.           *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool encode_reference_to_govm_label(govm_info *info, GoVMOpcodes id, const char *name)
{
    govm_label *label;                      /* Etiquette à modifier        */

    if (!encode_govm_instruction(info, GOP_LI))
        return false;

    label = find_govm_label_in_list(info->labels, info->labels_count, name);

    if (label == NULL)
        label = insert_new_govm_label(info, name);

    attach_new_ref_to_govm_label(label, info->csize);

    if (!encode_govm_number(info, 0x0000))
        return false;

    return encode_govm_instruction(info, id);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : info = ensemble à initialiser.                               *
*                fd   = flux ouvert en écriture.                              *
*                                                                             *
*  Description : Procède à l'enregistrement d'un shellcode pour GoVM.         *
*                                                                             *
*  Retour      : true si l'opération s'est bien déroulée, false sinon.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool write_govm_info(govm_info *info, int fd)
{
    bool result;                            /* Bilan à retourner           */
    uint16_t tmp;                           /* Sauvegarde de la quantité   */
    size_t i;                               /* Boucle de parcours          */
    ssize_t len;                            /* Quantité de données écrites */
    uint16_t expected;                      /* Quantité de données à écrire*/
    govm_label *label;                      /* Etiquette pour le début     */

    result = true;

    tmp = info->csize;

    for (i = 0; i < info->labels_count && result; i++)
        result = resolve_all_refs_of_govm_label(info->labels[i], &info->csize, info);

    info->csize = tmp;

    if (!result) return false;

    len = write(fd, "GOVM", 4);
    result = (len != 4);

    if (info->little) len = write(fd, "\x10", 1);
    else len = write(fd, "\x11", 1);

    result = (len != 1);

    /* Egalisation */
    if (info->csize % 2 != 0)
    {
        encode_govm_instruction(info, GOP_LI);
        encode_govm_number(info, 0xffff);
        encode_govm_instruction(info, GOP_POP);
    }

    expected = (info->csize % 2 == 0 ? info->csize / 2 : info->csize / 2 + 1);
    expected *= sizeof(bin_t);

    result &= write_u16(fd, expected);
    result &= write_u16(fd, info->dsize);
    result &= write_u16(fd, info->isize);
    result &= write_u16(fd, info->bsize);

    label = find_govm_label_in_list(info->labels, info->labels_count, "start");
    if (label != NULL) info->start = label->offset;

    result &= write_u16(fd, info->start);

    len = write(fd, info->code, expected);
    result = (len != expected);

    return result;

}
