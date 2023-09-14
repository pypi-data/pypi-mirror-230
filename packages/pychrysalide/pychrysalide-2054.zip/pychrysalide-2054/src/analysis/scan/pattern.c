
/* Chrysalide - Outil d'analyse de fichiers binaires
 * pattern.c - définition de motif à localiser dans du contenu binaire
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#include "pattern.h"


#include <malloc.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>


#include "pattern-int.h"
#include "../../core/logs.h"



/* Initialise la classe des motifs à localiser dans du binaire. */
static void g_search_pattern_class_init(GSearchPatternClass *);

/* Initialise une instance de motif à localiser dans du binaire. */
static void g_search_pattern_init(GSearchPattern *);

/* Supprime toutes les références externes. */
static void g_search_pattern_dispose(GSearchPattern *);

/* Procède à la libération totale de la mémoire. */
static void g_search_pattern_finalize(GSearchPattern *);



/* Indique le type défini pour un motif à localiser. */
G_DEFINE_TYPE(GSearchPattern, g_search_pattern, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des motifs à localiser dans du binaire. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_search_pattern_class_init(GSearchPatternClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_search_pattern_dispose;
    object->finalize = (GObjectFinalizeFunc)g_search_pattern_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de motif à localiser dans du binaire.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_search_pattern_init(GSearchPattern *pattern)
{
    pattern->name = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_search_pattern_dispose(GSearchPattern *pattern)
{
    G_OBJECT_CLASS(g_search_pattern_parent_class)->dispose(G_OBJECT(pattern));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_search_pattern_finalize(GSearchPattern *pattern)
{
    if (pattern->name != NULL)
        free(pattern->name);

    G_OBJECT_CLASS(g_search_pattern_parent_class)->finalize(G_OBJECT(pattern));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = définition de motif à consulter.                   *
*                                                                             *
*  Description : Fournit la désignation attribuée à un motif de recherche.    *
*                                                                             *
*  Retour      : Eventuelle étiquette associée ou NULL.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_search_pattern_get_name(const GSearchPattern *pattern)
{
    char *result;                           /* Désignation à retourner     */

    result = pattern->name;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = définition de motif à consulter.                   *
*                name    = désignation en tant que variable locale.           *
*                len     = taille de cette désignation.                       *
*                                                                             *
*  Description : Inscrit la désignation attribuée à un motif de recherche.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_search_pattern_set_name(GSearchPattern *pattern, const char *name, size_t len)
{
    if (pattern->name != NULL)
        free(pattern->name);

    if (name == NULL)
        pattern->name = NULL;
    else
        pattern->name = strndup(name, len);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = définition de motif à considérer.                  *
*                context = contexte de l'analyse à mener.                     *
*                fd      = canal d'écriture.                                  *
*                                                                             *
*  Description : Affiche un motif de recherche au format texte.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_search_pattern_output_to_text(const GSearchPattern *pattern, GScanContext *context, int fd)
{
    GSearchPatternClass *class;             /* Classe à activer            */

    class = G_SEARCH_PATTERN_GET_CLASS(pattern);

    class->to_text(pattern, context, fd);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = définition de motif à considérer.                  *
*                context = contexte de l'analyse à mener.                     *
*                                                                             *
*  Description : Convertit un motif de recherche en texte.                    *
*                                                                             *
*  Retour      : Données textuelles ou NULL en cas d'erreur.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_search_pattern_convert_as_text(const GSearchPattern *pattern, GScanContext *context)
{
    char *result;                           /* Données à retourner         */
    char *name;                             /* Nom "unique" pour le canal  */
    int ret;                                /* Bilan de création de nom    */
    int fd;                                 /* Canal d'écriture            */
    struct stat info;                       /* Infos. incluant une taille  */
    ssize_t got;                            /* Données effectivement relues*/

    static unsigned long long counter = 0;

    result = NULL;

    ret = asprintf(&name, "rost-pattern2text-%llu", counter++);
    if (ret == -1) goto exit;

    fd = memfd_create(name, MFD_CLOEXEC);
    if (fd == -1)
    {
        LOG_ERROR_N("memfd_create");
        goto exit_with_name;
    }

    g_search_pattern_output_to_text(pattern, context, fd);

    ret = fstat(fd, &info);
    if (ret != 0)
    {
        LOG_ERROR_N("fstat");
        goto exit_with_name_and_fd;
    }

    result = malloc((info.st_size + 1) * sizeof(char));

    lseek(fd, SEEK_SET, 0);

    got = read(fd, result, info.st_size);
    if (got != info.st_size)
    {
        LOG_ERROR_N("read");
        free(result);
        goto exit_with_name_and_fd;
    }

    result[info.st_size] = '\0';

 exit_with_name_and_fd:

    close(fd);

 exit_with_name:

    free(name);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = définition de motif à considérer.                  *
*                context  = contexte de l'analyse à mener.                    *
*                padding  = éventuel bourrage initial à placer ou NULL.       *
*                level    = profondeur actuelle.                              *
*                fd       = canal d'écriture.                                 *
*                trailing = impose une virgule finale ?                       *
*                                                                             *
*  Description : Affiche un motif de recherche au format JSON.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_search_pattern_output_to_json(const GSearchPattern *pattern, GScanContext *context, const sized_string_t *padding, unsigned int level, int fd, bool trailing)
{
    unsigned int i;                         /* Boucle de parcours          */
    GSearchPatternClass *class;             /* Classe à activer            */

    /* Introduction */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    write(fd, "{\n", 2);

    /* Désignation du motif */

    for (i = 0; i < (level + 1); i++)
        write(fd, padding->data, padding->len);

    write(fd, "\"name\": \"$", 10);

    write(fd, pattern->name, strlen(pattern->name));

    write(fd, "\",\n", 3);

    /* Affichage du contenu */

    class = G_SEARCH_PATTERN_GET_CLASS(pattern);

    class->to_json(pattern, context, padding, level + 1, fd);

    /* Conclusion */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    if (trailing)
        write(fd, "},\n", 3);
    else
        write(fd, "}\n", 2);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : pattern = définition de motif à considérer.                  *
*                context = contexte de l'analyse à mener.                     *
*                                                                             *
*  Description : Convertit un motif de recherche en JSON.                     *
*                                                                             *
*  Retour      : Données textuelles au format JSON ou NULL en cas d'erreur.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_search_pattern_convert_as_json(const GSearchPattern *pattern, GScanContext *context)
{
    char *result;                           /* Données à retourner         */
    char *name;                             /* Nom "unique" pour le canal  */
    int ret;                                /* Bilan de création de nom    */
    int fd;                                 /* Canal d'écriture            */
    sized_string_t padding;                 /* Bourrage pour le JSON       */
    struct stat info;                       /* Infos. incluant une taille  */
    ssize_t got;                            /* Données effectivement relues*/

    static unsigned long long counter = 0;

    result = NULL;

    ret = asprintf(&name, "rost-pattern2json-%llu", counter++);
    if (ret == -1) goto exit;

    fd = memfd_create(name, MFD_CLOEXEC);
    if (fd == -1)
    {
        LOG_ERROR_N("memfd_create");
        goto exit_with_name;
    }

    padding.data = "   ";
    padding.len = 3;

    g_search_pattern_output_to_json(pattern, context, &padding, 0, fd, false);

    ret = fstat(fd, &info);
    if (ret != 0)
    {
        LOG_ERROR_N("fstat");
        goto exit_with_name_and_fd;
    }

    result = malloc((info.st_size + 1) * sizeof(char));

    lseek(fd, SEEK_SET, 0);

    got = read(fd, result, info.st_size);
    if (got != info.st_size)
    {
        LOG_ERROR_N("read");
        free(result);
        goto exit_with_name_and_fd;
    }

    result[info.st_size] = '\0';

 exit_with_name_and_fd:

    close(fd);

 exit_with_name:

    free(name);

 exit:

    return result;

}
