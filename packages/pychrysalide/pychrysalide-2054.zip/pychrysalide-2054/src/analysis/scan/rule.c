
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rule.c - parcours de contenus à la recherche de motifs
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


#include "rule.h"


#include <assert.h>
#include <regex.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>


#include "rule-int.h"
#include "matches/bytes.h"
#include "patterns/token.h"
#include "../../common/extstr.h"
#include "../../core/logs.h"



/* Initialise la classe des règles de détection statique. */
static void g_scan_rule_class_init(GScanRuleClass *);

/* Initialise une instance de règle de détection statique. */
static void g_scan_rule_init(GScanRule *);

/* Supprime toutes les références externes. */
static void g_scan_rule_dispose(GScanRule *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_rule_finalize(GScanRule *);



/* Indique le type défini pour une règle de détection par motifs. */
G_DEFINE_TYPE(GScanRule, g_scan_rule, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des règles de détection statique.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_rule_class_init(GScanRuleClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_rule_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_rule_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rule = instance à initialiser.                               *
*                                                                             *
*  Description : Initialise une instance de règle de détection statique.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_rule_init(GScanRule *rule)
{
    rule->name = NULL;
    rule->name_hash = 0;

    rule->bytes_locals = NULL;
    rule->bytes_allocated = 0;
    rule->bytes_used = 0;

    rule->condition = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rule = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_rule_dispose(GScanRule *rule)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < rule->bytes_used; i++)
        g_clear_object(&rule->bytes_locals[i]);

    g_clear_object(&rule->condition);

    G_OBJECT_CLASS(g_scan_rule_parent_class)->dispose(G_OBJECT(rule));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rule = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_rule_finalize(GScanRule *rule)
{
    if (rule->name != NULL)
        free(rule->name);

    G_OBJECT_CLASS(g_scan_rule_parent_class)->finalize(G_OBJECT(rule));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : name = désignation à associer à la future règle.             *
*                                                                             *
*  Description : Crée une règle de détection statique à l'aide de motifs.     *
*                                                                             *
*  Retour      : Règle de détection mise en place.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanRule *g_scan_rule_new(const char *name)
{
    GScanRule *result;                /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_RULE, NULL);

    result->name = strdup(name);
    result->name_hash = fnv_64a_hash(name);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rule = règle de détection à compléter.                       *
*                hash = empreinte précalculée associée au nom. [OUT]          *
*                                                                             *
*  Description : Indique le nom associé à une règle de détection.             *
*                                                                             *
*  Retour      : Désignation humaine associée à la règle.                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_scan_rule_get_name(const GScanRule *rule, fnv64_t *hash)
{
    const char *result;                     /* Désignation à retourner     */

    result = rule->name;

    *hash = rule->name_hash;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rule    = règle de détection à compléter.                    *
*                pattern = nouveau motif de détection.                        *
*                                                                             *
*  Description : Intègre une nouvelle variable locale à une règle.            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_rule_add_local_variable(GScanRule *rule, GSearchPattern *pattern)
{
    if (G_IS_STRING_TOKEN(pattern))
    {
        if (rule->bytes_used == rule->bytes_allocated)
        {
            rule->bytes_allocated += PATTERN_ALLOC_SIZE;
            rule->bytes_locals = realloc(rule->bytes_locals, rule->bytes_allocated * sizeof(GSearchPattern *));
        }

        rule->bytes_locals[rule->bytes_used++] = pattern;
        g_object_ref(G_OBJECT(pattern));

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rule   = règle de détection à consulter.                     *
*                target = nom d'une variable locale à retrouver.              *
*                                                                             *
*  Description : Fournit une variable locale à une règle selon un nom.        *
*                                                                             *
*  Retour      : Motif de détection retrouvé ou NULL en cas d'échec.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GSearchPattern *g_scan_rule_get_local_variable(GScanRule *rule, const char *target)
{
    GSearchPattern *result;                 /* Variable à retourner        */
    size_t i;                               /* Boucle de parcours          */
    const char *name;                       /* Désignation d'un motif      */

    result = NULL;

    for (i = 0; i < rule->bytes_used; i++)
    {
        name = g_search_pattern_get_name(rule->bytes_locals[i]);

        if (strcmp(name, target) == 0)
        {
            result = rule->bytes_locals[i];
            break;
        }

    }

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rule   = règle de détection à consulter.                     *
*                target = nom d'une variable locale à retrouver.              *
*                count  = quantité de motifs renvoyés. [OUT]                  *
*                                                                             *
*  Description : Fournit une liste de variables locales à partir d'un nom.    *
*                                                                             *
*  Retour      : Motifs de détection retrouvés ou NULL en cas d'échec.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GSearchPattern **g_scan_rule_get_local_variables(GScanRule *rule, const char *target, size_t *count)
{
    GSearchPattern **result;                /* Variables à retourner       */
    size_t i;                               /* Boucle de parcours          */
    char *regex;                            /* Définition complète         */
    regex_t preg;                           /* Expression compilée         */
    int ret;                                /* Bilan d'un appel            */
    const char *name;                       /* Désignation d'un motif      */

    result = NULL;

    *count = 0;

    /* Premier cas de figure : la liste complète est attendue */

    if (target == NULL)
    {
        *count = rule->bytes_used;
        result = malloc(*count * sizeof(GSearchPattern *));

        for (i = 0; i < rule->bytes_used; i++)
        {
            result[i] = rule->bytes_locals[i];
            g_object_ref(G_OBJECT(result[i]));
        }

    }

    /* Second cas de figure : une expression régulière est vraisemblablement de mise */

    else
    {
        regex = strdup(target);

        regex = strrpl(regex, "*", ".*");
        regex = strprep(regex, "^");
        regex = stradd(regex, "$");

        ret = regcomp(&preg, regex, REG_NOSUB);

        if (ret != 0)
        {
            LOG_ERROR_REGCOMP(&preg, ret);
            goto done;
        }

        result = malloc(rule->bytes_used * sizeof(GSearchPattern *));

        for (i = 0; i < rule->bytes_used; i++)
        {
            name = g_search_pattern_get_name(rule->bytes_locals[i]);

            ret = regexec(&preg, name, 0, NULL, 0);

            if (ret != REG_NOMATCH)
            {
                result[*count] = rule->bytes_locals[i];
                g_object_ref(G_OBJECT(result[*count]));

                (*count)++;

            }

        }

        if (*count == 0)
        {
            free(result);
            result = NULL;
        }

        regfree(&preg);

 done:

        free(regex);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rule = règle de détection à compléter.                       *
*                expr = expression de condition à satisfaire.                 *
*                                                                             *
*  Description : Définit l'expression d'une correspondance recherchée.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_rule_set_match_condition(GScanRule *rule, GScanExpression *expr)
{
    rule->condition = expr;

    g_object_ref(G_OBJECT(expr));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rule    = règle de détection à considérer.                   *
*                backend = moteur d'analyse pour données brutes.              *
*                context = contexte de l'analyse à mener.                     *
*                                                                             *
*  Description : Prépare le suivi de recherche de motifs pour une règle.      *
*                                                                             *
*  Retour      : Bilan de l'opération à renvoyer.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_rule_setup_backend(GScanRule *rule, GEngineBackend *backend, GScanContext *context)
{
    bool result;                            /* Statut à retourner          */
    size_t maxsize;                         /* Taille maximale des atomes  */
    GSearchPattern *pattern;                /* Motif à intégrer            */
    GScanOptions *options;                  /* Options d'analyse           */
    size_t i;                               /* Boucle de parcours          */

    /* Suivi des conditions de correspondance */

    result = g_scan_context_set_rule_condition(context, rule->name, rule->condition);
    if (!result) goto exit;

    /* Programmation des motifs recherchés */

    maxsize = g_engine_backend_get_atom_max_size(backend);

    for (i = 0; i < rule->bytes_used && result; i++)
    {
        pattern = rule->bytes_locals[i];
        result = g_string_token_enroll(G_STRING_TOKEN(pattern), context, backend, maxsize);
    }

    g_engine_backend_warm_up(backend);

    /* Affichage éventuel de statistiques */

    options = g_scan_context_get_options(context);

    if (g_scan_options_get_print_stats(options))
        g_engine_backend_output_stats(backend);


    g_object_unref(G_OBJECT(options));

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rule    = règle de détection à considérer.                   *
*                backend = moteur d'analyse pour données brutes.              *
*                context = contexte de l'analyse à mener.                     *
*                                                                             *
*  Description : Lance une analyse d'un contenu binaire selon une règle.      *
*                                                                             *
*  Retour      : Contexte de suivi pour l'analyse menée.                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_rule_check(GScanRule *rule, GEngineBackend *backend, GScanContext *context)
{
    GBinContent *content;                   /* Contenu à manipuler         */
    vmpa2t start;                           /* Point de début du contenu   */
    vmpa2t end;                             /* Point de fin du contenu     */
    pending_matches_t matches;              /* Suivi de correspondances    */
    size_t i;                               /* Boucle de parcours #1       */
    GSearchPattern *pattern;                /* Motif à intégrer            */
    size_t k;                               /* Boucle de parcours #2       */
    match_area_t *area;                     /* Zone à initialiser          */
    GScanMatch *match;                      /* Correspondance à mémoriser  */

    content = g_scan_context_get_content(context);

    g_binary_content_compute_start_pos(content, &start);
    g_binary_content_compute_end_pos(content, &end);

    /* Consolidation des résultats */

    for (i = 0; i < rule->bytes_used; i++)
    {
        init_pending_matches(&matches, &start.physical, &end.physical);

        pattern = rule->bytes_locals[i];

        g_string_token_check(G_STRING_TOKEN(pattern), context, content, &matches);

        for (k = 0; k < matches.used; k++)
        {
            area = &matches.areas[k];

            match = g_scan_bytes_match_new(G_SEARCH_PATTERN(pattern), content,
                                           area->start, area->end - area->start);

            g_scan_context_register_full_match(context, match);
            g_object_unref(G_OBJECT(match));

        }

        exit_pending_matches(&matches);

    }

    /* Sortie propre */

    g_object_unref(G_OBJECT(content));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rule    = règle de détection à considérer.                   *
*                context = contexte de l'analyse à mener.                     *
*                full    = force un affichage complet des résultats.          *
*                fd      = canal d'écriture.                                  *
*                                                                             *
*  Description : Affiche une règle au format texte.                           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_rule_output_to_text(const GScanRule *rule, GScanContext *context, bool full, int fd)
{
    size_t i;                               /* Boucle de parcours          */

    if (full)
        for (i = 0; i < rule->bytes_used; i++)
            g_search_pattern_output_to_text(rule->bytes_locals[i], context, fd);

    if (g_scan_context_has_match_for_rule(context, rule->name))
    {
        write(fd, "Rule '", 6);
        write(fd, rule->name, strlen(rule->name));
        write(fd, "' has matched!\n", 15);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : rule    = règle de détection à considérer.                   *
*                context = contexte de l'analyse à mener.                     *
*                                                                             *
*  Description : Convertit une règle en texte.                                *
*                                                                             *
*  Retour      : Données textuelles ou NULL en cas d'erreur.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_scan_rule_convert_as_text(const GScanRule *rule, GScanContext *context)
{
    char *result;                           /* Données à retourner         */
    char *name;                             /* Nom "unique" pour le canal  */
    int ret;                                /* Bilan de création de nom    */
    int fd;                                 /* Canal d'écriture            */
    struct stat info;                       /* Infos. incluant une taille  */
    ssize_t got;                            /* Données effectivement relues*/

    static unsigned long long counter = 0;

    result = NULL;

    ret = asprintf(&name, "rost-rule2text-%llu", counter++);
    if (ret == -1) goto exit;

    fd = memfd_create(name, MFD_CLOEXEC);
    if (fd == -1)
    {
        LOG_ERROR_N("memfd_create");
        goto exit_with_name;
    }

    g_scan_rule_output_to_text(rule, context, true, fd);

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
*  Paramètres  : rule     = règle de détection à considérer.                  *
*                context  = contexte de l'analyse à mener.                    *
*                padding  = éventuel bourrage initial à placer ou NULL.       *
*                level    = profondeur actuelle.                              *
*                fd       = canal d'écriture.                                 *
*                trailing = impose une virgule finale ?                       *
*                                                                             *
*  Description : Affiche une règle au format JSON.                            *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_scan_rule_output_to_json(const GScanRule *rule, GScanContext *context, const sized_string_t *padding, unsigned int level, int fd, bool trailing)
{
    size_t i;                               /* Boucle de parcours          */
    bool sub_trailing;                      /* Virgule finale              */

    /* Introduction */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    write(fd, "{\n", 2);

    /* Désignation de la règle */

    for (i = 0; i < (level + 1); i++)
        write(fd, padding->data, padding->len);

    write(fd, "\"name\": \"", 9);

    write(fd, rule->name, strlen(rule->name));

    write(fd, "\",\n", 3);

    /* Affichage des correspondances d'octets */

    for (i = 0; i < (level + 1); i++)
        write(fd, padding->data, padding->len);

    write(fd, "\"bytes_patterns\": [\n", 20);

    for (i = 0; i < rule->bytes_used; i++)
    {
        sub_trailing = ((i + 1) < rule->bytes_used);

        g_search_pattern_output_to_json(rule->bytes_locals[i], context, padding, level + 2, fd, sub_trailing);

    }

    for (i = 0; i < (level + 1); i++)
        write(fd, padding->data, padding->len);

    write(fd, "],\n", 3);

    /* Bilan du filtrage */

    for (i = 0; i < (level + 1); i++)
        write(fd, padding->data, padding->len);

    write(fd, "\"matched\": ", 11);

    if (g_scan_context_has_match_for_rule(context, rule->name))
        write(fd, "true", 4);
    else
        write(fd, "false", 5);

    write(fd, "\n", 1);

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
*  Paramètres  : rule    = règle de détection à considérer.                   *
*                context = contexte de l'analyse à mener.                     *
*                                                                             *
*  Description : Convertit une règle en JSON.                                 *
*                                                                             *
*  Retour      : Données textuelles au format JSON ou NULL en cas d'erreur.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *g_scan_rule_convert_as_json(const GScanRule *rule, GScanContext *context)
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

    ret = asprintf(&name, "rost-rule2json-%llu", counter++);
    if (ret == -1) goto exit;

    fd = memfd_create(name, MFD_CLOEXEC);
    if (fd == -1)
    {
        LOG_ERROR_N("memfd_create");
        goto exit_with_name;
    }

    padding.data = "   ";
    padding.len = 3;

    g_scan_rule_output_to_json(rule, context, &padding, 0, fd, false);

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
