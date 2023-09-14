
/* Chrysalide - Outil d'analyse de fichiers binaires
 * writer.c - mise en place de commentaires adaptés aux appels système
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include "writer.h"


#include <malloc.h>
#include <string.h>


#include <analysis/db/items/comment.h>
#include <common/extstr.h>



/* Empilement de commentaire à une adresse donnée */
typedef struct _comment_data
{
    vmpa2t addr;                            /* Emplacement de l'insertion  */

    char **text;                            /* Pièces de texte rapportées  */
    size_t count;                           /* Nombre de ces pièces        */

} comment_data;

/* Mémorisation des commentaires à insérer */
struct _comment_writer
{
    comment_data *comments;                 /* Définitions de commentaire  */
    size_t count;                           /* Nombre de ces commentaires  */

};


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un espace de conservation pour commentaires d'appels.   *
*                                                                             *
*  Retour      : Structure de mémorisation en place.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

comment_writer *create_comment_writer(void)
{
    comment_writer *result;                 /* Structure à retourner       */

    result = (comment_writer *)malloc(sizeof(comment_writer));

    result->comments = NULL;
    result->count = 0;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : writer  = ensemble de commentaires conservés à supprimer.    *
*                                                                             *
*  Description : Détruit la conservation de commentaires pour appels.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void delete_comment_writer(comment_writer *writer)
{
    size_t i;                               /* Boucle de parcours #1       */
    comment_data *data;                     /* Facilités d'accès           */
    size_t k;                               /* Boucle de parcours #2       */

    for (i = 0; i < writer->count; i++)
    {
        data = &writer->comments[i];

        for (k = 0; k < data->count; k++)
            free(data->text[k]);

        if (data->text != NULL)
            free(data->text);

    }

    if (writer->comments != NULL)
        free(writer->comments);

    free(writer);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : writer = ensemble de commentaires conservés.                 *
*                text   = commentaire humainement lisible à insérer.          *
*                at     = instruction dont l'adresse est la destination visée.*
*                                                                             *
*  Description : Complète un commentaire ou en insére un nouveau.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void add_comment_at(comment_writer *writer, const char *text, GArchInstruction *at)
{
    const mrange_t *range;                  /* Couverture d'une instruction*/
    const vmpa2t *addr;                     /* Adresse de début liée       */
    size_t i;                               /* Boucle de parcours          */
    comment_data *target;                   /* Commentaire à éditer        */
    bool new;                               /* Age de ce commentaire       */

    range = g_arch_instruction_get_range(at);
    addr = get_mrange_addr(range);

    for (i = 0; i < writer->count; i++)
    {
        target = &writer->comments[i];

        if (cmp_vmpa(addr, &target->addr) == 0)
            break;

    }

    new = (i == writer->count);

    if (new)
    {
        writer->comments = (comment_data *)realloc(writer->comments, ++writer->count * sizeof(comment_data));

        target = &writer->comments[writer->count - 1];

        copy_vmpa(&target->addr, addr);

        target->text = NULL;
        target->count = 0;

    }

    for (i = 0; i < target->count; i++)
        if (strcmp(target->text[i], text) == 0)
            break;

    if (i == target->count)
    {
        target->text = (char **)realloc(target->text, ++target->count * sizeof(char *));

        target->text[target->count - 1] = strdup(text);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : writer  = ensemble de commentaires conservés.                *
*                preload = contexte de désassemblage avec info préchargées.   *
*                                                                             *
*  Description : Applique tous les commentaires à l'écriture anticipée.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void write_all_comments(comment_writer *writer, GPreloadInfo *preload)
{
    size_t i;                               /* Boucle de parcours #1       */
    comment_data *target;                   /* Commentaire à éditer        */
    char *text;                             /* Texte du commentaire complet*/
    size_t k;                               /* Boucle de parcours #2       */
    size_t index;                           /* Indice d'un existant ?      */
    GDbComment *comment;                    /* Commentaire final à intégrer*/

    for (i = 0; i < writer->count; i++)
    {
        target = &writer->comments[i];

        /* Construction de la nouveauté */

        text = NULL;

        for (k = 0; k < target->count; k++)
        {
            if (k > 0)
                text = stradd(text, " / ");

            text = stradd(text, target->text[k]);

        }

        /* Inclusion de l'existant */

        g_preload_info_lock_comments(preload);

        comment = g_preload_info_find_comment_at(preload, &target->addr, &index);

        if (comment == NULL)
        {
            comment = g_db_comment_new(&target->addr, CET_INLINED, BLF_HAS_CODE, text);
            g_db_item_add_flag(G_DB_ITEM(comment), DIF_VOLATILE);

            _g_preload_info_add_comment(preload, comment);

        }

        else
        {
            text = strprep(text, " / ");
            text = strprep(text, g_db_comment_get_text(comment));

            g_object_unref(G_OBJECT(comment));

            comment = g_db_comment_new(&target->addr, CET_INLINED, BLF_HAS_CODE, text);
            g_db_item_add_flag(G_DB_ITEM(comment), DIF_VOLATILE);

            g_preload_info_replace_comment_at(preload, index, comment);

        }

        g_preload_info_unlock_comments(preload);

        free(text);

    }

}
