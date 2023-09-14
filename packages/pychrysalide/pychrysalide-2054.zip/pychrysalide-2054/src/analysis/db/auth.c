
/* Chrysalide - Outil d'analyse de fichiers binaires
 * auth.c - mise en place et gestion des autorisations pour les partages
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#include "auth.h"


#include <fcntl.h>
#include <glib.h>
#include <pwd.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/wait.h>


#include "../../common/extstr.h"
#include "../../common/io.h"
#include "../../common/pathname.h"
#include "../../common/xdg.h"
#include "../../common/xml.h"
#include "../../core/logs.h"



/* Fournit le répertoire d'enregistrement des certificats. */
static char *get_cert_storage_directory(const char *, const char *, const char *);

/* Calcule l'empreinte d'un fichier de demande de signature. */
static char *compute_csr_fingerprint(const char *);

/* Renvoie un accès à la configuration XML des privilèges. */
static bool open_server_priv_config(const char *, const char *, xmlDocPtr *, xmlXPathContextPtr *);

/* Assure la présence d'au moins un administrateur. */
static bool ensure_one_admin_is_registered(const char *, const char *, const char *);

/* Enregistre et clôture la configuration XML des privilèges. */
static bool close_server_priv_config(const char *, const char *, xmlDocPtr, xmlXPathContextPtr);


/******************************************************************************
*                                                                             *
*  Paramètres  : addr = adresse UNIX constituée. [OUT]                        *
*                                                                             *
*  Description : Met en place un canal UNIX pour un serveur interne.          *
*                                                                             *
*  Retour      : Bilan de la définition.                                      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool build_internal_server_socket(struct sockaddr_un *addr)
{
    bool result;                            /* Bilan à retourner           */
    char *suffix;                           /* Fin de la destination       */
    char *path;                             /* Chemin d'accès au canal     */
    int ret;                                /* Bilan intermédiaire         */
    size_t length;                          /* Taille du chemin complet    */

    suffix = strdup("chrysalide");
    suffix = stradd(suffix, G_DIR_SEPARATOR_S);
    suffix = stradd(suffix, "internal-server");

    path = get_xdg_config_dir(suffix);

    free(suffix);

    ret = ensure_path_exists(path);
    if (ret != 0) goto mts_exit;

    length = strlen(path) + 1;

#ifndef UNIX_PATH_MAX
#   define UNIX_PATH_MAX 108
#endif

    if (length > UNIX_PATH_MAX)
    {
        log_variadic_message(LMT_ERROR,
                             _("Impossible to use '%s' as UNIX socket path: string is too long ! (%zu vs %u)\n"),
                             path, length, UNIX_PATH_MAX);
        goto mts_exit;
    }

    memset(addr, 0, sizeof(struct sockaddr_un));

    addr->sun_family = AF_UNIX;
    strncpy(addr->sun_path, path, UNIX_PATH_MAX - 1);

    result = true;

 mts_exit:

    free(path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : type = type de certificat à gérer.                           *
*                host = dénomination du serveur visé ou NULL.                 *
*                port = port d'écoute ou NULL.                                *
*                sub  = éventuelle sous-partie ou NULL.                       *
*                                                                             *
*  Description : Fournit le répertoire de travail pour les données d'analyse. *
*                                                                             *
*  Retour      : Définition d'emplacement à libérer de la mémoire après usage.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *get_db_working_directory(const char *type, const char *host, const char *port, const char *sub)
{
    char *result;                           /* Chemin à retourner          */
    char *suffix;                           /* Fin de la destination       */

    suffix = strdup("chrysalide");
    suffix = stradd(suffix, G_DIR_SEPARATOR_S);
    suffix = stradd(suffix, type);
    suffix = stradd(suffix, G_DIR_SEPARATOR_S);

    if (host != NULL)
    {
        suffix = stradd(suffix, host);

        if (port == NULL)
            suffix = stradd(suffix, G_DIR_SEPARATOR_S);

    }

    if (port != NULL)
    {
        suffix = stradd(suffix, "-");
        suffix = stradd(suffix, port);
        suffix = stradd(suffix, G_DIR_SEPARATOR_S);
    }

    if (sub != NULL)
    {
        suffix = stradd(suffix, sub);
        suffix = stradd(suffix, G_DIR_SEPARATOR_S);
    }

    result = get_xdg_config_dir(suffix);

    free(suffix);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : outdir = répertoire de sortie pour les nouveaux fichiers.    *
*                host   = dénomination du serveur visé.                       *
*                port   = port d'écoute ou NULL.                              *
*                                                                             *
*  Description : Fournit le répertoire d'enregistrement des certificats.      *
*                                                                             *
*  Retour      : Définition d'emplacement à libérer de la mémoire après usage.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *get_cert_storage_directory(const char *outdir, const char *host, const char *port)
{
    char *result;                           /* Chemin à retourner          */

    result = strdup(outdir);

    if (!endswith(result, G_DIR_SEPARATOR_S))
        result = stradd(result, G_DIR_SEPARATOR_S);

    result = stradd(result, host);

    if (port == NULL)
        result = stradd(result, G_DIR_SEPARATOR_S);

    else
    {
        result = stradd(result, "-");
        result = stradd(result, port);
        result = stradd(result, G_DIR_SEPARATOR_S);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Détermine la désignation par défaut de l'usager.             *
*                                                                             *
*  Retour      : Nom déterminé à libérer de la mémoire.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *get_default_username(void)
{
    char *result;                           /* Désignation à retourner     */
    uid_t uid;                              /* Identifiant d'utilisateur   */
    struct passwd *pw;                      /* Indications sur l'usager    */

    uid = geteuid();
    pw = getpwuid(uid);

    if (pw != NULL)
        result = strdup(pw->pw_name);

    else
        result = strdup("anonymous");

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : valid   = durée de validité des certificats.                 *
*                entries = éléments d'identité à utiliser pour l'opération.   *
*                                                                             *
*  Description : Etablit une base pour l'identité de l'utilisateur.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool setup_client_identity(unsigned long valid, x509_entries *entries)
{
    bool result;                            /* Bilan de l'opération        */
    char *working;                          /* Répertoire pour le client   */

    working = get_db_working_directory("clients", NULL, NULL, NULL);

    result = mkpath(working);

    if (result)
    {
        if (entries->common_name == NULL)
        {
            entries->common_name = get_default_username();

            log_variadic_message(LMT_WARNING,
                                 _("Replaced the empty identity common name with '%s'"),
                                 entries->common_name);

        }

        result = build_keys_and_request(working, "client", entries);

    }

    free(working);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : host    = désignation du serveur à contacter.                *
*                port    = port d'écoute correspondant.                       *
*                valid   = durée de validité des certificats.                 *
*                entries = éléments d'identité à utiliser pour l'opération.   *
*                                                                             *
*  Description : Etablit une base pour l'identité d'un serveur.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool setup_server_identity(const char *host, const char *port, unsigned long valid, x509_entries *entries)
{
    bool result;                            /* Bilan de l'opération        */
    char *working;                          /* Répertoire pour le serveur  */
    char *csr;                              /* Requête de signature        */
    char *old;                              /* Conservation de l'origine   */
    char *new;                              /* Nouvelle désignation        */
    char *cacert;                           /* Certificat d'autorité       */
    char *cakey;                            /* Clef de cette autorité      */
    char *cert;                             /* Certificat signé en sortie  */

    if (host == NULL)
    {
        host = "standalone";
        port = NULL;
    }

    else if (strcmp(host, "standalone") != 0 && port == NULL)
        port = "1337";

    working = get_db_working_directory("servers", host, port, NULL);

    result = mkpath(working);

    if (result)
    {
        if (entries->common_name == NULL)
        {
            log_variadic_message(LMT_WARNING,
                                 _("Replaced the empty identity common name with '%s'"),
                                 host);

            entries->common_name = strdup(host);

        }

        old = entries->common_name;

        new = strdup(old);
        new = stradd(new, " CA");

        entries->common_name = new;

        result = build_keys_and_ca(working, "ca", valid, entries);

        entries->common_name = old;

        free(new);

        if (result)
            result = build_keys_and_request(working, "server", entries);

        if (result)
        {
            csr = build_absolute_filename(working, "server-csr.pem");
            cacert = build_absolute_filename(working, "ca-cert.pem");
            cakey = build_absolute_filename(working, "ca-key.pem");
            cert = build_absolute_filename(working, "server-cert.pem");

            result = sign_cert(csr, cacert, cakey, cert, valid);

            free(csr);
            free(cacert);
            free(cakey);
            free(cert);

        }

    }

    free(working);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : csr = fichier contenant le certificat à signer.              *
*                                                                             *
*  Description : Calcule l'empreinte d'un fichier de demande de signature.    *
*                                                                             *
*  Retour      : Empreinte calculée ou NULL en cas d'erreur.                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static char *compute_csr_fingerprint(const char *csr)
{
    char *result;                           /* Empreinte à retourner       */
    int fd;                                 /* Descripteur du fichier      */
    struct stat info;                       /* Informations sur le fichier */
    int ret;                                /* Bilan d'un appel            */
    void *data;                             /* Quantité de données traitées*/
    bool status;                            /* Bilan de la lecture         */

    result = NULL;

    fd = open(csr, O_RDONLY);
    if (fd == -1)
    {
        LOG_ERROR_N("open");
        goto exit;
    }

    ret = fstat(fd, &info);
    if (ret == -1)
    {
        LOG_ERROR_N("fstat");
        goto done;
    }

    data = malloc(info.st_size);

    status = safe_read(fd, data, info.st_size);

    if (status)
        result = g_compute_checksum_for_data(G_CHECKSUM_SHA256, data, info.st_size);

    free(data);

 done:

    close(fd);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : host   = désignation du serveur à contacter.                 *
*                port   = port d'écoute correspondant.                        *
*                valid  = durée de validité des certificats.                  *
*                csr    = fichier contenant le certificat à signer.           *
*                outdir = répertoire de sortie pour les nouveaux fichiers.    *
*                                                                             *
*  Description : Ajoute un certificat dans les utilisateurs d'un serveur.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_client_to_server(const char *host, const char *port, unsigned long valid, const char *csr, const char *outdir)
{
    bool result;                            /* Bilan de l'opération        */
    char *hash;                             /* Empreinte de la requête     */
    char *working;                          /* Répertoire pour le serveur  */
    char *cacert;                           /* Certificat d'autorité       */
    char *cakey;                            /* Clef de cette autorité      */
    char *storage;                          /* Répertoire de stockage      */
    char *dest;                             /* Destination d'une copie     */
    x509_entries entries;                   /* Identitié du client         */
    char *id;                               /* Identifiant associé         */

    result = false;

    if (host == NULL)
    {
        host = "standalone";
        port = NULL;
    }

    else if (strcmp(host, "standalone") != 0 && port == NULL)
        port = "1337";

    hash = compute_csr_fingerprint(csr);
    if (hash == NULL) goto exit;

    working = get_db_working_directory("servers", host, port, "authorized");

    result = mkpath(working);

    if (result)
    {
        hash = strprep(hash, working);
        hash = stradd(hash, "-cert.pem");

        free(working);

        working = get_db_working_directory("servers", host, port, NULL);

        cacert = build_absolute_filename(working, "ca-cert.pem");
        cakey = build_absolute_filename(working, "ca-key.pem");

        result = sign_cert(csr, cacert, cakey, hash, valid);

        if (result)
        {
            storage = get_cert_storage_directory(outdir, host, port);

            result = mkpath(storage);

            if (result)
            {
                dest = build_absolute_filename(storage, "ca-cert.pem");

                result = copy_file(dest, cacert);

                free(dest);

            }

            if (result)
            {
                dest = build_absolute_filename(storage, "client-cert.pem");

                result = copy_file(dest, hash);

                free(dest);

            }

            if (result)
            {
                result = load_identity_from_cert(hash, &entries);

                if (result)
                {
                    id = translate_x509_entries(&entries);

                    result = ensure_one_admin_is_registered(host, port, id);

                    free_x509_entries(&entries);

                }

            }

            free(storage);

        }

        free(cacert);
        free(cakey);

        free(hash);

    }

    free(working);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : host    = désignation du serveur à contacter.                *
*                port    = port d'écoute correspondant.                       *
*                xdoc    = document XML prêt à emploi. [OUT]                  *
*                context = contexte de recherche XPath. [OUT]                 *
*                                                                             *
*  Description : Renvoie un accès à la configuration XML des privilèges.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool open_server_priv_config(const char *host, const char *port, xmlDocPtr *xdoc, xmlXPathContextPtr *context)
{
    bool result;                            /* Bilan à retourner           */
    char *filename;                         /* Chemin d'accès à la config. */
    int ret;                                /* Test de présence de fichier */

    filename = get_db_working_directory("servers", host, port, NULL);
    filename = stradd(filename, "privs.xml");

    ret = access(filename, F_OK);

    if (ret == 0)
        result = open_xml_file(filename, xdoc, context);

    else
    {
        result = create_new_xml_file(xdoc, context);

        if (result)
            result = (ensure_node_exist(*xdoc, *context, "/ServerPrivLevels") != NULL);

    }

    free(filename);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : host = désignation du serveur à contacter.                   *
*                port = port d'écoute correspondant.                          *
*                id   = identification d'un utilisateur.                      *
*                                                                             *
*  Description : Assure la présence d'au moins un administrateur.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool ensure_one_admin_is_registered(const char *host, const char *port, const char *id)
{
    bool result;                            /* Bilan à retourner           */
    xmlDocPtr xdoc;                         /* Document XML de configurat° */
    xmlXPathContextPtr context;             /* Contexte de recherche XPath */
    xmlXPathObjectPtr xobject;              /* Cible d'une recherche       */
    size_t count;                           /* Nombre de contenus premiers */

    result = open_server_priv_config(host, port, &xdoc, &context);
    if (!result) goto exit;

    xobject = get_node_xpath_object(context, "/ServerPrivLevels/Administrators/User");

    count = XPATH_OBJ_NODES_COUNT(xobject);

    if (count == 0)
        result = add_content_to_node(xdoc, context, "/ServerPrivLevels/Administrators/User", id);

    if(xobject != NULL)
        xmlXPathFreeObject(xobject);

    result = close_server_priv_config(host, port, xdoc, context);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : host    = désignation du serveur à contacter.                *
*                port    = port d'écoute correspondant.                       *
*                xdoc    = document XML prêt à emploi.                        *
*                context = contexte de recherche XPath.                       *
*                                                                             *
*  Description : Enregistre et clôture la configuration XML des privilèges.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool close_server_priv_config(const char *host, const char *port, xmlDocPtr xdoc, xmlXPathContextPtr context)
{
    bool result;                            /* Bilan à retourner           */
    char *filename;                         /* Chemin d'accès à la config. */

    filename = get_db_working_directory("servers", host, port, NULL);
    filename = stradd(filename, "privs.xml");

    result = save_xml_file(xdoc, filename);

    close_xml_file(xdoc, context);

    free(filename);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Assure la présence d'un environnement pour serveur interne.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_internal_connections_setup(void)
{
    bool result;                            /* Bilan à retourner           */
    unsigned long valid;                    /* Durée de validité           */
    char *filename;                         /* Fichier devant être présent */
    int ret;                                /* Bilan d'une validation      */
    x509_entries identity;                  /* Nouvelle identité à pousser */
    bool status;                            /* Bilan intermédiaire         */
    char *csr;                              /* Fichier de requête          */
    char *outdir;                           /* Répertoire de sortie        */

    result = false;

    valid = 3 * 365 * 24 * 60 * 60;

    /* Teste la présence d'une identitié pour le client */

    filename = get_db_working_directory("clients", NULL, NULL, NULL);
    filename = stradd(filename, "client-csr.pem");

    ret = access(filename, R_OK);

    if (ret != 0)
    {
        memset(&identity, 0, sizeof(identity));

        status = setup_client_identity(valid, &identity);

        free_x509_entries(&identity);

        if (status)
            ret = access(filename, R_OK);
        else
            ret = -1;

    }

    free(filename);

    if (ret != 0)
        goto done;

    /* Teste la présence d'une identitié pour le serveur interne */

    filename = get_db_working_directory("servers", "standalone", NULL, NULL);
    filename = stradd(filename, "server-csr.pem");

    ret = access(filename, R_OK);

    if (ret != 0)
    {
        memset(&identity, 0, sizeof(identity));

        status = setup_server_identity("standalone", NULL, valid, &identity);

        free_x509_entries(&identity);

        if (status)
            ret = access(filename, R_OK);
        else
            ret = -1;

    }

    free(filename);

    if (ret != 0)
        goto done;

    /* Teste la présence d'une autorisation pour l'accès à ce serveur */

    filename = get_db_working_directory("clients", "standalone", NULL, NULL);
    filename = stradd(filename, "client-cert.pem");

    ret = access(filename, R_OK);

    if (ret != 0)
    {
        csr = get_db_working_directory("clients", NULL, NULL, NULL);
        csr = stradd(csr, "client-csr.pem");

        outdir = get_db_working_directory("clients", NULL, NULL, NULL);

        status = add_client_to_server("standalone", NULL, valid, csr, outdir);

        free(outdir);
        free(csr);

        if (status)
            ret = access(filename, R_OK);
        else
            ret = -1;

    }

    free(filename);

    if (ret != 0)
        goto done;

    result = true;

 done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Lance un serveur interne si besoin est.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool launch_internal_server(void)
{
    bool result;                            /* Bilan à retourner           */
    pid_t child;                            /* Identifiant de processus    */
    const char *prgm;                       /* Programme à exécuter        */
    int wstatus;                            /* Etat du serveur lancé       */
    pid_t ret;                              /* Bilan d'un appel            */

    char * const argv[] = {
        "chrysalide-hub",
        "run",
        NULL
    };

    child = fork();

    switch (child)
    {
        case -1:
            result = false;
            LOG_ERROR_N("fork");
            break;

        case 0:
#ifndef DISCARD_LOCAL
            prgm = PACKAGE_SOURCE_DIR "/src/chrysalide-hub";
#else
            prgm = "chrysalide-hub";
#endif

            execvp(prgm, argv);

            LOG_ERROR_N("execvp");
            exit(EXIT_FAILURE);
            break;

        default:

            ret = waitpid(child, &wstatus, 0);

            if (ret == -1)
            {
                result = false;
                LOG_ERROR_N("waitpid");
            }

            else
                result = (WEXITSTATUS(wstatus) == EXIT_SUCCESS);

            break;

    }

    return result;

}
