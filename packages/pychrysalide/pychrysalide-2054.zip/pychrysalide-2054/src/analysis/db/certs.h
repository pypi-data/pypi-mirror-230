
/* Chrysalide - Outil d'analyse de fichiers binaires
 * certs.h - prototypes pour la gestion des certificats des échanges
 *
 * Copyright (C) 2017-2019 Cyrille Bagard
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


#ifndef _ANALYSIS_DB_CERTS_H
#define _ANALYSIS_DB_CERTS_H


#include <stdbool.h>



/* Informations pour les certificats X509 */
typedef struct _x509_entries
{
    char *country;                          /* Pays                        */
    char *state;                            /* Etat                        */
    char *locality;                         /* Localité                    */
    char *organisation;                     /* Organisation                */
    char *organisational_unit;              /* Département                 */
    char *common_name;                      /* Désignation commune         */

} x509_entries;


/* Indique si une définition existe dans l'identité. */
bool are_x509_entries_empty(const x509_entries *);

/* Traduit en chaîne de caractères une définition d'identité. */
char *translate_x509_entries(const x509_entries *);

/* Libère la mémoire occupée par une définition d'identité. */
void free_x509_entries(x509_entries *);

/* Crée un certificat de signature racine. */
bool build_keys_and_ca(const char *, const char *, unsigned long, const x509_entries *);

/* Crée un certificat pour application. */
bool build_keys_and_request(const char *, const char *, const x509_entries *);

/* Recharge l'identité inscrite dans une requête de signature. */
bool load_identity_from_request(const char *, x509_entries *);

/* Recharge l'identité inscrite dans un certificat signé. */
bool load_identity_from_cert(const char *, x509_entries *);

/* Signe un certificat pour application. */
bool sign_cert(const char *, const char *, const char *, const char *, unsigned long);



#endif  /* _ANALYSIS_DB_CERTS_H */
