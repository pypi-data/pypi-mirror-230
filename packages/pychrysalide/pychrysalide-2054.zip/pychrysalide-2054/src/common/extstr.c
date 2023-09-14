
/* Chrysalide - Outil d'analyse de fichiers binaires
 * extstr.c - extension des fonctions relatives aux chaînes
 *
 * Copyright (C) 2009-2019 Cyrille Bagard
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


#include "extstr.h"


#include <ctype.h>
#include <malloc.h>
#include <regex.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>



/******************************************************************************
*                                                                             *
*  Paramètres  : str1 = chaîne de caractères à compléter.                     *
*                str2 = chaîne de caractères à ajouter.                       *
*                                                                             *
*  Description : Complète une chaîne de caractères avec une autre.            *
*                                                                             *
*  Retour      : Chaîne de caractères complétée, à libérer de la mémoire.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *stradd(char *str1, const char *str2)
{
    char *result;                           /* Chaîne à renvoyer           */

    if (str1 == NULL)
        result = strdup(str2);

    else
    {
        result = (char *)realloc(str1, (strlen(str1) + strlen(str2) + 1) * sizeof(char));
        strcat(result, str2);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str1 = chaîne de caractères à compléter.                     *
*                str2 = chaîne de caractères à ajouter.                       *
*                n    = taille de la seconde chaîne.                          *
*                                                                             *
*  Description : Complète une chaîne de caractères avec une autre.            *
*                                                                             *
*  Retour      : Chaîne de caractères complétée, à libérer de la mémoire.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *strnadd(char *str1, const char *str2, size_t n)
{
    char *result;                           /* Chaîne à renvoyer           */

    if (str1 == NULL)
        result = strndup(str2, n);

    else
    {
        result = (char *)realloc(str1, (strlen(str1) + n + 1) * sizeof(char));
        strncat(result, str2, n);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str1 = chaîne de caractères à compléter.                     *
*                fmt  = description de la forme de la chaîne complémentaire.  *
*                ...  = éléments associés au format à construire.             *
*                                                                             *
*  Description : Complète une chaîne de caractères avec une chaîne à formater.*
*                                                                             *
*  Retour      : Chaîne de caractères complétée, à libérer de la mémoire.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *straddfmt(char *str1, const char *fmt, ...)
{
    char *result;                           /* Chaîne à renvoyer           */
    va_list ap;                             /* Liste des arguments         */
    char *tmp;                              /* Conservation temporaire     */
    int ret;                                /* Bilan intermédiaire         */

    va_start(ap, fmt);

    ret = vasprintf(&tmp, fmt, ap);

    if (ret != -1)
    {
        result = stradd(str1, tmp);
        free(tmp);
    }

    else
        result = str1;

    va_end(ap);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str1 = chaîne de caractères à compléter.                     *
*                str2 = chaîne de caractères à ajouter.                       *
*                                                                             *
*  Description : Fait précéder une chaîne de caractères par une autre.        *
*                                                                             *
*  Retour      : Chaîne de caractères complétée, à libérer de la mémoire.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *strprep(char *str1, const char *str2)
{
    char *result;                           /* Chaîne à renvoyer           */
    size_t len2;                            /* Taille de la seconde chaîne */

    result = (char *)realloc(str1, (strlen(str1) + strlen(str2) + 1) * sizeof(char));

    len2 = strlen(str2);

    memmove(&result[len2], result, strlen(result) + 1);
    memcpy(result, str2, len2);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str1 = chaîne de caractères à analyser.                      *
*                str2 = chaîne de caractères à retrouver.                     *
*                                                                             *
*  Description : Compare deux chaînes de caractères en partant de la fin.     *
*                                                                             *
*  Retour      : -1, 0, ou 1 selon la comparaison.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int strrcmp(const char *str1, const char *str2)
{
    int result;                             /* Bilan à renvoyer            */
    size_t len1;                            /* Longueur de la chaîne donnée*/
    size_t len2;                            /* Longueur de la chaîne visée */

    len1 = strlen(str1);
    len2 = strlen(str2);

    if (len1 <= len2)
        result = strcmp(str1, str2);

    else result = strcmp(&str1[len1 - len2], str2);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str1 = preière chaîne de caractères à analyser.              *
*                str2 = seconde chaîne de caractères à analyser.              *
*                                                                             *
*  Description : Compare deux pointeurs vers des chaînes de caractères.       *
*                                                                             *
*  Retour      : -1, 0, ou 1 selon la comparaison.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int strptrcmp(const char * const *str1, const char * const *str2)
{
    int result;                             /* Bilan à renvoyer            */

    result = strcmp(*str1, *str2);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : haystack = botte de foin à fouiller.                         *
*                needle1  = aiguille à trouver et remplacer.                  *
*                needle2  = aiguille de remplacement.                         *
*                                                                             *
*  Description : Remplace des éléments d'une chaîne par d'autres.             *
*                                                                             *
*  Retour      : Adresse de la chaîne de caractères modifiée.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *strrpl(char *haystack, const char *needle1, const char *needle2)
{
    size_t inlen;                           /* Taille en entrée            */
    size_t len1;                            /* Taille de l'aiguille n°1    */
    size_t len2;                            /* Taille de l'aiguille n°2    */
    size_t index;                           /* Conversion en indice        */
    char *found;                            /* Position d'une trouvaille   */

    inlen = strlen(haystack) + 1;
    len1 = strlen(needle1);
    len2 = strlen(needle2);

    index = 0;

    for (found = strstr(haystack + index, needle1);
         found != NULL;
         found = strstr(haystack + index, needle1))
    {
        index = found - haystack;

        if (len2 > len1)
        {
            inlen += (len2 - len1);

            haystack = (char *)realloc(haystack, inlen * sizeof(char *));
            found = haystack + index;

            memmove(found + len2, found + len1, inlen - len2 - index);

        }

        else if (len2 < len1)
        {
            memmove(found + len2, found + len1, inlen - index - len1);

            inlen -= (len1 - len2);

            haystack = (char *)realloc(haystack, inlen * sizeof(char *));
            found = haystack + index;

        }

        memcpy(found, needle2, len2);

        index += len2;

    }

    return haystack;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str = chaîne de caractères à manipuler. [OUT]                *
*                                                                             *
*  Description : Bascule toute une chaîne de caractères en (min|maj)uscules.  *
*                                                                             *
*  Retour      : Pointeur sur la chaîne fournie.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *_strxxx(char *str, int (* fn) (int))
{
    size_t max;                             /* Empleur du parcours         */
    size_t i;                               /* Boucle de parcours          */

    max = strlen(str);

    for (i = 0; i < max; i++)
        str[i] = fn(str[i]);

    return str;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str   = chaîne de caractères à traiter. [OUT]                *
*                delim = mot de séparation entre les mots identifiés.         *
*                                                                             *
*  Description : Extrait un mot d'une chaîne selon des séparations longues.   *
*                                                                             *
*  Retour      : Chaîne de caractères cernée ou NULL.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *strtok_w(char **str, const char *delim)
{
    char *result;
    char *haystack;
    char *next;
    const char *diter;

    haystack = *str;

    if (haystack == NULL)
        result = NULL;

    else
    {
        result = haystack;

        next = strstr(haystack, delim);

        if (next != NULL)
        {
            for (diter = delim; *diter; diter++, next++)
                *next = '\0';
        }

        *str = next;

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str   = chaîne de caractères à traiter.                      *
*                delim = séparateur entre les mots.                           *
*                count = nombre de mots trouvés. [OUT]                        *
*                                                                             *
*  Description : Extrait une liste de mots d'une chaîne.                      *
*                                                                             *
*  Retour      : Tableau construit à libérer de la mémoire.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char **strtoka(const char *str, const char *delim, size_t *count)
{
    char **result;                          /* Tableau à retourner         */
    char *tmp;                              /* Sauvegarde modifiable       */
    char *word;                             /* Nouveau mot détecté         */

    result = NULL;
    *count = 0;

    tmp = strdup(str);

    for (word = strtok(tmp, delim); word != NULL; word = strtok(NULL, delim))
    {
        result = (char **)realloc(result, ++(*count) * sizeof(char *));
        result[*count - 1] = strdup(word);
    }

    free(tmp);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : input = chaîne de caractères à traiter.                      *
*                                                                             *
*  Description : S'assure qu'une chaîne de caractères tient sur une ligne.    *
*                                                                             *
*  Retour      : Adresse de la chaîne de caractères modifiée.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *escape_crlf(char *input)
{
    size_t inlen;
    regex_t preg;
    size_t curpos;
    regmatch_t pmatch[2];

    inlen = strlen(input);

    /* On considère que la compilation est toujours bonne... */
    regcomp(&preg, "(\t|\n|\r)", REG_EXTENDED | REG_ICASE);

    for (curpos = 0; regexec(&preg, &input[curpos], 2, pmatch, 0) != REG_NOMATCH; )
    {
        inlen += 1 + 1;
        input = (char *)realloc(input, inlen * sizeof(char *));

        memmove(&input[curpos + pmatch[1].rm_eo + 1], &input[curpos + pmatch[1].rm_eo], inlen - 1 - curpos - pmatch[1].rm_eo);

        switch (input[curpos + pmatch[1].rm_so])
        {
            case '\t':
                memcpy(&input[curpos + pmatch[1].rm_so], "\\t", 2);
                break;
            case '\n':
                memcpy(&input[curpos + pmatch[1].rm_so], "\\n", 2);
                break;
            case '\r':
                memcpy(&input[curpos + pmatch[1].rm_so], "\\r", 2);
                break;
        }

        curpos += pmatch[1].rm_eo + 1;

    }

    regfree(&preg);

    return input;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : input = chaîne de caractères à traiter.                      *
*                max   = taille maximale de chaîne acceptable.                *
*                                                                             *
*  Description : Borne la taille d'une chaîne à une valeur donnée.            *
*                                                                             *
*  Retour      : Adresse de la chaîne de caractères ou input si pas besoin.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *ellipsis(char *input, size_t max)
{
    char *result;                           /* Chaîne à retourner          */

    if (strlen(input) > max)
    {
        result = strndup(input, max);
        result = stradd(result, "...");

        free(input);

    }
    else result = input;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str    = chaîne à analyser.                                  *
*                prefix = chaîne à retrouver en extrémité éventuellement.     *
*                start  = premier caractère hors préfixe. [OUT]               *
*                                                                             *
*  Description : Détermine si une chaîne débute par une autre.                *
*                                                                             *
*  Retour      : true si le préfixe a été identifié, ou false sinon.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _startswith(const char *str, const char *prefix, const char **start)
{
    bool result;                            /* Bilan à faire remonter      */
    size_t len;                             /* Taille de la chaîne soumise */
    size_t preflen;                         /* Taille du préfixe           */

    result = false;

    len = strlen(str);
    preflen = strlen(prefix);

    if (len > preflen)
    {
        result = (strncmp(str, prefix, preflen) == 0);

        if (result && start != NULL)
            *start = &str[preflen];

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : str    = chaîne à analyser.                                  *
*                suffix = chaîne à retrouver en extrémité éventuellement.     *
*                end    = premier caractère du préfixe. [OUT]                 *
*                                                                             *
*  Description : Détermine si une chaîne se termine par une autre.            *
*                                                                             *
*  Retour      : true si le suffixe a été identifié, ou false sinon.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _endswith(const char *str, const char *suffix, const char **end)
{
    bool result;                            /* Bilan à faire remonter      */
    size_t len;                             /* Taille de la chaîne soumise */
    size_t suflen;                          /* Taille du suffixe           */
    const char *tmp;                        /* Stockage temporaire         */

    result = false;

    len = strlen(str);
    suflen = strlen(suffix);

    if (len > suflen)
    {
        if (end == NULL) end = &tmp;

        *end = &str[len - suflen];

        result = (strncmp(*end, suffix, suflen) == 0);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : haystack    = botte de foin composant l'espace de recherche. *
*                haystacklen = taille de cet espace.                          *
*                needle      = aiguille visée, cible des recherches.          *
*                needlelen   = taille de l'aiguille à rechercher.             *
*                                                                             *
*  Description : Recherche une séquence d'octets dans un ensemble de données. *
*                                                                             *
*  Retour      : Adresse de l'éventuelle trouvaille ou NULL.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const void *memcasemem(const void *haystack, size_t haystacklen, const void *needle, size_t needlelen)
{
    const void *result;                     /* Trouvaille à renvoyer       */
    const char *_haystack;                  /* Autre version de la botte   */
    const char *_needle;                    /* Autre version de l'aiguille */
    size_t i;                               /* Boucle de parcours #1       */
    size_t k;                               /* Boucle de parcours #2       */
    int c1;                                 /* Caractère de la chaîne #1   */
    int c2;                                 /* Caractère de la chaîne #2   */

    result = NULL;

    if (needlelen > haystacklen)
        goto done;

    _haystack = (const char *)haystack;
    _needle = (const char *)needle;

    for (i = 0; i <= (haystacklen - needlelen); i++, _haystack++)
    {
        for (k = 0; k < needlelen; k++)
        {
            c1 = toupper(_haystack[k]);
            c2 = toupper(_needle[k]);

            if (c1 != c2)
                break;

        }

        if (k == needlelen)
        {
            result = _haystack;
            break;
        }

    }

 done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : s1 = première séquence d'octets à consulter.                 *
*                s2 = second séquence d'octets à consulter.                   *
*                n  = quantité d'octets à comparer.                           *
*                                                                             *
*  Description : Compare sans casse deux série d'octets entre elles.          *
*                                                                             *
*  Retour      : Status de la comparaison des séries d'octets.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int memcasecmp(const void *s1, const void *s2, size_t n)
{
    int result;                             /* Statut à retourner          */
    size_t i;                               /* Boucle de parcours          */
    const char *_s1;                        /* Séquence avec taille #1     */
    const char *_s2;                        /* Séquence avec taille #2     */
    int c1;                                 /* Caractère de la chaîne #1   */
    int c2;                                 /* Caractère de la chaîne #2   */

    result = 0;

    _s1 = (const char *)s1;
    _s2 = (const char *)s2;

    for (i = 0; i < n; i++)
    {
        c1 = toupper(_s1[i]);
        c2 = toupper(_s2[i]);

        result = c1 - c2;
        if (result != 0) break;

    }

    return result;

}
