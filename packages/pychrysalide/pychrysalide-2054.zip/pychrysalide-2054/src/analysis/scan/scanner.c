
/* Chrysalide - Outil d'analyse de fichiers binaires
 * scanner.c - parcours de contenus à la recherche de motifs
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


#include "scanner.h"


#include <assert.h>
#include <libgen.h>
#include <malloc.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>


#include "decl.h"
#include "scanner-int.h"
#include "../contents/file.h"
#include "../../common/extstr.h"
#include "../../core/logs.h"



/* Initialise la classe des recherches dans du binaire. */
static void g_content_scanner_class_init(GContentScannerClass *);

/* Initialise une instance de recherche dans du binaire. */
static void g_content_scanner_init(GContentScanner *);

/* Supprime toutes les références externes. */
static void g_content_scanner_dispose(GContentScanner *);

/* Procède à la libération totale de la mémoire. */
static void g_content_scanner_finalize(GContentScanner *);

/* Intègre une nouvelle règle de détection. */
static bool _g_content_scanner_add_rule(GContentScanner *, GScanRule *);



/* Indique le type défini pour une recherche dans du binaire. */
G_DEFINE_TYPE(GContentScanner, g_content_scanner, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des recherches dans du binaire.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_scanner_class_init(GContentScannerClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_content_scanner_dispose;
    object->finalize = (GObjectFinalizeFunc)g_content_scanner_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de recherche dans du binaire.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_scanner_init(GContentScanner *scanner)
{
    scanner->filename = NULL;

    scanner->rules = NULL;
    scanner->rule_count = 0;

    scanner->data_backend = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_scanner_dispose(GContentScanner *scanner)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < scanner->rule_count; i++)
        g_clear_object(&scanner->rules[i]);

    g_clear_object(&scanner->data_backend);

    G_OBJECT_CLASS(g_content_scanner_parent_class)->dispose(G_OBJECT(scanner));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_content_scanner_finalize(GContentScanner *scanner)
{
    if (scanner->filename != NULL)
        free(scanner->filename);

    if (scanner->rules != NULL)
        free(scanner->rules);

    G_OBJECT_CLASS(g_content_scanner_parent_class)->finalize(G_OBJECT(scanner));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : text = définitions textuelles de règles de recherche.        *
*                                                                             *
*  Description : Prépare une recherche de motifs dans du contenu binaire.     *
*                                                                             *
*  Retour      : Mécanismes mis en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GContentScanner *g_content_scanner_new_from_text(const char *text)
{
    GContentScanner *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_CONTENT_SCANNER, NULL);

    if (!g_content_scanner_create_from_text(result, text))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner = scanner de contenus à initialiser pleinement.      *
*                text    = définitions textuelles de règles de recherche.     *
*                                                                             *
*  Description : Met en place un scanner de contenus binaires.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_content_scanner_create_from_text(GContentScanner *scanner, const char *text)
{
    bool result;                            /* Bilan à retourner           */
    size_t length;                          /* Taille de la définition     */

    length = strlen(text);

    result = process_rules_definitions(scanner, text, length);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : filename = chemin vers des définitions de règles.            *
*                                                                             *
*  Description : Prépare une recherche de motifs dans du contenu binaire.     *
*                                                                             *
*  Retour      : Mécanismes mis en place.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GContentScanner *g_content_scanner_new_from_file(const char *filename)
{
    GContentScanner *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_CONTENT_SCANNER, NULL);

    if (!g_content_scanner_create_from_file(result, filename))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner  = scanner de contenus à initialiser pleinement.     *
*                filename = chemin vers des définitions de règles.            *
*                                                                             *
*  Description : Met en place un scanner de contenus binaires.                *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_content_scanner_create_from_file(GContentScanner *scanner, const char *filename)
{
    bool result;                            /* Bilan à retourner           */
    GBinContent *content;                   /* Fichier à parcourir         */
    phys_t size;                            /* Taille du contenu associé   */
    vmpa2t start;                           /* Tête de lecture             */
    const bin_t *data;                      /* Données à consulter         */

    result = false;

    content = g_file_content_new(filename);
    if (content == NULL) goto no_content;

    scanner->filename = strdup(filename);

    size = g_binary_content_compute_size(content);

    g_binary_content_compute_start_pos(content, &start);
    data = g_binary_content_get_raw_access(content, &start, size);

    result = process_rules_definitions(scanner, (char *)data, size);

    g_object_unref(G_OBJECT(content));

 no_content:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner = scanner de contenus à consulter.                   *
*                                                                             *
*  Description : Indique le chemin d'un éventuel fichier de source.           *
*                                                                             *
*  Retour      : Chemin d'un éventuel fichier de définitions ou NULL.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_content_scanner_get_filename(const GContentScanner *scanner)
{
    const char *result;                     /* Chemin à retourner          */

    result = scanner->filename;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner = gestionnaire de recherche à compléter.             *
*                path    = chemin vers une définition de règles à intégrer.   *
*                                                                             *
*  Description : Inclut les définitions d'un fichier de règles externe.       *
*                                                                             *
*  Retour      : Bilan de l'inclusion à retourner.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_content_scanner_include_resource(GContentScanner *scanner, const char *path)
{
    bool result;                            /* Bilan à retourner           */
    GContentScanner *included;              /* Définition à inclure        */
    char *tmp;                              /* Copie de travail            */
    char *filename;                         /* Chemin d'accès reconstruit  */
    size_t i;                               /* Boucle de parcours          */
    const char *inc_name;                   /* Nom de la nouvelle règle    */

    /* Cas le plus simple : un chemin absolu */
    if (path[0] == '/')
        included = g_content_scanner_new_from_file(path);

    /* Chemin relatif à l'emplacement de la définition courante ? */
    else if (scanner->filename != NULL)
    {
        tmp = strdup(scanner->filename);

        filename = strdup(dirname(tmp));
        filename = stradd(filename, G_DIR_SEPARATOR_S);
        filename = stradd(filename, path);

        included = g_content_scanner_new_from_file(filename);

        free(filename);
        free(tmp);

    }

    else
        included = NULL;

    /* Inclusion des règles chargées */

    result = (included != NULL);

    if (result)
    {
        for (i = 0; i < included->rule_count && result; i++)
        {
            result = _g_content_scanner_add_rule(scanner, included->rules[i]);

            if (!result)
            {
                inc_name = g_scan_rule_get_name(included->rules[i], (fnv64_t []) { 0 });

                log_variadic_message(LMT_ERROR, "Can not import from '%s': rule '%s' already exists!",
                                     path, inc_name);

            }

        }

        g_object_unref(G_OBJECT(included));

    }

    return result;



}


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner = gestionnaire de recherche à compléter.             *
*                rule    = règle de détection à intégrer.                     *
*                                                                             *
*  Description : Intègre une nouvelle règle de détection.                     *
*                                                                             *
*  Retour      : Bilan de l'ajout à retourner.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool _g_content_scanner_add_rule(GContentScanner *scanner, GScanRule *rule)
{
    bool result;                            /* Bilan à retourner           */
    const char *inc_name;                   /* Nom de la nouvelle règle    */
    fnv64_t inc_hash;                       /* Empreinte de ce nom         */
    size_t i;                               /* Boucle de parcours          */
    const char *cur_name;                   /* Nom d'une règle en place    */
    fnv64_t cur_hash;                       /* Empreinte de ce nom         */

    result = false;

    inc_name = g_scan_rule_get_name(rule, &inc_hash);

    for (i = 0; i < scanner->rule_count; i++)
    {
        cur_name = g_scan_rule_get_name(scanner->rules[i], &cur_hash);

        if (inc_hash != cur_hash)
            continue;

        if (strcmp(inc_name, cur_name) == 0)
            goto exit_add;

    }

    result = true;

    scanner->rules = realloc(scanner->rules, ++scanner->rule_count * sizeof(GScanRule *));

    scanner->rules[scanner->rule_count - 1] = rule;

    g_object_ref(G_OBJECT(rule));

 exit_add:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner = gestionnaire de recherche à compléter.             *
*                rule    = règle de détection à intégrer.                     *
*                                                                             *
*  Description : Intègre une nouvelle règle de détection.                     *
*                                                                             *
*  Retour      : Bilan de l'ajout à retourner.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_content_scanner_add_rule(GContentScanner *scanner, GScanRule *rule)
{
    bool result;                            /* Bilan à retourner           */
    const char *inc_name;                   /* Nom de la nouvelle règle    */

    result = _g_content_scanner_add_rule(scanner, rule);

    if (!result)
    {
        inc_name = g_scan_rule_get_name(rule, (fnv64_t []) { 0 });

        log_variadic_message(LMT_ERROR, "Can not add rule: '%s' already exists!", inc_name);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner = gestionnaire de recherche à compléter.             *
*                options = ensemble des options d'analyses à respecter.       *
*                content = contenu à parcourir et analyser.                   *
*                                                                             *
*  Description : Lance une analyse d'un contenu binaire.                      *
*                                                                             *
*  Retour      : Contexte de suivi pour l'analyse menée.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanContext *g_content_scanner_analyze(GContentScanner *scanner, GScanOptions *options, GBinContent *content)
{
    GScanContext *result;                   /* Bilan global à retourner    */
    bool status;                            /* Bilan d'opération locale    */
    size_t i;                               /* Boucle de parcours          */

    result = g_scan_context_new(options);

    if (scanner->data_backend == NULL)
    {
        scanner->data_backend = g_object_new(g_scan_options_get_backend_for_data(options), NULL);
        assert(scanner->data_backend != NULL);

        status = (scanner->data_backend != NULL);

        for (i = 0; i < scanner->rule_count && status; i++)
            status = g_scan_rule_setup_backend(scanner->rules[i], scanner->data_backend, result);

        if (!status)
        {
            g_clear_object(&result);
            goto exit;
        }

    }

    g_scan_context_set_content(result, content);

    g_engine_backend_run_scan(scanner->data_backend, result);

    g_scan_context_mark_scan_as_done(result);

    for (i = 0; i < scanner->rule_count; i++)
        g_scan_rule_check(scanner->rules[i], scanner->data_backend, result);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner = gestionnaire de recherche à consulter.             *
*                context = contexte de l'analyse à mener.                     *
*                full    = force un affichage complet des résultats.          *
*                fd      = canal d'écriture.                                  *
*                                                                             *
*  Description : Affiche un gestionnaire de recherches au format texte.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_content_scanner_output_to_text(const GContentScanner *scanner, GScanContext *context, bool full, int fd)
{
    size_t i;                               /* Boucle de parcours          */

    /* Sous-traitance aux règles */

    for (i = 0; i < scanner->rule_count; i++)
        g_scan_rule_output_to_text(scanner->rules[i], context, full, fd);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner = gestionnaire de recherche à consulter.             *
*                context = contexte de l'analyse à mener.                     *
*                                                                             *
*  Description : Convertit un gestionnaire de recherches en texte.            *
*                                                                             *
*  Retour      : Données textuelles ou NULL en cas d'erreur.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_content_scanner_convert_to_text(const GContentScanner *scanner, GScanContext *context)
{
    char *result;                           /* Données à retourner         */
    char *name;                             /* Nom "unique" pour le canal  */
    int ret;                                /* Bilan de création de nom    */
    int fd;                                 /* Canal d'écriture            */
    struct stat info;                       /* Infos. incluant une taille  */
    ssize_t got;                            /* Données effectivement relues*/

    static unsigned long long counter = 0;

    result = NULL;

    ret = asprintf(&name, "rost-scanner2text-%llu", counter++);
    if (ret == -1) goto exit;

    fd = memfd_create(name, MFD_CLOEXEC);
    if (fd == -1)
    {
        LOG_ERROR_N("memfd_create");
        goto exit_with_name;
    }

    g_content_scanner_output_to_text(scanner, context, true, fd);

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
*  Paramètres  : scanner = gestionnaire de recherche à consulter.             *
*                context = contexte de l'analyse à mener.                     *
*                padding = éventuel bourrage initial à placer ou NULL.        *
*                level   = profondeur actuelle.                               *
*                fd      = canal d'écriture.                                  *
*                                                                             *
*  Description : Affiche un gestionnaire de recherches au format JSON.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_content_scanner_output_to_json(const GContentScanner *scanner, GScanContext *context, const sized_string_t *padding, unsigned int level, int fd)
{
    size_t i;                               /* Boucle de parcours          */
    bool trailing;                          /* Virgule finale              */

    /* Introduction */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    write(fd, "[\n", 2);

    /* Sous-traitance aux règles */

    for (i = 0; i < scanner->rule_count; i++)
    {
        trailing = ((i + 1) < scanner->rule_count);

        g_scan_rule_output_to_json(scanner->rules[i], context, padding, level + 1, fd, trailing);

    }

    /* Conclusion */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    write(fd, "]\n", 2);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : scanner = gestionnaire de recherche à consulter.             *
*                context = contexte de l'analyse à mener.                     *
*                                                                             *
*  Description : Convertit un gestionnaire de recherches en JSON.             *
*                                                                             *
*  Retour      : Données textuelles au format JSON ou NULL en cas d'erreur.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_content_scanner_convert_to_json(const GContentScanner *scanner, GScanContext *context)
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

    ret = asprintf(&name, "rost-scanner2json-%llu", counter++);
    if (ret == -1) goto exit;

    fd = memfd_create(name, MFD_CLOEXEC);
    if (fd == -1)
    {
        LOG_ERROR_N("memfd_create");
        goto exit_with_name;
    }

    padding.data = "   ";
    padding.len = 3;

    g_content_scanner_output_to_json(scanner, context, &padding, 0, fd);

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
