
/* Chrysalide - Outil d'analyse de fichiers binaires
 * extstr.h - prototypes pour une extension des fonctions relatives aux chaînes
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


#ifndef _COMMON_EXTSTR_H
#define _COMMON_EXTSTR_H


#include <ctype.h>
#include <stdbool.h>
#include <sys/types.h>



/* Complète une chaîne de caractères avec une autre. */
char *stradd(char *, const char *);

/* Complète une chaîne de caractères avec une autre. */
char *strnadd(char *, const char *, size_t);

/* Complète une chaîne de caractères avec une chaîne à formater. */
char *straddfmt(char *, const char *, ...);

/* Fait précéder une chaîne de caractères par une autre. */
char *strprep(char *, const char *);

/* Compare deux chaînes de caractères en partant de la fin. */
int strrcmp(const char *, const char *);

/* Compare deux pointeurs vers des chaînes de caractères. */
int strptrcmp(const char * const *, const char * const *);

/* Remplace des éléments d'une chaîne par d'autres. */
char *strrpl(char *, const char *, const char *);

/* Bascule toute une chaîne de caractères en (min|maj)uscules. */
char *_strxxx(char *, int (* fn) (int));

#define strlower(str) _strxxx(str, tolower)
#define strupper(str) _strxxx(str, toupper)

/* Extrait un mot d'une chaîne selon des séparations longues. */
char *strtok_w(char **, const char *);

/* Extrait une liste de mots d'une chaîne. */
char **strtoka(const char *, const char *, size_t *);

/* S'assure qu'une chaîne de caractères tient sur une ligne. */
char *escape_crlf(char *);

/* Borne la taille d'une chaîne à une valeur donnée. */
char *ellipsis(char *, size_t);

/* Détermine si une chaîne débute par une autre. */
bool _startswith(const char *, const char *, const char **);

/* Détermine si une chaîne se termine par une autre. */
bool _endswith(const char *, const char *, const char **);

#define startswith(str, prefix) _startswith(str, prefix, NULL)
#define endswith(str, suffix) _endswith(str, suffix, NULL)

/* Recherche une séquence d'octets dans un ensemble de données. */
const void *memcasemem(const void *, size_t, const void *, size_t);

/* Compare sans casse deux série d'octets entre elles. */
int memcasecmp(const void *, const void *, size_t);



#endif  /* _COMMON_EXTSTR_H */
