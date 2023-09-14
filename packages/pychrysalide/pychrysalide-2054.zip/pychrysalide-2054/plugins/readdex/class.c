
/* Chrysalide - Outil d'analyse de fichiers binaires
 * class.c - annotation des définitions de classes
 *
 * Copyright (C) 2016-2019 Cyrille Bagard
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


#include "class.h"


#include <i18n.h>
#include <plugins/dex/pool.h>
#include <plugins/dex/dex_def.h>
#include <plugins/fmtp/parser.h>


#include "code.h"



/* Définition des champs */

static fmt_field_def _dex_class_defs[] = {

    {
        .name = "class_idx",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index into the type_ids list for this class"))

    },

    {
        .name = "access_flags",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Access flags for the class"))

    },

    {
        .name = "superclass_idx",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index for the superclass or NO_INDEX if this class has no superclass"))

    },

    {
        .name = "interfaces_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the list of interfaces"))

    },

    {
        .name = "source_file_idx",

        .size = MDS_32_BITS,
        .repeat = 1,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index for the name of the file containing the original source or NO_INDEX"))

    },

    {
        .name = "annotations_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the annotations structure for this class"))

    },

    {
        .name = "class_data_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the associated class data for this item"))

    },

    {
        .name = "static_values_off",

        .size = MDS_32_BITS,
        .repeat = 1,

        PLAIN_COMMENT(__("Offset to the list of initial values for static fields"))

    }

};

static fmt_field_def _dex_class_data[] = {

    {
        .name = "static_fields_size",

        .is_uleb128 = true,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Number of static fields defined in this item"))

    },

    {
        .name = "instance_fields_size",

        .is_uleb128 = true,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Number of instance fields defined in this item"))

    },

    {
        .name = "direct_methods_size",

        .is_uleb128 = true,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Number of direct methods defined in this item"))

    },

    {
        .name = "virtual_methods_size",

        .is_uleb128 = true,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Number of virtual methods defined in this item"))

    }

};

static fmt_field_def _dex_encoded_field[] = {

    {
        .name = "field_idx_diff",

        .is_uleb128 = true,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index into the field_ids list for the identity of this field"))

    },

    {
        .name = "access_flags",

        .is_uleb128 = true,

        PLAIN_COMMENT(__("Access flags for the field"))

    }

};

static fmt_field_def _dex_encoded_method[] = {

    {
        .name = "method_idx_diff",

        .is_uleb128 = true,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Index into the method_ids list for the identity of this method"))

    },

    {
        .name = "access_flags",

        .is_uleb128 = true,

        DISPLAY_RULES(IOD_DEC),

        PLAIN_COMMENT(__("Access flags for the method"))

    },

    {
        .name = "code_off",

        .is_uleb128 = true,

        PLAIN_COMMENT(__("Offset to the code structure for this method"))

    }

};



/* Commente les définitions des classes pour la VM Dalvik. */
static bool annotate_dex_class_data(const GDexFormat *, GPreloadInfo *, const GDexClass *, uint32_t );

/* Commente les définitions des champs encodés. */
static bool annotate_dex_encoded_field(const GDexFormat *, GPreloadInfo *, vmpa2t *);

/* Commente les définitions des méthodes encodées. */
static bool annotate_dex_encoded_method(const GDexFormat *, GPreloadInfo *, const encoded_method *, vmpa2t *);



/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                status = barre de statut à tenir informée.                   *
*                                                                             *
*  Description : Commente les définitions des classes pour la VM Dalvik.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool annotate_dex_class_defs(const GDexFormat *format, GPreloadInfo *info, GtkStatusStack *status)
{
    bool result;                            /* Bilan à retourner           */
    const dex_header *header;               /* En-tête principale          */
    vmpa2t pos;                             /* Tête de lecture des symboles*/
    GDexPool *pool;                         /* Table de ressources         */
    uint32_t count;                         /* Nombre de classes présentes */
    activity_id_t msg;                      /* Message de progression      */
    GBinFormat *bformat;                    /* Autre version du format     */
    uint32_t i;                             /* Boucle de parcours          */
    GDexClass *class;                       /* Classe chargée à manipuler  */
    const class_def_item *def;              /* Définition brute à lire     */

    header = g_dex_format_get_header(format);

    result = g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), header->class_defs_off, &pos);

    if (!result)
        goto adcd_exit;

    pool = g_dex_format_get_pool(format);

    count = g_dex_pool_count_classes(pool);

    msg = gtk_status_stack_add_activity(status, _("Writing annotations for all Dex classes..."), count);

    bformat = G_BIN_FORMAT(format);

    for (i = 0; i < count && result; i++)
    {
        result = parse_field_definitions(PARSING_DEFS(_dex_class_defs), bformat, info, &pos, NULL);
        if (!result) break;

        /* Annotations supplémentaires */

        class = g_dex_pool_get_class(pool, i);

        def = g_dex_class_get_definition(class);

        if (def->class_data_off > 0)
            result = annotate_dex_class_data(format, info, class, def->class_data_off);

        g_object_unref(G_OBJECT(class));

        gtk_status_stack_update_activity_value(status, msg, 1);

    }

    gtk_status_stack_remove_activity(status, msg);

    g_object_unref(G_OBJECT(pool));

 adcd_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                class  = classe Dex dont les données sont à commenter.       *
*                offset = tête de lecture physique des symboles.              *
*                                                                             *
*  Description : Commente les définitions des classes pour la VM Dalvik.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool annotate_dex_class_data(const GDexFormat *format, GPreloadInfo *info, const GDexClass *class, uint32_t offset)
{
    bool result;                            /* Bilan à retourner           */
    vmpa2t pos;                             /* Tête de lecture des symboles*/
    GBinFormat *bformat;                    /* Autre version du format     */
    const class_data_item *data;            /* Données chargées à lire     */
    uleb128_t i;                            /* Boucle de parcours          */

    result = g_exe_format_translate_offset_into_vmpa(G_EXE_FORMAT(format), offset, &pos);

    if (!result)
        goto adcd_exit;

    bformat = G_BIN_FORMAT(format);

    result = parse_field_definitions(PARSING_DEFS(_dex_class_data), bformat, info, &pos, NULL);

    if (!result)
        goto adcd_exit;

    /* Chargements complémentaires */

    data = g_dex_class_get_data(class);

    if (data != NULL)
    {
        for (i = 0; i < data->static_fields_size && result; i++)
            result = annotate_dex_encoded_field(format, info, &pos);

        for (i = 0; i < data->instance_fields_size && result; i++)
            result = annotate_dex_encoded_field(format, info, &pos);

        for (i = 0; i < data->direct_methods_size && result; i++)
            result = annotate_dex_encoded_method(format, info, &data->direct_methods[i], &pos);

        for (i = 0; i < data->virtual_methods_size && result; i++)
            result = annotate_dex_encoded_method(format, info, &data->virtual_methods[i], &pos);

    }

 adcd_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                pos    = tête de lecture à faire progresser. [OUT]           *
*                                                                             *
*  Description : Commente les définitions des champs encodés.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool annotate_dex_encoded_field(const GDexFormat *format, GPreloadInfo *info, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */
    GBinFormat *bformat;                    /* Autre version du format     */

    bformat = G_BIN_FORMAT(format);

    result = parse_field_definitions(PARSING_DEFS(_dex_encoded_field), bformat, info, pos, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description de l'exécutable à compléter.            *
*                info   = informations à constituer en avance de phase.       *
*                method = méthode à décrire.                                  *
*                pos    = tête de lecture à faire progresser. [OUT]           *
*                                                                             *
*  Description : Commente les définitions des méthodes encodées.              *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool annotate_dex_encoded_method(const GDexFormat *format, GPreloadInfo *info, const encoded_method *method, vmpa2t *pos)
{
    bool result;                            /* Bilan à retourner           */
    GBinFormat *bformat;                    /* Autre version du format     */

    bformat = G_BIN_FORMAT(format);

    result = parse_field_definitions(PARSING_DEFS(_dex_encoded_method), bformat, info, pos, NULL);

    /* Chargements complémentaires, si non abstraite ni native */

    if (result && method->code_off > 0)
        result = annotate_dex_code_item(format, info, method->code_off);

    return result;

}
