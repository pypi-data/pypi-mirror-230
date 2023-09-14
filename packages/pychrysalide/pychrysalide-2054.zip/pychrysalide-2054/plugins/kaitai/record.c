
/* Chrysalide - Outil d'analyse de fichiers binaires
 * record.c - définition d'une correspondance avec un attribut Kaitai
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


#include "record.h"


#include <assert.h>


#include "expression.h"
#include "record-int.h"
#include "parsers/attribute.h"



/* Initialise la classe des correspondances avec du binaire. */
static void g_match_record_class_init(GMatchRecordClass *);

/* Initialise une correspondance avec du binaire. */
static void g_match_record_init(GMatchRecord *);

/* Supprime toutes les références externes. */
static void g_match_record_dispose(GMatchRecord *);

/* Procède à la libération totale de la mémoire. */
static void g_match_record_finalize(GMatchRecord *);

/* Recherche la correspondance associée à un identifiant. */
static GMatchRecord *_g_match_record_find_by_name(GMatchRecord *, const char *, size_t, unsigned int);



/* Indique le type défini pour une correspondance avec du binaire. */
G_DEFINE_TYPE(GMatchRecord, g_match_record, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des correspondances avec du binaire.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_match_record_class_init(GMatchRecordClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_match_record_dispose;
    object->finalize = (GObjectFinalizeFunc)g_match_record_finalize;

    klass->find = (find_record_by_name_fc)_g_match_record_find_by_name;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : record = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une correspondance avec du binaire.               *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_match_record_init(GMatchRecord *record)
{
    record->creator = NULL;

    record->content = NULL;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : record = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_match_record_dispose(GMatchRecord *record)
{
    G_OBJECT_CLASS(g_match_record_parent_class)->dispose(G_OBJECT(record));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : record = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_match_record_finalize(GMatchRecord *record)
{
    G_OBJECT_CLASS(g_match_record_parent_class)->finalize(G_OBJECT(record));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : record  = correspondance à initialiser pleinement.           *
*                creator = lecteur à l'origine de la correspondance.          *
*                content = contenu binaire lié à la correspondance.           *
*                                                                             *
*  Description : Met en place une correspondance entre attribut et binaire.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_match_record_create(GMatchRecord *record, GKaitaiParser *creator, GBinContent *content)
{
    bool result;                            /* Bilan à retourner           */

    result = true;

    record->creator = creator;
    g_object_ref(G_OBJECT(creator));

    record->content = content;

    if (content != NULL)
        g_object_ref(G_OBJECT(content));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : record = correspondance à consulter.                         *
*                                                                             *
*  Description : Renvoie vers le lecteur à l'origine de la correspondance.    *
*                                                                             *
*  Retour      : Lecteur à l'origine de la création.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GKaitaiParser *g_match_record_get_creator(const GMatchRecord *record)
{
    GKaitaiParser *result;                  /* Instance à retourner        */

    result = record->creator;

    g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : record  = correspondance à modifier.                         *
*                creator = lecteur à l'origine de la correspondance.          *
*                                                                             *
*  Description : Modifie la référence au créateur de la correspondance.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_match_record_fix_creator(GMatchRecord *record, GKaitaiParser *creator)
{
    g_object_unref(G_OBJECT(record->creator));

    record->creator = creator;
    g_object_ref(G_OBJECT(creator));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : record = correspondance à consulter.                         *
*                                                                             *
*  Description : Fournit le contenu lié à une correspondance établie.         *
*                                                                             *
*  Retour      : Contenu binaire associé.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinContent *g_match_record_get_content(const GMatchRecord *record)
{
    GBinContent *result;                    /* Instance à retourner        */

    result = record->content;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : record = correspondance à consulter.                         *
*                range  = zone de couverture déterminée. [OUT]                *
*                                                                             *
*  Description : Calcule ou fournit la zone couverte par une correspondance.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_match_record_get_range(const GMatchRecord *record, mrange_t *range)
{
    GMatchRecordClass *class;               /* Classe de l'instance        */

    class = G_MATCH_RECORD_GET_CLASS(record);

    class->get_range(record, range);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : record = correspondance établie à consulter.                 *
*                out    = tableau d'octets retournés. [OUT]                   *
*                len    = taille de ce tableau alloué. [OUT]                  *
*                                                                             *
*  Description : Lit les octets bruts couverts par une correspondance.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_match_record_read_raw_bytes(const GMatchRecord *record, bin_t **out, size_t *len)
{
    mrange_t range;                         /* Zone de correspondance      */
    const bin_t *data;                      /* Accès aux données brutes    */

    g_match_record_get_range(record, &range);

    *len = get_mrange_length(&range);

    data = g_binary_content_get_raw_access(record->content, get_mrange_addr(&range), *len);
    assert(data != NULL);

    *out = malloc(sizeof(bin_t) * (*len + 1));

    memcpy(*out, data, *len);
    (*out)[*len] = '\0';

}


/******************************************************************************
*                                                                             *
*  Paramètres  : record = correspondance à consulter.                         *
*                name   = désignation de l'élément recherché.                 *
*                len    = taille de cette désignation.                        *
*                level  = profondeur maximale à atteindre (fond : 0).         *
*                                                                             *
*  Description : Recherche la correspondance associée à un identifiant.       *
*                                                                             *
*  Retour      : Correspondance trouvée ou NULL.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GMatchRecord *_g_match_record_find_by_name(GMatchRecord *record, const char *name, size_t len, unsigned int level)
{
    GMatchRecord *result;                   /* Trouvaille à retourner      */
    const char *label;                      /* Etiquette à manipuler       */
    size_t label_len;                       /* Taille de cette étiquette   */

    result = NULL;

    if (G_IS_KAITAI_ATTRIBUTE(record->creator))
    {
        label = g_kaitai_attribute_get_label(G_KAITAI_ATTRIBUTE(record->creator));

        label_len = strlen(label);

        if (label_len == len && strncmp(label, name, len) == 0)
        {
            result = record;
            g_object_ref(G_OBJECT(result));
        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : record = correspondance à consulter.                         *
*                name   = désignation de l'élément recherché.                 *
*                len    = taille de cette désignation.                        *
*                level  = profondeur maximale à atteindre (fond : 0).         *
*                                                                             *
*  Description : Recherche la correspondance associée à un identifiant.       *
*                                                                             *
*  Retour      : Correspondance trouvée ou NULL.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GMatchRecord *g_match_record_find_by_name(GMatchRecord *record, const char *name, size_t len, unsigned int level)
{
    GMatchRecord *result;                   /* Trouvaille à retourner      */
    GMatchRecordClass *class;               /* Classe de l'instance        */

    class = G_MATCH_RECORD_GET_CLASS(record);

    result = class->find(record, name, len, level);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : record = correspondance à consulter.                         *
*                name   = désignation de l'élément recherché.                 *
*                label  = étiquette de l'élément constant à traduire.         *
*                value  = valeur entière correspondante. [OUT]                *
*                                                                             *
*  Description : Transforme une énumération en constante entière.             *
*                                                                             *
*  Retour      : Bilan de l'opération : true si la résolution est réalisée.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_match_record_resolve_enum(const GMatchRecord *record, const sized_string_t *name, const sized_string_t *label, resolved_value_t *value)
{
    bool result;                            /* Bilan à retourner           */
    GMatchRecordClass *class;               /* Classe de l'instance        */

    class = G_MATCH_RECORD_GET_CLASS(record);

    if (class->resolve == NULL)
        result = false;

    else
        result = class->resolve(record, name, label, value);

    return result;

}
