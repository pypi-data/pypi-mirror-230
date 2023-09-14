
/* Chrysalide - Outil d'analyse de fichiers binaires
 * group.c - conservation d'un groupe de correspondance avec du binaire
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#include "group.h"


#include <malloc.h>


#include "group-int.h"
#include "../parsers/attribute.h"



/* ------------------ DEFINITION D'UNE SEQUENCE DE CORRESPONDANCES ------------------ */


/* Initialise la classe des groupes de correspondances. */
static void g_record_group_class_init(GRecordGroupClass *);

/* Initialise une série de correspondances attributs/binaire. */
static void g_record_group_init(GRecordGroup *);

/* Supprime toutes les références externes. */
static void g_record_group_dispose(GRecordGroup *);

/* Procède à la libération totale de la mémoire. */
static void g_record_group_finalize(GRecordGroup *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Calcule ou fournit la zone couverte par une correspondance. */
static void g_record_group_get_range(const GRecordGroup *, mrange_t *);

/* Recherche la correspondance associée à un identifiant. */
static GMatchRecord *g_record_group_find_by_name(GRecordGroup *, const char *, size_t, unsigned int);

/* Transforme une énumération en constante entière. */
static bool g_record_group_resolve_enum(const GRecordGroup *, const sized_string_t *, const sized_string_t *, resolved_value_t *);



/* ---------------------------------------------------------------------------------- */
/*                    DEFINITION D'UNE SEQUENCE DE CORRESPONDANCES                    */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour une série de correspondances entre attributes et binaire. */
G_DEFINE_TYPE(GRecordGroup, g_record_group, G_TYPE_MATCH_RECORD);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des groupes de correspondances.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_group_class_init(GRecordGroupClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GMatchRecordClass *record;              /* Version parente de la classe*/

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_record_group_dispose;
    object->finalize = (GObjectFinalizeFunc)g_record_group_finalize;

    record = G_MATCH_RECORD_CLASS(klass);

    record->get_range = (get_record_range_fc)g_record_group_get_range;
    record->find = (find_record_by_name_fc)g_record_group_find_by_name;
    record->resolve = (resolve_record_enum_fc)g_record_group_resolve_enum;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une série de correspondances attributs/binaire.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_group_init(GRecordGroup *group)
{
    group->children = NULL;
    group->count = 0;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_group_dispose(GRecordGroup *group)
{
    size_t i;                               /* Boucle de parcours          */

    for (i = 0; i < group->count; i++)
        g_clear_object(&group->children[i]);

    G_OBJECT_CLASS(g_record_group_parent_class)->dispose(G_OBJECT(group));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_group_finalize(GRecordGroup *group)
{
    if (group->children != NULL)
        free(group->children);

    G_OBJECT_CLASS(g_record_group_parent_class)->finalize(G_OBJECT(group));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = contenu binaire lié à la correspondance.           *
*                kstruct = analyseur à l'origine de la correspondance.        *
*                                                                             *
*  Description : Crée une nouvelle série de correspondances attribut/binaire. *
*                                                                             *
*  Retour      : Instance mise en place ou NULL en cas d'échec.               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GRecordGroup *g_record_group_new(GKaitaiStruct *kstruct, GBinContent *content)
{
    GRecordGroup *result;                    /* Structure à retourner       */

    result = g_object_new(G_TYPE_RECORD_GROUP, NULL);

    if (!g_record_group_create(result, kstruct, content))
        g_clear_object(&result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group   = correspondance à initialiser pleinement.           *
*                kstruct = analyseur à l'origine de la correspondance.        *
*                content = contenu binaire lié à la correspondance.           *
*                                                                             *
*  Description : Met en place une série de correspondances attribut/binaire.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_record_group_create(GRecordGroup *group, GKaitaiStruct *kstruct, GBinContent *content)
{
    bool result;                            /* Bilan à retourner           */

    result = g_match_record_create(G_MATCH_RECORD(group), G_KAITAI_PARSER(kstruct), content);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group  = ensemble de correspondances attribut/binaire.       *
*                record = sous-corresponde à intégrer.                        *
*                                                                             *
*  Description : Ajoute une correspondance supplémentaire à une série.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_record_group_add_record(GRecordGroup *group, GMatchRecord *record)
{
    group->children = realloc(group->children, ++group->count * sizeof(GMatchRecord));

    group->children[group->count - 1] = record;
    g_object_ref(G_OBJECT(record));

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : group = correspondance à consulter.                          *
*                range = zone de couverture déterminée. [OUT]                 *
*                                                                             *
*  Description : Calcule ou fournit la zone couverte par une correspondance.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_record_group_get_range(const GRecordGroup *group, mrange_t *range)
{
    vmpa2t start;                           /* Position de départ          */
    mrange_t range_0;                       /* Première zone couverte      */
    mrange_t range_n;                       /* Dernière zone couverte      */
    vmpa2t end;                             /* Position de d'arrivée       */
    phys_t length;                          /* Taille de zone couverte     */

    if (group->count == 0)
    {
        init_vmpa(&start, VMPA_NO_PHYSICAL, VMPA_NO_VIRTUAL);
        init_mrange(range, &start, VMPA_NO_PHYSICAL);
    }

    else
    {
        g_match_record_get_range(group->children[0], &range_0);
        g_match_record_get_range(group->children[group->count - 1], &range_n);

        copy_vmpa(&start, get_mrange_addr(&range_0));

        compute_mrange_end_addr(&range_n, &end);
        length = compute_vmpa_diff(&start, &end);

        init_mrange(range, &start, length);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group = ensemble de correspondances attribut/binaire.        *
*                name  = désignation de l'élément recherché.                  *
*                len   = taille de cette désignation.                         *
*                level  = profondeur maximale à atteindre (fond : 0).         *
*                                                                             *
*  Description : Recherche la correspondance associée à un identifiant.       *
*                                                                             *
*  Retour      : Correspondance trouvée ou NULL.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GMatchRecord *g_record_group_find_by_name(GRecordGroup *group, const char *name, size_t len, unsigned int level)
{
    GMatchRecord *result;                   /* Correspondance à renvoyer   */
    GMatchRecordClass *class;               /* Classe parente normalisée   */
    size_t i;                               /* Boucle de parcours          */

    class = G_MATCH_RECORD_CLASS(g_record_group_parent_class);

    /**
     * Le cas d'un type utilisateur peut rattacher un attribut Kaitai à un groupe...
     */
    result = class->find(G_MATCH_RECORD(group), name, len, level);

    if (level > 0)
    {
        level--;

        for (i = 0; i < group->count && result == NULL; i++)
            result = g_match_record_find_by_name(group->children[i], name, len, level);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group = ensemble de correspondances attribut/binaire.        *
*                name  = désignation de l'élément recherché.                  *
*                label = étiquette de l'élément constant à traduire.          *
*                value = valeur entière correspondante. [OUT]                 *
*                                                                             *
*  Description : Transforme une énumération en constante entière.             *
*                                                                             *
*  Retour      : Bilan de l'opération : true si la résolution est réalisée.   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_record_group_resolve_enum(const GRecordGroup *group, const sized_string_t *name, const sized_string_t *label, resolved_value_t *value)
{
    bool result;                            /* Bilan à retourner           */
    GMatchRecord *base;                     /* Autre version du groupe     */
    size_t i;                               /* Boucle de parcours          */
    GKaitaiEnum *kenum;                     /* Enumération à consulter     */

    result = false;

    base = G_MATCH_RECORD(group);

    if (G_IS_KAITAI_STRUCT(base->creator))
    {
        kenum = g_kaitai_structure_get_enum(G_KAITAI_STRUCT(base->creator), name);

        if (kenum != NULL)
        {
            result = g_kaitai_enum_find_value(kenum, label, value);
            g_object_unref(G_OBJECT(kenum));
        }

    }

    for (i = 0; i < group->count && !result; i++)
        result = g_match_record_resolve_enum(group->children[i], name, label, value);

    return result;

}
