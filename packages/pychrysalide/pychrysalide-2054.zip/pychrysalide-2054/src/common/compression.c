
/* Chrysalide - Outil d'analyse de fichiers binaires
 * compression.c - facilités de manipulation des archives
 *
 * Copyright (C) 2018 Cyrille Bagard
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


#include "compression.h"


#include <fcntl.h>
#include <stdio.h>
#include <string.h>


#include "io.h"
#include "../analysis/contents/memory.h"



/* Fixe le tampon pour la lecture des fichiers à inclure */
#define ARCHIVE_RBUF_SIZE 2048



/******************************************************************************
*                                                                             *
*  Paramètres  : output   = archive dont le contenu est à composer.           *
*                filename = chemin d'accès au fichier d'entrée.               *
*                path     = chemin d'accès dans l'archive.                    *
*                                                                             *
*  Description : Ajoute un élement à une archive.                             *
*                                                                             *
*  Retour      : Code de retour pour l'opération.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

CPError add_file_into_archive(struct archive *output, const char *filename, const char *path)
{
    CPError result;                     /* Code de retour à renvoyer   */
    struct stat info;                   /* Informations d'origine      */
    int ret;                                /* Bilan d'un appel            */
    struct archive_entry *entry;        /* Elément de l'archive        */
    int fd;                             /* Flux ouvert en lecture      */
    char buffer[ARCHIVE_RBUF_SIZE];     /* Tampon pour les transferts  */
    ssize_t len;                        /* Quantité de données lues    */

    result = CPE_ARCHIVE_ERROR;

    ret = stat(filename, &info);
    if (ret != 0)
    {
        perror("stat");
        result = CPE_SYSTEM_ERROR;
        goto afia_quick_exit;
    }

    entry = archive_entry_new();

    archive_entry_copy_stat(entry, &info);
    archive_entry_set_pathname(entry, path);

    ret = archive_write_header(output, entry);
    if (ret != 0) goto afia_exit;

    fd = open(filename, O_RDONLY);
    if (fd == -1)
    {
        perror("open");
        result = CPE_SYSTEM_ERROR;
        goto afia_exit;
    }

    for (len = safe_read_partial(fd, buffer, ARCHIVE_RBUF_SIZE);
         len > 0;
         len = safe_read_partial(fd, buffer, ARCHIVE_RBUF_SIZE))
    {
        if (archive_write_data(output, buffer, len) != len)
            goto afia_exit;
    }

    close(fd);

    archive_entry_free(entry);

    return CPE_NO_ERROR;

 afia_exit:

    archive_entry_free(entry);

 afia_quick_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : intput   = archive dont le contenu est à extraire.           *
*                entry    = entrée de l'archive à extraire.                   *
*                filename = chemin d'accès au fichier de sortie.              *
*                                                                             *
*  Description : Extrait un élement d'une archive.                            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool dump_archive_entry_into_file(struct archive *input, struct archive_entry *entry, const char *filename)
{
    bool result;                            /* Conclusion à retourner      */
    int flags;                              /* Propriétés à extraire       */
    struct archive *output;                 /* Extracteur générique        */
    int ret;                                /* Bilan d'un appel            */
    const void *buff;                       /* Tampon de copie             */
    size_t size;                            /* Quantité copiée             */
    __LA_INT64_T offset;                    /* Position de lecture         */

    result = false;

    archive_entry_set_pathname(entry, filename);

    /* Propriétés à restaurer */
    flags = ARCHIVE_EXTRACT_TIME;
    flags |= ARCHIVE_EXTRACT_PERM;
    flags |= ARCHIVE_EXTRACT_ACL;
    flags |= ARCHIVE_EXTRACT_FFLAGS;

    output = archive_write_disk_new();
    archive_write_disk_set_options(output, flags);
    archive_write_disk_set_standard_lookup(output);

    ret = archive_write_header(output, entry);
    if (ret != ARCHIVE_OK) goto daeif_exit;

    for (ret = archive_read_data_block(input, &buff, &size, &offset);
         ret == ARCHIVE_OK;
         ret = archive_read_data_block(input, &buff, &size, &offset))
    {
        ret = archive_write_data_block(output, buff, size, offset);
    }

    if (ret != ARCHIVE_EOF)
        goto daeif_exit;

    ret = archive_write_finish_entry(output);

    result = (ret == ARCHIVE_OK);

 daeif_exit:

    archive_write_close(output);
    archive_write_free(output);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : intput   = archive dont le contenu est à extraire.           *
*                entry    = entrée de l'archive à extraire.                   *
*                                                                             *
*  Description : Extrait un élement d'une archive.                            *
*                                                                             *
*  Retour      : Nouveau contenu volatile ou NULL en cas d'échec.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *dump_archive_entry_into_memory(struct archive *input, struct archive_entry *entry)
{
    GBinContent *result;                    /* Contenu à retourner         */
    bin_t *full_data;                       /* Données rassemblées         */
    phys_t full_size;                       /* Somme de toutes les tailles */
    const void *buff;                       /* Tampon de copie             */
    size_t size;                            /* Quantité copiée             */
    __LA_INT64_T offset;                    /* Position de lecture         */
    int ret;                                /* Bilan d'un appel            */

    result = NULL;

    full_data = NULL;
    full_size = 0;

    for (ret = archive_read_data_block(input, &buff, &size, &offset);
         ret == ARCHIVE_OK;
         ret = archive_read_data_block(input, &buff, &size, &offset))
    {
        full_data = realloc(full_data, full_size + size);

        memcpy(full_data + full_size, buff, size);

        full_size += size;

    }

    if (ret == ARCHIVE_EOF)
        result = g_memory_content_new(full_data, full_size);

    if (full_data != NULL)
        free(full_data);

    return result;

}
