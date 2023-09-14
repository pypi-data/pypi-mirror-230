
/* Chrysalide - Outil d'analyse de fichiers binaires
 * imphash.c - calculs d'empreintes sur la base des importations
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#include "imphash.h"


#include <malloc.h>
#include <stdlib.h>
#include <strings.h>


#include <common/extstr.h>
#include <common/sort.h>
#include <plugins/pe/format.h>
#include <plugins/pe/routine.h>



/* Mémorisation d'un symbole importé */
typedef struct _imported_sym_t
{
    size_t index;                           /* Position dans les imports   */
    char *name;                             /* Désignation pour empreinte  */

} imported_sym_t;

/* Dresse la liste des symboles importés pour un format. */
static imported_sym_t *list_all_pe_imports_for_hash(const GPeFormat *, size_t *);

/* Etablit une comparaison entre deux importations. */
static int compare_imports_by_name(const imported_sym_t *, const imported_sym_t *);

/* Etablit une comparaison entre deux importations. */
static int compare_imports_by_index(const imported_sym_t *, const imported_sym_t *);



/******************************************************************************
*                                                                             *
*  Paramètres  : format = format chargé dont l'analyse est faite.             *
*                count  = taille de la liste retournée. [OUT]                 *
*                                                                             *
*  Description : Dresse la liste des symboles importés pour un format.        *
*                                                                             *
*  Retour      : Liste de symboles mise en place.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static imported_sym_t *list_all_pe_imports_for_hash(const GPeFormat *format, size_t *count)
{
    imported_sym_t *result;                 /* Liste de symboles           */
    GBinFormat *base;                       /* Format basique du binaire   */
    size_t sym_count;                       /* Nombre de ces symboles      */
    size_t i;                               /* Boucle de parcours          */
    GBinSymbol *symbol;                     /* Commodité d'accès           */
    const char *name;                       /* Désignation actuelle        */
    const char *library;                    /* Fichier DLL à charger       */
    char *item;                             /* Nouvelle entrée de la liste */
    char *dot;                              /* Point à raccourcir          */

    result = NULL;
    *count = 0;

    base = G_BIN_FORMAT(format);

    g_binary_format_lock_symbols_rd(base);

    sym_count = g_binary_format_count_symbols(base);

    for (i = 0; i < sym_count; i++)
    {
        symbol = g_binary_format_get_symbol(base, i);

        if (!G_IS_PE_IMPORTED_ROUTINE(symbol))
            goto next;

        name = g_binary_routine_get_name(G_BIN_ROUTINE(symbol));

        if (name == NULL)
            goto next;

        library = g_pe_imported_routine_get_library(G_PE_IMPORTED_ROUTINE(symbol));

        if (library == NULL)
            goto next;

        item = malloc((strlen(library) + 1 + strlen(name) + 1) * sizeof(char));

        strcpy(item, library);

        dot = strchr(item, '.');

        if (dot != NULL)
            *dot = '\0';

        strcat(item, ".");
        strcat(item, name);

        item = strlower(item);

        result = realloc(result, ++(*count) * sizeof(imported_sym_t));

        result[*count - 1].index = g_pe_imported_routine_get_index(G_PE_IMPORTED_ROUTINE(symbol));
        result[*count - 1].name = item;

 next:

        g_object_unref(G_OBJECT(symbol));

    }

    g_binary_format_unlock_symbols_rd(base);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : p1 = première importation à traiter.                         *
*                p2 = seconde importation à traiter.                          *
*                                                                             *
*  Description : Etablit une comparaison entre deux importations.             *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int compare_imports_by_name(const imported_sym_t *p1, const imported_sym_t *p2)
{
    int result;                             /* Bilan à retourner           */

    result = strcmp(p1->name, p2->name);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : p1 = première importation à traiter.                         *
*                p2 = seconde importation à traiter.                          *
*                                                                             *
*  Description : Etablit une comparaison entre deux importations.             *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int compare_imports_by_index(const imported_sym_t *p1, const imported_sym_t *p2)
{
    int result;                             /* Bilan à retourner           */

    result = sort_unsigned_long(p1->index, p2->index);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = format en place à consulter.                        *
*                std    = précise si la méthode de calcul est standard.       *
*                                                                             *
*  Description : Calcule l'empreinte des importations d'un format PE.         *
*                                                                             *
*  Retour      : Empreinte MD5 calculée ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *compute_pe_import_hash(const GPeFormat *format, bool std)
{
    char *result;                           /* Empreinte à retourner       */
    size_t count;                           /* Quantité de symboles        */
    imported_sym_t *list;                   /* Liste de symboles           */
    GChecksum *checksum;                    /* Preneur d'empreinte         */
    size_t i;                               /* Boucle de parcours          */

    result = NULL;

    list = list_all_pe_imports_for_hash(format, &count);

    if (list != NULL)
    {
        if (std)
            qsort(list, count, sizeof(imported_sym_t), (__compar_fn_t)compare_imports_by_name);
        else
            qsort(list, count, sizeof(imported_sym_t), (__compar_fn_t)compare_imports_by_index);

        checksum = g_checksum_new(G_CHECKSUM_MD5);

        for (i = 0; i < count; i++)
        {
            if (i > 0)
                g_checksum_update(checksum, (unsigned char *)",", 1);

            g_checksum_update(checksum, (unsigned char *)list[i].name, strlen(list[i].name));

            free(list[i].name);

        }

        result = strdup(g_checksum_get_string(checksum));

        g_checksum_free(checksum);

        free(list);

    }

    return result;

}
