
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


#include "certs.h"


#include <assert.h>
#include <glib.h>
#include <malloc.h>
#include <stdio.h>
#include <openssl/err.h>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/rsa.h>
#include <openssl/x509.h>
#include <openssl/x509v3.h>


#include <i18n.h>


#include "../../common/extstr.h"
#include "../../core/logs.h"



/* Ajoute une extension à un certificat. */
static bool add_extension_to_cert(X509 *, X509 *, /*const */char *, /*const */char *);

/* Ajoute une extension à une requête de signature. */
static bool add_extension_to_req(STACK_OF(X509_EXTENSION) *, int, /*const */char *);

/* Crée une paire de clefs RSA. */
static RSA *generate_rsa_key(unsigned int, unsigned long);

/* Recharge l'identité inscrite dans un élément X509. */
static bool load_identity_from_x509(/*const */X509_NAME *, x509_entries *);



/******************************************************************************
*                                                                             *
*  Paramètres  : entries = éléments d'identité à consulter.                   *
*                                                                             *
*  Description : Indique si une définition existe dans l'identité.            *
*                                                                             *
*  Retour      : Etat de la définition des entrées.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool are_x509_entries_empty(const x509_entries *entries)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    if (entries->country != NULL)
        result = false;

    if (!result && entries->state != NULL)
        result = false;

    if (!result && entries->locality != NULL)
        result = false;

    if (!result && entries->organisation != NULL)
        result = false;

    if (!result && entries->organisational_unit != NULL)
        result = false;

    if (!result && entries->common_name != NULL)
        result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : entries = éléments d'identité à convertir.                   *
*                                                                             *
*  Description : Traduit en chaîne de caractères une définition d'identité.   *
*                                                                             *
*  Retour      : Chaîne de caractères ou NULL.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *translate_x509_entries(const x509_entries *entries)
{
    char *result;                           /* Description à retourner     */

    result = NULL;

    if (entries->country != NULL)
    {
        result = stradd(result, "C=");
        result = stradd(result, entries->country);
    }

    if (entries->state != NULL)
    {
        if (result != NULL) result = stradd(result, "/");
        result = stradd(result, "ST=");
        result = stradd(result, entries->state);
    }

    if (entries->locality != NULL)
    {
        if (result != NULL) result = stradd(result, "/");
        result = stradd(result, "L=");
        result = stradd(result, entries->locality);
    }

    if (entries->organisation != NULL)
    {
        if (result != NULL) result = stradd(result, "/");
        result = stradd(result, "O=");
        result = stradd(result, entries->organisation);
    }

    if (entries->organisational_unit != NULL)
    {
        if (result != NULL) result = stradd(result, "/");
        result = stradd(result, "OU=");
        result = stradd(result, entries->organisational_unit);
    }

    if (entries->common_name != NULL)
    {
        if (result != NULL) result = stradd(result, "/");
        result = stradd(result, "CN=");
        result = stradd(result, entries->common_name);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : entries = éléments d'identité à supprimer de la mémoire.     *
*                                                                             *
*  Description : Libère la mémoire occupée par une définition d'identité.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void free_x509_entries(x509_entries *entries)
{
    if (entries->country != NULL)
        free(entries->country);

    if (entries->state != NULL)
        free(entries->state);

    if (entries->locality != NULL)
        free(entries->locality);

    if (entries->organisation != NULL)
        free(entries->organisation);

    if (entries->organisational_unit != NULL)
        free(entries->organisational_unit);

    if (entries->common_name != NULL)
        free(entries->common_name);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : issuer = certificat de l'autorité émettrice.                 *
*                subj   = certificat à la reception.                          *
*                name   = nom de l'extension.                                 *
*                value  = valeur portée par l'extension.                      *
*                                                                             *
*  Description : Ajoute une extension à un certificat.                        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool add_extension_to_cert(X509 *issuer, X509 *subj, /*const */char *name, /*const */char *value)
{
    bool result;                            /* Bilan à retourner           */
    X509V3_CTX ctx;                         /* Contexte à conserver        */
    X509_EXTENSION *ext;                    /* Définition d'une extension  */
    int ret;                                /* Bilan d'un ajout            */

    result = false;

    X509V3_set_ctx_nodb(&ctx);
    X509V3_set_ctx(&ctx, issuer, subj, NULL, NULL, 0);

    ext = X509V3_EXT_conf(NULL, &ctx, name, value);

    if (ext != NULL)
    {
        ret = X509_add_ext(subj, ext, -1);

        result = (ret != 0);

        X509_EXTENSION_free(ext);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : bits = taille de la clef en nombre de bits.                  *
*                e    = valeur de l'exposant destiné à la clef.               *
*                                                                             *
*  Description : Crée une paire de clefs RSA.                                 *
*                                                                             *
*  Retour      : Clef RSA mise en place.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static RSA *generate_rsa_key(unsigned int bits, unsigned long e)
{
    RSA *result;                            /* Clef à retourner            */
    BIGNUM *bne;                            /* Autre version de l'exposant */
    int ret;                                /* Bilan d'un appel            */

    result = NULL;

    bne = BN_new();
    if (bne == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Unable to create a BIGNUM structure (error=%lu)"), ERR_get_error());
        goto grk_no_bne;
    }

    ret = BN_set_word(bne, e);
    if (ret != 1) goto grk_bne_failed;

    result = RSA_new();
    if (bne == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Unable to create a RSA key (error=%lu)"), ERR_get_error());
        goto grk_no_rsa;
    }

    ret = RSA_generate_key_ex(result, bits, bne, NULL);
    if (ret != 1)
    {
        log_variadic_message(LMT_ERROR, _("Unable to generate RSA key (error=%lu)"), ERR_get_error());

        RSA_free(result);
        result = NULL;

        goto grk_done;
    }

 grk_done:

 grk_no_rsa:

 grk_bne_failed:

    BN_free(bne);

 grk_no_bne:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dir     = répertoire d'enregistrement de la création.        *
*                label   = étiquette à coller au certificat produit.          *
*                valid   = durée de validité en secondes.                     *
*                entries = éléments de l'identité à constituer.               *
*                                                                             *
*  Description : Crée un certificat de signature racine.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool build_keys_and_ca(const char *dir, const char *label, unsigned long valid, const x509_entries *entries)
{
    bool result;                            /* Bilan à retourner           */
    RSA *rsa;                               /* Clef RSA pour le certificat */
    EVP_PKEY *pk;                           /* Enveloppe pour clef publique*/
    int ret;                                /* Bilan d'un appel            */
    X509 *x509;                             /* Certificat X509 à définir   */
    X509_NAME *subject;                     /* SUjet du certificat         */
    char *filename;                         /* Chemin d'accès à un fichier */
    FILE *stream;                           /* Flux ouvert en écriture     */

    result = false;

    rsa = generate_rsa_key(4096, 17);
    if (rsa == NULL) goto rsa_failed;

    pk = EVP_PKEY_new();
    if (pk == NULL)
    {
        RSA_free(rsa);
        goto pk_failed;
    }

    ret = EVP_PKEY_assign_RSA(pk, rsa);
    if (ret != 1)
    {
        RSA_free(rsa);
        goto asign_failed;
    }

    x509 = X509_new();
    if (x509 == NULL) goto x509_failed;

    ret = X509_set_pubkey(x509, pk);
    if (ret != 1) goto ca_asign_failed;

    ret = X509_set_version(x509, 2);
    if (ret != 1) goto ca_failed;

    ret = ASN1_INTEGER_set(X509_get_serialNumber(x509), 1);
    if (ret != 1) goto ca_failed;

    X509_gmtime_adj(X509_get_notBefore(x509), 0);
    X509_gmtime_adj(X509_get_notAfter(x509), valid);

    /* Etablissement d'une identité */

    subject = X509_get_subject_name(x509);

#define SET_NAME_ENTRY(key, value)                                                          \
    do                                                                                      \
    {                                                                                       \
        if (entries->value != NULL)                                                         \
        {                                                                                   \
            ret = X509_NAME_add_entry_by_txt(subject, key, MBSTRING_UTF8,                   \
                                             (unsigned char *)entries->value, -1, -1, 0);   \
            if (ret != 1) goto ca_failed;                                                   \
        }                                                                                   \
    }                                                                                       \
    while (0)

    SET_NAME_ENTRY("C", country);

    SET_NAME_ENTRY("ST", state);

    SET_NAME_ENTRY("L", locality);

    SET_NAME_ENTRY("O", organisation);

    SET_NAME_ENTRY("OU", organisational_unit);

    SET_NAME_ENTRY("CN", common_name);

#undef SET_NAME_ENTRY

    ret = X509_set_issuer_name(x509, subject);
    if (ret != 1) goto ca_failed;

    /* Extensions */

    if (!add_extension_to_cert(x509, x509, "basicConstraints", "CA:TRUE"))
        goto ca_failed;

    if (!add_extension_to_cert(x509, x509, "keyUsage", "critical,keyCertSign,cRLSign"))
        goto ca_failed;

    if (!add_extension_to_cert(x509, x509, "subjectKeyIdentifier", "hash"))
        goto ca_failed;

    if (!add_extension_to_cert(x509, x509, "nsComment", "\"OpenSSL Generated Certificate\""))
        goto ca_failed;

    /* Signature */

    ret = X509_sign(x509, pk, EVP_sha256());
    if (ret == 0) goto ca_failed;

    /* Ecriture dans des fichiers */

    asprintf(&filename, "%s%c%s-key.pem", dir, G_DIR_SEPARATOR, label);

    stream = fopen(filename, "wb");
    if (stream == NULL)
    {
        free(filename);
        goto ca_failed;
    }

    ret = PEM_write_PrivateKey(stream, pk, NULL, NULL, 0, NULL, NULL);

    if (ret != 1)
        log_variadic_message(LMT_ERROR, _("Unable to write the CA key into '%s'"), filename);

    fclose(stream);

    free(filename);

    if (ret != 1)
        goto ca_failed;

    asprintf(&filename, "%s%c%s-cert.pem", dir, G_DIR_SEPARATOR, label);

    stream = fopen(filename, "wb");
    if (stream == NULL)
    {
        free(filename);
        goto ca_failed;
    }

    ret = PEM_write_X509(stream, x509);

    if (ret != 1)
        log_variadic_message(LMT_ERROR, _("Unable to write the CA certificate into '%s'"), filename);

    fclose(stream);

    free(filename);

    if (ret != 1)
        goto ca_failed;

    result = true;

    /* Libérations finales */

 ca_failed:
 ca_asign_failed:

    X509_free(x509);

 x509_failed:
 asign_failed:

    EVP_PKEY_free(pk);

 pk_failed:
 rsa_failed:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : sk    = pile d'extension à agrandir.                         *
*                nid   = identifiant de l'extension à apporter.               *
*                value = valeur portée par l'extension.                       *
*                                                                             *
*  Description : Ajoute une extension à une requête de signature.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool add_extension_to_req(STACK_OF(X509_EXTENSION) *sk, int nid, /*const */char *value)
{
    bool result;                            /* Bilan à retourner           */
    X509_EXTENSION *ext;                    /* Définition d'une extension  */
    int ret;                                /* Bilan d'un ajout            */

    result = false;

    ext = X509V3_EXT_conf_nid(NULL, NULL, nid, value);

    if (ext != NULL)
    {
        ret = sk_X509_EXTENSION_push(sk, ext);
        result = (ret == 1);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dir     = répertoire d'enregistrement de la création.        *
*                label   = étiquette à coller au certificat produit.          *
*                entries = éléments de l'identité à constituer.               *
*                                                                             *
*  Description : Crée un certificat pour application.                         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool build_keys_and_request(const char *dir, const char *label, const x509_entries *entries)
{
    bool result;                            /* Bilan à retourner           */
    RSA *rsa;                               /* Clef RSA pour le certificat */
    EVP_PKEY *pk;                           /* Enveloppe pour clef publique*/
    int ret;                                /* Bilan d'un appel            */
    X509_REQ *x509;                         /* Certificat X509 à définir   */
    X509_NAME *subject;                     /* Sujet du certificat         */
    STACK_OF(X509_EXTENSION) *exts;         /* Extensions du certificat    */
    char *filename;                         /* Chemin d'accès à un fichier */
    FILE *stream;                           /* Flux ouvert en écriture     */

    result = false;

    rsa = generate_rsa_key(2048, 17);
    if (rsa == NULL) goto rsa_failed;

    pk = EVP_PKEY_new();
    if (pk == NULL)
    {
        RSA_free(rsa);
        goto pk_failed;
    }

    ret = EVP_PKEY_assign_RSA(pk, rsa);
    if (ret != 1)
    {
        RSA_free(rsa);
        goto asign_failed;
    }

    x509 = X509_REQ_new();
    if (x509 == NULL) goto x509_failed;

    ret = X509_REQ_set_pubkey(x509, pk);
    if (ret != 1) goto req_asign_failed;

    /* Etablissement d'une identité */

    subject = X509_REQ_get_subject_name(x509);

#define SET_NAME_ENTRY(key, value)                                                          \
    do                                                                                      \
    {                                                                                       \
        if (entries->value != NULL)                                                         \
        {                                                                                   \
            ret = X509_NAME_add_entry_by_txt(subject, key, MBSTRING_UTF8,                   \
                                             (unsigned char *)entries->value, -1, -1, 0);   \
            if (ret != 1) goto req_failed;                                                  \
        }                                                                                   \
    }                                                                                       \
    while (0)

    SET_NAME_ENTRY("C", country);

    SET_NAME_ENTRY("ST", state);

    SET_NAME_ENTRY("L", locality);

    SET_NAME_ENTRY("O", organisation);

    SET_NAME_ENTRY("OU", organisational_unit);

    SET_NAME_ENTRY("CN", common_name);

#undef SET_NAME_ENTRY

    /* Extensions */

    exts = sk_X509_EXTENSION_new_null();
    if (exts == NULL) goto req_failed;

    if (!add_extension_to_req(exts, NID_key_usage, "critical,digitalSignature,keyEncipherment"))
        goto exts_failed;

    ret = X509_REQ_add_extensions(x509, exts);
    if (ret != 1) goto exts_failed;

    /* Signature */

    ret = X509_REQ_sign(x509, pk, EVP_sha256());
    if (ret == 0) goto req_failed_2;

    ret = X509_REQ_verify(x509, pk);
    if (ret != 1) goto req_failed_2;

    /* Ecriture dans des fichiers */

    asprintf(&filename, "%s%c%s-key.pem", dir, G_DIR_SEPARATOR, label);

    stream = fopen(filename, "wb");
    if (stream == NULL)
    {
        free(filename);
        goto req_failed_2;
    }

    ret = PEM_write_PrivateKey(stream, pk, NULL, NULL, 0, NULL, NULL);

    if (ret != 1)
        log_variadic_message(LMT_ERROR, _("Unable to write the CA key into '%s'"), filename);

    fclose(stream);

    free(filename);

    if (ret != 1)
        goto req_failed_2;

    asprintf(&filename, "%s%c%s-csr.pem", dir, G_DIR_SEPARATOR, label);

    stream = fopen(filename, "wb");
    if (stream == NULL)
    {
        free(filename);
        goto req_failed_2;
    }

    ret = PEM_write_X509_REQ(stream, x509);

    if (ret != 1)
        log_variadic_message(LMT_ERROR, _("Unable to write the CA certificate into '%s'"), filename);

    fclose(stream);

    free(filename);

    if (ret != 1)
        goto req_failed_2;

    result = true;

    /* Libérations finales */

 req_failed_2:
 exts_failed:

    sk_X509_EXTENSION_pop_free(exts, X509_EXTENSION_free);

 req_failed:
 req_asign_failed:

    X509_REQ_free(x509);

 x509_failed:
 asign_failed:

    EVP_PKEY_free(pk);

 pk_failed:
 rsa_failed:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : subject = sujet d'un élément X509.                           *
*                entries = éléments de l'identité constituée. [OUT]           *
*                                                                             *
*  Description : Recharge l'identité inscrite dans un élément X509.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool load_identity_from_x509(/*const */X509_NAME *subject, x509_entries *entries)
{
    bool result;                            /* Bilan à retourner           */
    int length;                             /* Taille du champ visé        */

    result = false;

#define GET_NAME_ENTRY(key, value)                                                          \
    do                                                                                      \
    {                                                                                       \
        length = X509_NAME_get_text_by_NID(subject, key, NULL, -1);                         \
        if (length != -1)                                                                   \
        {                                                                                   \
            entries->value = malloc((length + 1) * sizeof(char));                           \
            length = X509_NAME_get_text_by_NID(subject, key, entries->value, length + 1);   \
            assert(length != -1);                                                           \
            if (length == -1)                                                               \
                goto copy_failed;                                                           \
        }                                                                                   \
    }                                                                                       \
    while (0)

    GET_NAME_ENTRY(NID_countryName, country);

    GET_NAME_ENTRY(NID_stateOrProvinceName, state);

    GET_NAME_ENTRY(NID_localityName, locality);

    GET_NAME_ENTRY(NID_organizationName, organisation);

    GET_NAME_ENTRY(NID_organizationalUnitName, organisational_unit);

    GET_NAME_ENTRY(NID_commonName, common_name);

#undef GET_NAME_ENTRY

    result = true;

 copy_failed:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : csr     = fichier contenant le certificat à signer.          *
*                entries = éléments de l'identité constituée. [OUT]           *
*                                                                             *
*  Description : Recharge l'identité inscrite dans une requête de signature.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_identity_from_request(const char *csr, x509_entries *entries)
{
    bool result;                            /* Bilan à retourner           */
    FILE *stream;                           /* Flux ouvert en lecture      */
    X509_REQ *req;                          /* Certificat X509 à signer    */
    X509_NAME *subject;                     /* Sujet du certificat         */

    result = false;

    memset(entries, 0, sizeof(*entries));

    /* Chargement de la requête */

    stream = fopen(csr, "rb");
    if (stream == NULL) goto csr_read_failed;

    req = PEM_read_X509_REQ(stream, NULL, NULL, NULL);

    fclose(stream);

    if (req == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Unable to read the certificate signing request from '%s'"), csr);
        goto csr_read_failed;
    }

    /* Recherche des éléments */

    subject = X509_REQ_get_subject_name(req);

    result = load_identity_from_x509(subject, entries);

    X509_REQ_free(req);

 csr_read_failed:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : crt     = fichier contenant un certificat signé.             *
*                entries = éléments de l'identité constituée. [OUT]           *
*                                                                             *
*  Description : Recharge l'identité inscrite dans un certificat signé.       *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_identity_from_cert(const char *crt, x509_entries *entries)
{
    bool result;                            /* Bilan à retourner           */
    FILE *stream;                           /* Flux ouvert en lecture      */
    X509 *x;                                /* Certificat X509 signé       */
    X509_NAME *subject;                     /* Sujet du certificat         */

    result = false;

    memset(entries, 0, sizeof(*entries));

    /* Chargement de la requête */

    stream = fopen(crt, "rb");
    if (stream == NULL) goto crt_read_failed;

    x = PEM_read_X509(stream, NULL, NULL, NULL);

    fclose(stream);

    if (x == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Unable to read the signed certificate from '%s'"), crt);
        goto crt_read_failed;
    }

    /* Recherche des éléments */

    subject = X509_get_subject_name(x);

    result = load_identity_from_x509(subject, entries);

    X509_free(x);

 crt_read_failed:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : csr    = fichier contenant le certificat à signer.           *
*                cacert = fichier contenant le certificat de l'autorité.      *
*                cakey  = fichier contenant la clef privée du CA.             *
*                cert   = fichier contenant le certificat signé.              *
*                valid  = durée de validité en secondes.                      *
*                                                                             *
*  Description : Signe un certificat pour application.                        *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool sign_cert(const char *csr, const char *cacert, const char *cakey, const char *cert, unsigned long valid)
{
    FILE *stream;                           /* Flux ouvert en lecture      */
    X509_REQ *req;                          /* Certificat X509 à signer    */
    EVP_PKEY *pk;                           /* Enveloppe pour clef publique*/
    X509 *ca_cert;                          /* Certificat de l'autorité    */
    EVP_PKEY *ca_pk;                        /* Enveloppe pour clef privée  */
    X509 *x509;                             /* Certificat X509 à définir   */
    int ret;                                /* Bilan d'un appel            */
    X509_NAME *subject;                     /* Sujet de certificat         */

    /* Chargement de la requête */

    stream = fopen(csr, "rb");

    if (stream == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Unable to open the certificate signing request file '%s'"), csr);
        goto csr_read_failed;
    }

    req = PEM_read_X509_REQ(stream, NULL, NULL, NULL);

    fclose(stream);

    if (req == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Unable to read the certificate signing request from '%s'"), csr);
        goto csr_read_failed;
    }

    pk = X509_REQ_get_pubkey(req);
    if (pk == NULL) goto csr_no_pk;

    ret = X509_REQ_verify(req, pk);
    if (ret != 1) goto csr_bad_pk;

    /* Chargement des éléments de l'autorité */

    stream = fopen(cacert, "rb");

    if (stream == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Unable to open the CA certificate file '%s'"), cacert);
        goto cacert_read_failed;
    }

    ca_cert = PEM_read_X509(stream, NULL, NULL, NULL);

    fclose(stream);

    if (ca_cert == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Unable to read the CA certificate from '%s'"), cacert);
        goto cacert_read_failed;
    }

    stream = fopen(cakey, "rb");

    if (stream == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Unable to open the CA private key file '%s'"), cakey);
        goto cakey_read_failed;
    }

    ca_pk = PEM_read_PrivateKey(stream, NULL, NULL, NULL);

    fclose(stream);

    if (ca_pk == NULL)
    {
        log_variadic_message(LMT_ERROR, _("Unable to read the CA private key from '%s'"), cakey);
        goto cakey_read_failed;
    }

    /* Création d'un nouveau certificat */

    x509 = X509_new();
    if (x509 == NULL) goto x509_failed;

    ret = X509_set_version(x509, 2);
    if (ret != 1) goto signing_failed;

    ret = ASN1_INTEGER_set(X509_get_serialNumber(x509), 1);
    if (ret != 1) goto signing_failed;

    X509_gmtime_adj(X509_get_notBefore(x509), 0);
    X509_gmtime_adj(X509_get_notAfter(x509), valid);

    /* Transfert des informations existantes */

    ret = X509_set_pubkey(x509, pk);
    if (ret != 1) goto signing_failed;

    subject = X509_REQ_get_subject_name(req);

    ret = X509_set_subject_name(x509, subject);
    if (ret != 1) goto signing_failed;

    subject = X509_get_subject_name(ca_cert);

    ret = X509_set_issuer_name(x509, subject);
    if (ret != 1) goto signing_failed;

    /* Extensions */

    if (!add_extension_to_cert(ca_cert, x509, "basicConstraints", "CA:FALSE"))
        goto signing_failed;

    if (!add_extension_to_cert(ca_cert, x509, "keyUsage", "nonRepudiation,digitalSignature,keyEncipherment"))
        goto signing_failed;

    if (!add_extension_to_cert(ca_cert, x509, "subjectKeyIdentifier", "hash"))
        goto signing_failed;

    if (!add_extension_to_cert(ca_cert, x509, "authorityKeyIdentifier", "keyid,issuer:always"))
        goto signing_failed;

    if (!add_extension_to_cert(ca_cert, x509, "nsComment", "\"OpenSSL Generated Certificate\""))
        goto signing_failed;

    /* Signature */

    ret = X509_sign(x509, ca_pk, EVP_sha256());
    if (ret == 0) goto signing_failed;

    /* Ecriture dans un fichier */

    stream = fopen(cert, "wb");
    if (stream == NULL) goto signing_failed;

    ret = PEM_write_X509(stream, x509);

    if (ret != 1)
        log_variadic_message(LMT_ERROR, _("Unable to write the signed certificate into '%s'"), cert);

    fclose(stream);

    /* Libérations finales */

    X509_free(x509);
    EVP_PKEY_free(ca_pk);
    X509_free(ca_cert);
    EVP_PKEY_free(pk);
    X509_REQ_free(req);

    return true;

 signing_failed:

    X509_free(x509);

 x509_failed:

    EVP_PKEY_free(ca_pk);

 cakey_read_failed:

    X509_free(ca_cert);

 cacert_read_failed:

 csr_bad_pk:

    EVP_PKEY_free(pk);

 csr_no_pk:

    X509_REQ_free(req);

 csr_read_failed:

    return false;

}
