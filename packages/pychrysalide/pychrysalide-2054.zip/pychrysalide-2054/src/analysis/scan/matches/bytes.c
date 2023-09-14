
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bytes.h - sauvegarde d'une correspondance identifiée de suite d'octets
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


#include "bytes.h"


#include <assert.h>
#include <ctype.h>
#include <stdio.h>


#include "bytes-int.h"
#include "../../../common/cpp.h"
#include "../../../core/logs.h"



/* --------------------- CORRESPONDANCE AVEC UNE SUITE D'OCTETS --------------------- */


/* Initialise la classe des correspondances de chaînes. */
static void g_scan_bytes_match_class_init(GScanBytesMatchClass *);

/* Initialise une instance de correspondance de chaîne trouvée. */
static void g_scan_bytes_match_init(GScanBytesMatch *);

/* Supprime toutes les références externes. */
static void g_scan_bytes_match_dispose(GScanBytesMatch *);

/* Procède à la libération totale de la mémoire. */
static void g_scan_bytes_match_finalize(GScanBytesMatch *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Affiche une correspondance au format texte. */
static void g_scan_bytes_match_output_to_text(const GScanBytesMatch *, int);

/* Affiche une correspondance au format JSON. */
static void g_scan_bytes_match_output_to_json(const GScanBytesMatch *, const sized_string_t *, unsigned int, int);



/* ---------------------------------------------------------------------------------- */
/*                       CORRESPONDANCE AVEC UNE SUITE D'OCTETS                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un correspondance de chaîne identifiée. */
G_DEFINE_TYPE(GScanBytesMatch, g_scan_bytes_match, G_TYPE_SCAN_MATCH);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des correspondances de chaînes.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_bytes_match_class_init(GScanBytesMatchClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GScanMatchClass *match;                 /* Version parente de la classe*/

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_scan_bytes_match_dispose;
    object->finalize = (GObjectFinalizeFunc)g_scan_bytes_match_finalize;

    match = G_SCAN_MATCH_CLASS(klass);

    match->to_text = (output_scan_match_to_text_fc)g_scan_bytes_match_output_to_text;
    match->to_json = (output_scan_match_to_json_fc)g_scan_bytes_match_output_to_json;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de correspondance de chaîne trouvée. *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_bytes_match_init(GScanBytesMatch *match)
{
    match->content = NULL;

    match->start = VMPA_NO_PHYSICAL;
    match->len = VMPA_NO_PHYSICAL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_bytes_match_dispose(GScanBytesMatch *match)
{
    g_clear_object(&match->content);

    G_OBJECT_CLASS(g_scan_bytes_match_parent_class)->dispose(G_OBJECT(match));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_bytes_match_finalize(GScanBytesMatch *match)
{
    G_OBJECT_CLASS(g_scan_bytes_match_parent_class)->finalize(G_OBJECT(match));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : source  = lien vers le motif recherché d'origine.            *
*                content = contenu binaire présentant un motif reconnu.       *
*                start   = position de départ d'un motif détecté.             *
*                len     = taille du motif repéré.                            *
*                                                                             *
*  Description : Prend note d'une correspondance trouvée avec un motif.       *
*                                                                             *
*  Retour      : Correspondance mise en place.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GScanMatch *g_scan_bytes_match_new(GSearchPattern *source, GBinContent *content, phys_t start, phys_t len)
{
    GScanMatch *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_SCAN_BYTES_MATCH, NULL);

    if (!g_scan_bytes_match_create(G_SCAN_BYTES_MATCH(result), source, content, start, len))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match   = instance à initialiser pleinement.                 *
*                source  = lien vers le motif recherché d'origine.            *
*                content = contenu binaire présentant un motif reconnu.       *
*                start   = position de départ d'un motif détecté.             *
*                len     = taille du motif repéré.                            *
*                                                                             *
*  Description : Met en place une correspondance trouvée avec un motif.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_scan_bytes_match_create(GScanBytesMatch *match, GSearchPattern *source, GBinContent *content, phys_t start, phys_t len)
{
    bool result;                            /* Bilan à retourner           */
    GScanMatch *base;                       /* Lien vers les infos de base */

    result = true;

    base = G_SCAN_MATCH(match);

    base->source = source;
    g_object_ref(G_OBJECT(source));

    match->content = content;
    g_object_ref(G_OBJECT(content));

    match->start = start;
    match->len = len;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match = informations de correspondance à consulter.          *
*                                                                             *
*  Description : Fournit une référence au contenu lié à la correspondance.    *
*                                                                             *
*  Retour      : Content binaire associé au context.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_scan_bytes_match_get_content(const GScanBytesMatch *match)
{
    GBinContent *result;                    /* Instance à retourner        */

    result = match->content;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match = informations de correspondance à consulter.          *
*                start = position de départ d'un motif détecté. [OUT]         *
*                end   = position d'arrivée d'un motif détecté. [OUT]         *
*                                                                             *
*  Description : Indique la localisation d'une correspondance établie.        *
*                                                                             *
*  Retour      : Taille mesurée de la correspondance.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

phys_t g_scan_bytes_match_get_location(const GScanBytesMatch *match, phys_t *start, phys_t *end)
{
    phys_t result;                          /* Taille à retourner          */

    result = match->len;

    *start = match->start;
    *end = match->start + result;

    return result;

}


/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : match = définition de correspondance à manipuler.            *
*                fd    = canal d'écriture.                                    *
*                                                                             *
*  Description : Affiche une correspondance au format texte.                  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_bytes_match_output_to_text(const GScanBytesMatch *match, int fd)
{
    char value[2 + ULLONG_MAXLEN];          /* Impression de la position   */
    int ret;                                /* Bilan d'une conversion      */
    GScanMatch *base;                       /* Lien vers les infos de base */
    const char *name;                       /* Désignation du motif ciblé  */
    vmpa2t pos;                             /* Tête de lecture             */
    const bin_t *data;                      /* Accès aux données brutes    */
    phys_t k;                               /* Boucle de parcours #2       */

    /* Position dans le binaire (hexadécimal) */

    ret = snprintf(value, ULLONG_MAXLEN, "0x%llx", (unsigned long long)match->start);

    if (ret > 0)
        write(fd, value, ret);

    else
    {
        log_simple_message(LMT_EXT_ERROR, "Error while converting offset to hex!");
        write(fd, "\"<error>\"", 9);
    }

    write(fd, ":", 1);

    /* Affichage de la désignation */

    write(fd, "$", 1);

    base = G_SCAN_MATCH(match);

    name = g_search_pattern_get_name(base->source);

    /**
     * Les fonctionnalités Yara d'origine autorisent les variables anonymes '$'.
     *
     * Cette absence de nom est supportée ici.
     */

    if (name != NULL)
        write(fd, name, strlen(name));

    write(fd, ": ", 2);

    /* Affichage du contenu */

    init_vmpa(&pos, match->start, VMPA_NO_VIRTUAL);

    data = g_binary_content_get_raw_access(match->content, &pos, match->len);

    for (k = 0; k < match->len; k++)
    {
        if (isprint(data[k]))
            write(fd, &data[k], 1);

        else
        {
            write(fd, "\\x", 2);

            ret = snprintf(value, ULLONG_MAXLEN, "%02hhx", data[k]);

            if (ret > 0)
            {
                assert(ret == 2);
                write(fd, value, ret);
            }

            else
            {
                log_simple_message(LMT_EXT_ERROR, "Error while converting data!");
                write(fd, "??", 2);
            }

        }

    }

    write(fd, "\n", 1);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : match   = définition de correspondance à manipuler.          *
*                padding = éventuel bourrage initial à placer ou NULL.        *
*                level   = profondeur actuelle.                               *
*                fd      = canal d'écriture.                                  *
*                                                                             *
*  Description : Affiche une correspondance au format JSON.                   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_scan_bytes_match_output_to_json(const GScanBytesMatch *match, const sized_string_t *padding, unsigned int level, int fd)
{
    unsigned int i;                         /* Boucle de parcours #1       */
    vmpa2t pos;                             /* Tête de lecture             */
    char value[4 + ULLONG_MAXLEN];          /* Impression de la position   */
    int ret;                                /* Bilan d'une conversion      */
    const bin_t *data;                      /* Accès aux données brutes    */
    phys_t k;                               /* Boucle de parcours #2       */

    /* Position dans le binaire (décimal) */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    write(fd, "\"offset\": ", 10);

    ret = snprintf(value, ULLONG_MAXLEN, "%llu", (unsigned long long)match->start);

    if (ret > 0)
        write(fd, value, ret);

    else
    {
        log_simple_message(LMT_EXT_ERROR, "Error while converting offset!");
        write(fd, "null", 4);
    }

    write(fd, ",\n", 2);

    /* Position dans le binaire (hexadécimal) */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    write(fd, "\"offset_hex\": ", 14);

    ret = snprintf(value, ULLONG_MAXLEN, "\"0x%llx\"", (unsigned long long)match->start);

    if (ret > 0)
        write(fd, value, ret);

    else
    {
        log_simple_message(LMT_EXT_ERROR, "Error while converting offset to hex!");
        write(fd, "null", 4);
    }

    write(fd, ",\n", 2);

    /* Affichage du contenu brut */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    write(fd, "\"content\": \"", 12);

    init_vmpa(&pos, match->start, VMPA_NO_VIRTUAL);

    data = g_binary_content_get_raw_access(match->content, &pos, match->len);
    assert(data != NULL);

    for (k = 0; k < match->len; k++)
    {
        if (data[k] == '\\')
            write(fd, "\\\\", 2);

        else if (isprint(data[k]))
            write(fd, &data[k], 1);

        else
        {
            write(fd, "\\u", 2);

            /**
             * Cf. https://datatracker.ietf.org/doc/html/rfc8259#section-7
             */
            ret = snprintf(value, ULLONG_MAXLEN, "%04hhx", data[k]);

            if (ret > 0)
            {
                assert(ret == 4);
                write(fd, value, ret);
            }

            else
            {
                log_simple_message(LMT_EXT_ERROR, "Error while converting data!");
                write(fd, "??", 2);
            }

        }

    }

    write(fd, "\",\n", 3);

    /* Affichage du contenu en version humainement lisible */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    write(fd, "\"content_str\": \"", 16);

    init_vmpa(&pos, match->start, VMPA_NO_VIRTUAL);

    data = g_binary_content_get_raw_access(match->content, &pos, match->len);
    assert(data != NULL);

    for (k = 0; k < match->len; k++)
    {
        if (data[k] == '\\')
            write(fd, "\\\\", 2);

        else if (isprint(data[k]))
            write(fd, &data[k], 1);

        else
        {
            write(fd, "\\\\x", 3);

            ret = snprintf(value, ULLONG_MAXLEN, "%02hhx", data[k]);

            if (ret > 0)
            {
                assert(ret == 2);
                write(fd, value, ret);
            }

            else
            {
                log_simple_message(LMT_EXT_ERROR, "Error while converting data!");
                write(fd, "??", 2);
            }

        }

    }

    write(fd, "\",\n", 3);

    /* Affichage du contenu brut */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    write(fd, "\"length\": ", 10);

    init_vmpa(&pos, match->start, VMPA_NO_VIRTUAL);

    ret = snprintf(value, ULLONG_MAXLEN, "%llu", (unsigned long long)match->len);

    if (ret > 0)
        write(fd, value, ret);

    else
    {
        log_simple_message(LMT_EXT_ERROR, "Error while converting data!");
        write(fd, "-1", 2);
    }

    write(fd, ",\n", 2);

    /* Affichage du contenu brut (hexadécimal) */

    for (i = 0; i < level; i++)
        write(fd, padding->data, padding->len);

    write(fd, "\"length_hex\": ", 14);

    init_vmpa(&pos, match->start, VMPA_NO_VIRTUAL);

    ret = snprintf(value, ULLONG_MAXLEN, "\"0x%llx\"", (unsigned long long)match->len);

    if (ret > 0)
        write(fd, value, ret);

    else
    {
        log_simple_message(LMT_EXT_ERROR, "Error while converting data!");
        write(fd, "\"0xffffffffffffffff\"", 20);
    }

    write(fd, "\n", 1);

}
