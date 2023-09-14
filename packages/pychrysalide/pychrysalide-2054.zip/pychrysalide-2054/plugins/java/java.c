
/* Chrysalide - Outil d'analyse de fichiers binaires
 * java.c - support du format Java
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


#include "java.h"


#include <string.h>


#include "java-int.h"











/* Initialise la classe des formats d'exécutables Java. */
static void g_java_format_class_init(GJavaFormatClass *);

/* Initialise une instance de format d'exécutable Java. */
static void g_java_format_init(GJavaFormat *);

/* Supprime toutes les références externes. */
static void g_java_format_dispose(GJavaFormat *);

/* Procède à la libération totale de la mémoire. */
static void g_java_format_finalize(GJavaFormat *);

/* Indique le type d'architecture visée par le format. */
static const char *g_java_format_get_target_machine(const GJavaFormat *);



/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à parcourir.                       *
*                                                                             *
*  Description : Indique si le format peut être pris en charge ici.           *
*                                                                             *
*  Retour      : true si la réponse est positive, false sinon.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool java_is_matching(GBinContent *content)
{
    bool result;                            /* Bilan à faire connaître     */
    vmpa2t addr;                            /* Tête de lecture initiale    */
    char magic[4];                          /* Idenfiant standard          */

    init_vmpa(&addr, 0, VMPA_NO_VIRTUAL);

    result = g_binary_content_read_raw(content, &addr, 4, (bin_t *)magic);

    result &= (memcmp(magic, "\xca\xfe\xba\xbe", 4) == 0);

    return result;

}


/* Indique le type défini pour un format d'exécutable Java. */
G_DEFINE_TYPE(GJavaFormat, g_java_format, G_TYPE_EXE_FORMAT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des formats d'exécutables Java.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_java_format_class_init(GJavaFormatClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GExeFormatClass *exe;                   /* Version en exécutable       */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_java_format_dispose;
    object->finalize = (GObjectFinalizeFunc)g_java_format_finalize;

    exe = G_EXE_FORMAT_CLASS(klass);

    exe->get_machine = (get_target_machine_fc)g_java_format_get_target_machine;
    //exe->refine_portions = (refine_portions_fc)g_java_format_refine_portions;

    exe->translate_phys = (translate_phys_fc)g_exe_format_without_virt_translate_offset_into_vmpa;
    exe->translate_virt = (translate_virt_fc)g_exe_format_without_virt_translate_address_into_vmpa;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de format d'exécutable Java.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_java_format_init(GJavaFormat *format)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_java_format_dispose(GJavaFormat *format)
{
    G_OBJECT_CLASS(g_java_format_parent_class)->dispose(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_java_format_finalize(GJavaFormat *format)
{
    G_OBJECT_CLASS(g_java_format_parent_class)->finalize(G_OBJECT(format));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à parcourir.                       *
*                length  = taille du contenu en question.                     *
*                                                                             *
*  Description : Prend en charge un nouveau format Java.                      *
*                                                                             *
*  Retour      : Adresse de la structure mise en place ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinFormat *g_java_format_new(const bin_t *content, off_t length)
{
    GJavaFormat *result;                      /* Structure à retourner       */
    off_t offset;                           /* Tête de lecture             */

    result = g_object_new(G_TYPE_JAVA_FORMAT, NULL);

    //g_binary_format_set_content(G_BIN_FORMAT(result), content, length);


    offset = 0;

    if (!read_java_header(result, &offset, &result->header))
    {
        /* TODO */
        return NULL;
    }


    return G_BIN_FORMAT(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Indique le type d'architecture visée par le format.          *
*                                                                             *
*  Retour      : Identifiant de l'architecture ciblée par le format.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static const char *g_java_format_get_target_machine(const GJavaFormat *format)
{
    return "jvm";

}












#if 0

#include <malloc.h>
#include <string.h>


#include "attribute.h"
#include "field.h"
#include "java-int.h"
#include "method.h"
#include "pool.h"
#include "../../common/endianness.h"




/* Indique le type d'architecture visée par le format. */
FormatTargetMachine get_java_target_machine(const java_format *);



/* Fournit les références aux zones de code à analyser. */
bin_part **get_java_default_code_parts(const java_format *, size_t *);


/* Fournit le prototype de toutes les routines détectées. */
GBinRoutine **get_all_java_routines(const java_format *, size_t *);





/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à parcourir.                       *
*                length  = taille du contenu en question.                     *
*                                                                             *
*  Description : Indique si le format peut être pris en charge ici.           *
*                                                                             *
*  Retour      : true si la réponse est positive, false sinon.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool java_is_matching(const uint8_t *content, off_t length)
{
    bool result;                            /* Bilan à faire connaître     */

    result = false;

    if (length >= 4)
        result = (strncmp((const char *)content, "\xca\xfe\xba\xbe", 4) == 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire à parcourir.                       *
*                length  = taille du contenu en question.                     *
*                                                                             *
*  Description : Prend en charge une nouvelle classe Java.                    *
*                                                                             *
*  Retour      : Adresse de la structure mise en place ou NULL en cas d'échec.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

exe_format *load_java(const uint8_t *content, off_t length)
{
    java_format *result;                    /* Adresse à retourner         */
    off_t pos;                              /* Point d'analyse             */
    uint32_t magic;                         /* Identifiant Java            */
    uint16_t i;                             /* Boucle de parcours          */

    result = (java_format *)calloc(1, sizeof(java_format));

    EXE_FORMAT(result)->content = content;
    EXE_FORMAT(result)->length = length;

    EXE_FORMAT(result)->get_target_machine = (get_target_machine_fc)get_java_target_machine;
    EXE_FORMAT(result)->get_def_parts = (get_def_parts_fc)get_java_default_code_parts;
    EXE_FORMAT(result)->get_all_routines = (get_all_routines_fc)get_all_java_routines;

    pos = 0;

    if (!read_u32(&magic, content, &pos, length, SRE_BIG))
        goto ldj_error;

    if (!read_u16(&result->minor_version, content, &pos, length, SRE_BIG))
        goto ldj_error;

    if (!read_u16(&result->major_version, content, &pos, length, SRE_BIG))
        goto ldj_error;

    if (!load_java_pool(result, &pos))
        goto ldj_error;

    if (!read_u16((uint16_t *)&result->access, content, &pos, length, SRE_BIG))
        goto ldj_error;

    if (!read_u16(&result->this_class, content, &pos, length, SRE_BIG))
        goto ldj_error;

    if (!read_u16(&result->super_class, content, &pos, length, SRE_BIG))
        goto ldj_error;

    if (!read_u16(&result->interfaces_count, content, &pos, length, SRE_BIG))
       goto ldj_error;

    for (i = 0; i < result->interfaces_count; i++)
        if (!read_u16(&result->interfaces[i], content, &pos, length, SRE_BIG))
            goto ldj_error;

    if (!load_java_fields(result, &pos))
        goto ldj_error;

    if (!load_java_methods(result, &pos))
        goto ldj_error;

    if (!load_java_attributes(result, &pos, &result->attributes, &result->attributes_count))
        goto ldj_error;

    return EXE_FORMAT(result);

 ldj_error:

    unload_java(result);

    return NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à supprimer.            *
*                                                                             *
*  Description : Efface la prise en charge une nouvelle classe Java.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void unload_java(java_format *format)
{
    if (format->pool_len > 0)
        unload_java_pool(format);

    if (format->interfaces_count > 0)
        free(format->interfaces);

    if (format->fields_count > 0)
        unload_java_fields(format);

    if (format->methods_count > 0)
        unload_java_methods(format);

    if (format->attributes_count > 0)
        unload_java_attributes(format, format->attributes, format->attributes_count);

    free(format);

}





/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Indique le type d'architecture visée par le format.          *
*                                                                             *
*  Retour      : Identifiant de l'architecture ciblée par le format.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

FormatTargetMachine get_java_target_machine(const java_format *format)
{
    return FTM_JVM;

}





/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                count  = quantité de zones listées. [OUT]                    *
*                                                                             *
*  Description : Fournit les références aux zones de code à analyser.         *
*                                                                             *
*  Retour      : Zones de code à analyser.                                    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bin_part **get_java_default_code_parts(const java_format *format, size_t *count)
{
    bin_part **result;                      /* Tableau à retourner         */
    uint16_t i;                             /* Boucle de parcours          */
    off_t offset;                           /* Position physique           */
    off_t size;                             /* Taille de la partie         */
    bin_part *part;                         /* Partie à intégrer à la liste*/

    result = NULL;
    *count = 0;

    for (i = 0; i < format->methods_count; i++)
        if (find_java_method_code_part(&format->methods[i], &offset, &size))
        {
            part = create_bin_part();

            set_bin_part_values(part, offset, size, offset);

            result = (bin_part **)realloc(result, ++(*count) * sizeof(bin_part *));
            result[*count - 1] = part;

        }

    return result;

}




/******************************************************************************
*                                                                             *
*  Paramètres  : format = informations chargées à consulter.                  *
*                count  = taille du tableau créé. [OUT]                       *
*                                                                             *
*  Description : Fournit le prototype de toutes les routines détectées.       *
*                                                                             *
*  Retour      : Tableau créé ou NULL si aucun symbole de routine trouvé.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinRoutine **get_all_java_routines(const java_format *format, size_t *count)
{
    *count = 0;

    return NULL;

}

#endif
