
/* Chrysalide - Outil d'analyse de fichiers binaires
 * configuration.c - éléments de configuration du programme
 *
 * Copyright (C) 2014-2019 Cyrille Bagard
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


#include "configuration.h"


#include <assert.h>
#include <limits.h>
#include <malloc.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>


#include "configuration-int.h"
#include "../common/cpp.h"
#include "../common/extstr.h"
#include "../common/io.h"
#include "../common/xdg.h"
#include "../common/xml.h"



/* ---------------------------- ELEMENT DE CONFIGURATION ---------------------------- */


/* Initialise la classe des blocs de données binaires. */
static void g_config_param_class_init(GCfgParamClass *);

/* Initialise une instance de bloc de données binaires. */
static void g_config_param_init(GCfgParam *);

/* Supprime toutes les références externes. */
static void g_config_param_dispose(GCfgParam *);

/* Procède à la libération totale de la mémoire. */
static void g_config_param_finalize(GCfgParam *);

/* Lit un paramètre de configuration depuis un fichier. */
static bool g_config_param_read(GCfgParam *, xmlXPathContextPtr);

/* Ecrit un paramètre de configuration dans un fichier. */
static bool g_config_param_write(GCfgParam *, xmlDocPtr, xmlXPathContextPtr);



/* --------------------- PARTIES IMPREVISIBLES DE CONFIGURATION --------------------- */


/* Groupe de paramètres non fixés à l'avance (instance) */
struct _GCfgGroup
{
    GObject parent;                         /* A laisser en premier        */

    char *root;                             /* Chemin d'accès commun       */
    ConfigParamType type;                   /* Type de valeur              */

};

/* Groupe de paramètres non fixés à l'avance (classe) */
struct _GCfgGroupClass
{
    GObjectClass parent;                    /* A laisser en premier        */

};


/* Initialise la classe des groupes de paramètres. */
static void g_config_group_class_init(GCfgGroupClass *);

/* Initialise une instance de groupe de paramètres. */
static void g_config_group_init(GCfgGroup *);

/* Supprime toutes les références externes. */
static void g_config_group_dispose(GCfgGroup *);

/* Procède à la libération totale de la mémoire. */
static void g_config_group_finalize(GCfgGroup *);

/* Charge tous les paramètres correspondants au groupe. */
static void g_config_group_load(GCfgGroup *, GGenConfig *, xmlXPathContextPtr);



/* ----------------------- GESTION GENERIQUE DE CONFIGURATION ----------------------- */


/* Initialise la classe des blocs de données binaires. */
static void g_generic_config_class_init(GGenConfigClass *);

/* Initialise une instance de bloc de données binaires. */
static void g_generic_config_init(GGenConfig *);

/* Supprime toutes les références externes. */
static void g_generic_config_dispose(GGenConfig *);

/* Procède à la libération totale de la mémoire. */
static void g_generic_config_finalize(GGenConfig *);

/* Réagit à un changement de valeur pour un paramètre. */
static void on_config_param_modified(GCfgParam *, GGenConfig *);



/* ---------------------------------------------------------------------------------- */
/*                              ELEMENT DE CONFIGURATION                              */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour les configurations génériques. */
G_DEFINE_TYPE(GCfgParam, g_config_param, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des blocs de données binaires.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_config_param_class_init(GCfgParamClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_config_param_dispose;
    object->finalize = (GObjectFinalizeFunc)g_config_param_finalize;

    g_signal_new("modified",
                 G_TYPE_CFG_PARAM,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GCfgParamClass, modified),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__VOID,
                 G_TYPE_NONE, 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de bloc de données binaires.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_config_param_init(GCfgParam *param)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_config_param_dispose(GCfgParam *param)
{
    G_OBJECT_CLASS(g_config_param_parent_class)->dispose(G_OBJECT(param));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param = instance d'objet GLib à traiter.                     *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_config_param_finalize(GCfgParam *param)
{
    free(param->path);

    switch (param->type)
    {
        case CPT_STRING:
            if (param->def.string != NULL)
                free(param->def.string);
            if (param->cur.string != NULL)
                free(param->cur.string);
            break;

        default:
            break;

    }

    G_OBJECT_CLASS(g_config_param_parent_class)->finalize(G_OBJECT(param));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin d'accès à un paramètre en guise de clef.       *
*                type = type de paramètre à installer.                        *
*                ...  = valeur par défaut du paramètre.                       *
*                                                                             *
*  Description : Crée un paramètre de configuration.                          *
*                                                                             *
*  Retour      : Elément mis en place.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GCfgParam *g_config_param_new(const char *path, ConfigParamType type, ...)
{
    GCfgParam *result;                      /* Structure à retourner       */
    va_list ap;                             /* Liste d'arguments           */
    param_value value;                      /* Valeur par défaut           */

    result = NULL;

    va_start(ap, type);

    switch (type)
    {
        case CPT_BOOLEAN:
            value.boolean = va_arg(ap, /*bool*/int);
            break;

        case CPT_INTEGER:
            value.integer = va_arg(ap, int);
            break;

        case CPT_ULONG:
            value.ulong = va_arg(ap, unsigned long);
            break;

        case CPT_STRING:
            value.string = va_arg(ap, char *);
            if (value.string != NULL)
                value.string = strdup(value.string);
            break;

        case CPT_COLOR:
            value.color = *va_arg(ap, GdkRGBA *);
            break;

        default:
            assert(false);
            goto quick_exit;
            break;

    }

    va_end(ap);

    result = g_object_new(G_TYPE_CFG_PARAM, NULL);

    g_config_param_build(result, path, type, &value);

 quick_exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param = paramètre de configuration à construire.             *
*                path  = chemin d'accès à un paramètre en guise de clef.      *
*                type  = type de paramètre à installer.                       *
*                value = valeur par défaut à appliquer.                       *
*                                                                             *
*  Description : Construit un paramètre de configuration.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_config_param_build(GCfgParam *param, const char *path, ConfigParamType type, const param_value *value)
{
    param->path = strdup(path);
    param->hash = fnv_64a_hash(path);

    param->type = type;

    param->def = *value;

    g_config_param_reset(param);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : path = chemin d'accès à un paramètre en guise de clef.       *
*                type = type de paramètre à installer.                        *
*                                                                             *
*  Description : Crée un paramètre de configuration sans valeur.              *
*                                                                             *
*  Retour      : Elément mis en place.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GCfgParam *g_config_param_new_empty(const char *path, ConfigParamType type)
{
    GCfgParam *result;                      /* Structure à retourner       */

    result = g_object_new(G_TYPE_CFG_PARAM, NULL);

    g_config_param_build_empty(result, path, type);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param = paramètre de configuration à construire.             *
*                path  = chemin d'accès à un paramètre en guise de clef.      *
*                type  = type de paramètre à installer.                       *
*                                                                             *
*  Description : Construit un paramètre de configuration sans valeur.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_config_param_build_empty(GCfgParam *param, const char *path, ConfigParamType type)
{
    param->path = strdup(path);
    param->hash = fnv_64a_hash(path);

    param->type = type;

    g_config_param_make_empty(param);

    param->def = param->cur;
    param->def_empty = true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param   = paramètre de configuration à charger.              *
*                context = contexte de lecture d'un fichier XML.              *
*                                                                             *
*  Description : Lit un paramètre de configuration depuis un fichier.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_config_param_read(GCfgParam *param, xmlXPathContextPtr context)
{
    char *access;                           /* Chemin d'accès XML          */
    char *value;                            /* Valeur en chaîne de carac.  */
    unsigned long ulval;                    /* Valeur transformée          */
    GdkRGBA color;                          /* Couleur transformée         */
    char *end;                              /* Position terminale          */

    access = strdup(param->path);
    access = strrpl(access, ".", "/");
    access = strprep(access, "/ChrysalideConfig/");

    value = get_node_text_value(context, access);
    if (value == NULL) goto gcpr_no_value;

    if (strlen(value) == 0)
        g_config_param_make_empty(param);

    else
        switch (param->type)
        {
            case CPT_BOOLEAN:
                g_config_param_set_value(param, strcmp(value, "true") == 0);
                break;

            case CPT_INTEGER:
                g_config_param_set_value(param, atoi(value));
                break;

            case CPT_ULONG:
                ulval = strtoul(value, NULL, 10);
                g_config_param_set_value(param, ulval);
                break;

            case CPT_STRING:
                g_config_param_set_value(param, value);
                break;

            case CPT_COLOR:
                color.red = strtod(value, &end);
                if (*end != ';') goto gcpr_bad_value;
                else end++;
                color.green = strtod(end, &end);
                if (*end != ';') goto gcpr_bad_value;
                else end++;
                color.blue = strtod(end, &end);
                if (*end != ';') goto gcpr_bad_value;
                else end++;
                color.alpha = strtod(end, &end);
                g_config_param_set_value(param, &color);
                break;

            default:
                assert(false);
                break;

        }

    free(value);

 gcpr_no_value:

    free(access);

    return true;

 gcpr_bad_value:

    free(value);

    return false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param   = paramètre de configuration à charger.              *
*                xdoc    = document XML à mettre en place.                    *
*                context = contexte de lecture d'un fichier XML.              *
*                                                                             *
*  Description : Ecrit un paramètre de configuration dans un fichier.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool g_config_param_write(GCfgParam *param, xmlDocPtr xdoc, xmlXPathContextPtr context)
{
    bool result;                            /* Bilan à retourner           */
    ConfigParamState state;                 /* Etat du paramètre           */
    char *access;                           /* Chemin d'accès XML          */
    char int_val[sizeof(XSTR(INT_MIN)) + 1];/* Valeur en chaîne de carac.  */
    char ul_val[sizeof(XSTR(ULONG_MAX)) + 1];/* Valeur en chaîne de carac. */
    char *color;                            /* Valeurs d'une couleur       */

    state = g_config_param_get_state(param);

    if (state & CPS_DEFAULT)
        return true;

    result = true;

    access = strdup(param->path);
    access = strrpl(access, ".", "/");
    access = strprep(access, "/ChrysalideConfig/");

    if (state & CPS_EMPTY)
        result = add_content_to_node(xdoc, context, access, "");

    else
        switch (param->type)
        {
            case CPT_BOOLEAN:
                result = add_content_to_node(xdoc, context, access,
                                             param->cur.boolean ? "true" : "false");
                break;

            case CPT_INTEGER:
                snprintf(int_val, sizeof(int_val), "%d", param->cur.integer);
                result = add_content_to_node(xdoc, context, access, int_val);
                break;

            case CPT_ULONG:
                snprintf(ul_val, sizeof(ul_val), "%lu", param->cur.ulong);
                result = add_content_to_node(xdoc, context, access, ul_val);
                break;

            case CPT_STRING:

                if (param->def.string != NULL && param->def.string != NULL
                    && strcmp(param->cur.string, param->def.string) == 0)
                    break;

                result = add_content_to_node(xdoc, context, access,
                                             param->cur.string != NULL ? param->cur.string : "");
                break;

            case CPT_COLOR:

                asprintf(&color, "%f;%f;%f;%f",
                         param->cur.color.red,
                         param->cur.color.green,
                         param->cur.color.blue,
                         param->cur.color.alpha);

                result = add_content_to_node(xdoc, context, access, color);

                free(color);
                break;

            default:
                assert(false);
                break;

        }

    free(access);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param = paramètre de configuration à analyser.               *
*                path  = chemin d'accès à retrouver.                          *
*                                                                             *
*  Description : Etablit une comparaison selon un chemin d'accès.             *
*                                                                             *
*  Retour      : -1, 0 ou 1 selon les conclusions de la comparaison.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gint g_config_param_compare(const GCfgParam *param, const GCfgParam *path)
{
    gint result;                            /* Bilan à renvoyer            */

    result = cmp_fnv_64a(param->hash, path->hash);

    if (result == 0)
        result = strcmp(param->path, path->path);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param = paramètre de configuration à consulter.              *
*                                                                             *
*  Description : Indique le chemin d'accès utilisé pour un paramètre.         *
*                                                                             *
*  Retour      : Clef servant de chemin d'accès.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_config_param_get_path(const GCfgParam *param)
{
    return param->path;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param = paramètre de configuration à consulter.              *
*                                                                             *
*  Description : Indique le type de valeur utilisée par un paramètre.         *
*                                                                             *
*  Retour      : Type de paramètre.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ConfigParamType g_config_param_get_ptype(const GCfgParam *param)
{
    ConfigParamType result;                 /* Type de paramètre à renvoyer*/

    result = param->type;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param = paramètre de configuration à consulter.              *
*                                                                             *
*  Description : Indique le statut d'une valeur utilisée par un paramètre.    *
*                                                                             *
*  Retour      : Etat de paramètre.                                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

ConfigParamState g_config_param_get_state(GCfgParam *param)
{
    if (param->cached_state == CPS_UNDEFINED)
    {
        if (param->def_empty || param->cur_empty)
        {
            param->cached_state = (param->def_empty && param->cur_empty ? CPS_DEFAULT : CPS_CHANGED);

            if (param->cur_empty)
                param->cached_state |= CPS_EMPTY;

            goto gcpgs_recached;

        }

        switch (param->type)
        {
            case CPT_BOOLEAN:
                param->cached_state = (param->def.boolean == param->cur.boolean ? CPS_DEFAULT : CPS_CHANGED);
                break;

            case CPT_INTEGER:
                param->cached_state = (param->def.integer == param->cur.integer ? CPS_DEFAULT : CPS_CHANGED);
                break;

            case CPT_ULONG:
                param->cached_state = (param->def.ulong == param->cur.ulong ? CPS_DEFAULT : CPS_CHANGED);
                break;

            case CPT_STRING:
                if (param->def.string == NULL && param->cur.string == NULL)
                    param->cached_state = CPS_DEFAULT;
                else if (param->def.string != NULL && param->cur.string != NULL)
                    param->cached_state = strcmp(param->def.string, param->cur.string) == 0 ? CPS_DEFAULT : CPS_CHANGED;
                else
                    param->cached_state = CPS_CHANGED;
                break;

            case CPT_COLOR:
                param->cached_state = (param->def.color.red == param->cur.color.red
                                       && param->def.color.blue == param->cur.color.blue
                                       && param->def.color.green == param->cur.color.green
                                       && param->def.color.alpha == param->cur.color.alpha
                                       ? CPS_DEFAULT : CPS_CHANGED);
                break;

            default:
                break;

        }

 gcpgs_recached:;

    }

    return param->cached_state;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param = paramètre à mettre à jour.                           *
*                                                                             *
*  Description : Efface toute valeur courante d'un paramètre de configuration.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_config_param_make_empty(GCfgParam *param)
{
    switch (param->type)
    {
        case CPT_BOOLEAN:
            param->cur.boolean = false;
            break;

        case CPT_INTEGER:
            param->cur.integer = INT_MIN;
            break;

        case CPT_ULONG:
            param->cur.ulong = 0;
            break;

        case CPT_STRING:
            if (param->cur.string != NULL)
            {
                free(param->cur.string);
                param->cur.string = NULL;
            }
            break;

        case CPT_COLOR:
            param->cur.color.red = 0;
            param->cur.color.blue = 0;
            param->cur.color.green = 0;
            param->cur.color.alpha = 0;
            break;

        default:
            break;

    }

    if (!param->cur_empty)
    {
        param->cur_empty = true;

        /* Réinitialisation du cache d'état... */
        param->cached_state = CPS_UNDEFINED;

        g_signal_emit_by_name(param, "modified");

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param = paramètre à mettre à jour.                           *
*                                                                             *
*  Description : Réinitialise la valeur d'un paramètre de configuration.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_config_param_reset(GCfgParam *param)
{
    bool modified;                          /* Détermine une modification  */

    modified = !(g_config_param_get_state(param) & CPS_DEFAULT);

    switch (param->type)
    {
        case CPT_BOOLEAN:
            param->cur.boolean = param->def.boolean;
            break;

        case CPT_INTEGER:
            param->cur.integer = param->def.integer;
            break;

        case CPT_ULONG:
            param->cur.ulong = param->def.ulong;
            break;

        case CPT_STRING:
            if (param->def.string != NULL)
                param->cur.string = strdup(param->def.string);
            else
                param->cur.string = NULL;
            break;

        case CPT_COLOR:
            param->cur.color = param->def.color;
            break;

        default:
            assert(false);
            break;

    }

    if (modified)
    {
        param->cur_empty = param->def_empty;

        /* Réinitialisation du cache d'état... */
        param->cached_state = CPS_UNDEFINED;

        g_signal_emit_by_name(param, "modified");

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param = paramètre à mettre à jour.                           *
*                ...   = nouvelle valeur du paramètre.                        *
*                                                                             *
*  Description : Modifie la valeur courante d'un paramètre de configuration.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_config_param_set_value(GCfgParam *param, ...)
{
    va_list ap;                             /* Liste d'arguments           */
    bool old_boolean;                       /* Valeur booléenne            */
    int old_integer;                        /* Valeur entière              */
    unsigned long old_ulong;                /* Valeur entière positive     */
    char *old_string;                       /* Chaîne de caractères        */
    GdkRGBA old_color;                      /* Couleur avec transparence   */
    bool modified;                          /* Détermine une modification  */

    va_start(ap, param);

    switch (param->type)
    {
        case CPT_BOOLEAN:
            old_boolean = param->cur.boolean;
            param->cur.boolean = va_arg(ap, /*bool*/int);
            modified = (old_boolean != param->cur.boolean);
            break;

        case CPT_INTEGER:
            old_integer = param->cur.integer;
            param->cur.integer = va_arg(ap, int);
            modified = (old_integer != param->cur.integer);
            break;

        case CPT_ULONG:
            old_ulong = param->cur.ulong;
            param->cur.ulong = va_arg(ap, unsigned long);
            modified = (old_ulong != param->cur.ulong);
            break;

        case CPT_STRING:
            old_string = param->cur.string;

            param->cur.string = va_arg(ap, char *);
            if (param->cur.string != NULL)
                param->cur.string = strdup(param->cur.string);

            if (old_string == NULL && param->cur.string == NULL)
                modified = false;
            else if (old_string != NULL && param->cur.string != NULL)
                modified = (strcmp(old_string, param->cur.string) != 0);
            else
                modified = true;

            if (old_string != NULL)
                free(old_string);

            break;

        case CPT_COLOR:
            old_color = param->cur.color;
            param->cur.color = *va_arg(ap, GdkRGBA *);
            modified = (old_color.red != param->cur.color.red
                        || old_color.blue != param->cur.color.blue
                        || old_color.green != param->cur.color.green
                        || old_color.alpha != param->cur.color.alpha);
            break;

        default:
            assert(false);
            modified = false;
            break;

    }

    va_end(ap);

    if (modified)
    {
        param->cur_empty = false;

        /* Réinitialisation du cache d'état... */
        param->cached_state = CPS_UNDEFINED;

        g_signal_emit_by_name(param, "modified");

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param = paramètre à consulter.                               *
*                ...   = zone d'enregistrement de la valeur du paramètre.     *
*                                                                             *
*  Description : Indique la valeur courante d'un paramètre de configuration.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_config_param_get_value(const GCfgParam *param, ...)
{
    va_list ap;                             /* Liste d'arguments           */

    va_start(ap, param);

    switch (param->type)
    {
        case CPT_BOOLEAN:
            *(va_arg(ap, bool *)) = param->cur.boolean;
            break;

        case CPT_INTEGER:
            *(va_arg(ap, int *)) = param->cur.integer;
            break;

        case CPT_ULONG:
            *(va_arg(ap, unsigned long *)) = param->cur.ulong;
            break;

        case CPT_STRING:
            *(va_arg(ap, char **)) = param->cur.string;
            break;

        case CPT_COLOR:
            *(va_arg(ap, GdkRGBA *)) = param->cur.color;
            break;

        default:
            assert(false);
            break;

    }

    va_end(ap);

}



/* ---------------------------------------------------------------------------------- */
/*                       PARTIES IMPREVISIBLES DE CONFIGURATION                       */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour les groupes de paramètres non prévisibiles. */
G_DEFINE_TYPE(GCfgGroup, g_config_group, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des groupes de paramètres.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_config_group_class_init(GCfgGroupClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_config_group_dispose;
    object->finalize = (GObjectFinalizeFunc)g_config_group_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group = instance à initialiser.                              *
*                                                                             *
*  Description : Initialise une instance de groupe de paramètres.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_config_group_init(GCfgGroup *group)
{

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

static void g_config_group_dispose(GCfgGroup *group)
{
    G_OBJECT_CLASS(g_config_group_parent_class)->dispose(G_OBJECT(group));

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

static void g_config_group_finalize(GCfgGroup *group)
{
    free(group->root);

    G_OBJECT_CLASS(g_config_group_parent_class)->finalize(G_OBJECT(group));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : root = base du chemin d'accès à un groupe de paramètres.     *
*                type = type de groupètre à installer.                        *
*                                                                             *
*  Description : Crée un groupe de paramètres de configuration.               *
*                                                                             *
*  Retour      : Groupe mis en place.                                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GCfgGroup *g_config_group_new(const char *root, ConfigParamType type)
{
    GCfgGroup *result;                      /* Structure à retourner       */

    result = g_object_new(G_TYPE_CFG_GROUP, NULL);

    result->root = strdup(root);
    result->type = type;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : group   = groupe de paramètres de configuration à étudier.   *
*                config  = ensemble de paramètres à compléter.                *
*                context = contexte de lecture d'un fichier XML.              *
*                                                                             *
*  Description : Charge tous les paramètres correspondants au groupe.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_config_group_load(GCfgGroup *group, GGenConfig *config, xmlXPathContextPtr context)
{
    char *access;                           /* Chemin d'accès XML          */
    xmlXPathObjectPtr xpathObj;             /* Cible d'une recherche       */
    int i;                                  /* Boucle de parcours          */
    char *key;                              /* Clef d'accès à un paramètre */
    GCfgParam *param;                       /* Nouveau paramètre à ajouter */

    access = strdup(group->root);
    access = strrpl(access, ".", "/");
    access = stradd(access, "/*");
    access = strprep(access, "/ChrysalideConfig/");

    xpathObj = get_node_xpath_object(context, access);

    for (i = 0; i < XPATH_OBJ_NODES_COUNT(xpathObj); i++)
    {
        asprintf(&key, "%s.%s", group->root, NODE_FROM_PATH_OBJ(xpathObj, i)->name);

        param = g_config_param_new_empty(key, group->type);
        _g_generic_config_add_param(config, param, false);
        g_object_unref(G_OBJECT(param));

        free(key);

    }

    if (xpathObj != NULL)
        xmlXPathFreeObject(xpathObj);

    free(access);

}



/* ---------------------------------------------------------------------------------- */
/*                         GESTION GENERIQUE DE CONFIGURATION                         */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini par la GLib pour les configurations génériques. */
G_DEFINE_TYPE(GGenConfig, g_generic_config, G_TYPE_OBJECT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des blocs de données binaires.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_generic_config_class_init(GGenConfigClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_generic_config_dispose;
    object->finalize = (GObjectFinalizeFunc)g_generic_config_finalize;

    g_signal_new("modified",
                 G_TYPE_GEN_CONFIG,
                 G_SIGNAL_RUN_LAST,
                 G_STRUCT_OFFSET(GGenConfigClass, modified),
                 NULL, NULL,
                 g_cclosure_marshal_VOID__OBJECT,
                 G_TYPE_NONE, 1, G_TYPE_OBJECT);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de bloc de données binaires.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_generic_config_init(GGenConfig *config)
{
    g_rw_lock_init(&config->params_access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_generic_config_dispose(GGenConfig *config)
{
    g_list_free_full(config->groups, g_object_unref);

    config->groups = NULL;

    g_list_free_full(config->params, g_object_unref);

    config->params = NULL;

    G_OBJECT_CLASS(g_generic_config_parent_class)->dispose(G_OBJECT(config));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_generic_config_finalize(GGenConfig *config)
{
    if (config->filename != NULL)
        free(config->filename);

    g_rw_lock_clear(&config->params_access);

    G_OBJECT_CLASS(g_generic_config_parent_class)->finalize(G_OBJECT(config));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée un gestionnaire configuration générique.                *
*                                                                             *
*  Retour      : Elément mis en place.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGenConfig *g_generic_config_new(void)
{
    GGenConfig *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_GEN_CONFIG, NULL);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : name = désignation de la configuration.                      *
*                                                                             *
*  Description : Crée un gestionnaire configuration générique.                *
*                                                                             *
*  Retour      : Elément mis en place.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GGenConfig *g_generic_config_new_from_file(const char *name)
{
    GGenConfig *result;                     /* Structure à retourner       */

    result = g_object_new(G_TYPE_GEN_CONFIG, NULL);

    g_generic_config_build(result, name);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = ensemble de paramètres de configuration à manipuler.*
*                name   = désignation de la configuration.                    *
*                                                                             *
*  Description : Crée un gestionnaire configuration générique.                *
*                                                                             *
*  Retour      : Elément mis en place.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_generic_config_build(GGenConfig *config, const char *name)
{
    char *suffix;                           /* Fin du nom de fichier       */

    if (g_path_is_absolute(name))
        config->filename = strdup(name);

    else
    {
        suffix = strdup("chrysalide");
        suffix = stradd(suffix, G_DIR_SEPARATOR_S);
        suffix = stradd(suffix, name);
        suffix = stradd(suffix, ".xml");

        config->filename = get_xdg_config_dir(suffix);

        free(suffix);

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = ensemble de paramètres de configuration à consulter.*
*                                                                             *
*  Description : Indique le fichier utilisé pour l'enregistrement XML.        *
*                                                                             *
*  Retour      : Chemin d'accès, potentiellement non existant.                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

const char *g_generic_config_get_filename(const GGenConfig *config)
{
    char *result;                           /* Chemin à retourner          */

    result = config->filename;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = configuration à mettre à jour.                      *
*                write  = précise le type d'accès prévu (lecture/écriture).   *
*                lock   = indique le sens du verrouillage à mener.            *
*                                                                             *
*  Description : Met à disposition un encadrement des accès aux paramètres.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_generic_config_lock_unlock(GGenConfig *config, bool write, bool lock)
{
    if (write)
    {
        if (lock) g_rw_lock_writer_lock(&config->params_access);
        else g_rw_lock_writer_unlock(&config->params_access);
    }
    else
    {
        if (lock) g_rw_lock_reader_lock(&config->params_access);
        else g_rw_lock_reader_unlock(&config->params_access);
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = ensemble de paramètres de configuration à charger.  *
*                                                                             *
*  Description : Lit la configuration depuis un fichier.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_generic_config_read(GGenConfig *config)
{
    bool result;                            /* Bilan à retourner           */
    int ret;                                /* Test de présence de fichier */
    xmlDocPtr xdoc;                         /* Document XML de configurat° */
    xmlXPathContextPtr context;             /* Contexte de recherche XPath */
    GList *iter;                            /* Boucle de parcours          */

    ret = access(config->filename, F_OK);
    if (ret != 0) return true;

    if (!open_xml_file(config->filename, &xdoc, &context))
        return false;

    g_generic_config_rlock(config);

    for (iter = g_list_first(config->groups);
         iter != NULL;
         iter = g_list_next(iter))
    {
        g_config_group_load(G_CFG_GROUP(iter->data), config, context);
    }

    for (result = true, iter = g_list_first(config->params);
         result && iter != NULL;
         iter = g_list_next(iter))
    {
        result = g_config_param_read(G_CFG_PARAM(iter->data), context);
    }

    g_generic_config_runlock(config);

    close_xml_file(xdoc, context);

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = ensemble de paramètres de configuration à décharger.*
*                                                                             *
*  Description : Ecrit la configuration dans un fichier.                      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_generic_config_write(GGenConfig *config)
{
    bool result;                            /* Bilan à retourner           */
    xmlDocPtr xdoc;                         /* Document XML de configurat° */
    xmlXPathContextPtr context;             /* Contexte de recherche XPath */
    GList *iter;                            /* Boucle de parcours          */

    if (config->filename == NULL)
        result = false;

    else
    {
        result = create_new_xml_file(&xdoc, &context);
        if (!result) goto exit;

        g_generic_config_rlock(config);

        for (iter = g_list_first(config->params);
             result && iter != NULL;
             iter = g_list_next(iter))
        {
            result = g_config_param_write(G_CFG_PARAM(iter->data), xdoc, context);
        }

        g_generic_config_runlock(config);

        if (result)
            result = save_xml_file(xdoc, config->filename);

        close_xml_file(xdoc, context);

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = configuration à mettre à jour.                      *
*                param  = groupe de paramètres à prendre en compte.           *
*                                                                             *
*  Description : Ajoute la définition d'un groupe à une configuration.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_generic_config_add_group(GGenConfig *config, GCfgGroup *group)
{
    g_generic_config_wlock(config);

    g_object_ref(G_OBJECT(group));

    config->groups = g_list_append(config->groups, group);

    g_generic_config_wunlock(config);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = ensemble de paramètres de configuration.            *
*                path   = chemin d'accès au paramètre visé.                   *
*                lock   = pose un verrou si ce n'est déjà fait.               *
*                                                                             *
*  Description : Retrouve un élément de configuration par son chemin.         *
*                                                                             *
*  Retour      : Elément trouvé ou NULL en cas d'échec.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GCfgParam *_g_generic_config_search(GGenConfig *config, const char *path, bool lock)
{
    GCfgParam *result;                      /* Instance à retourner        */
    GList *item;                            /* Elément générique de liste  */
    GCfgParam fake;                         /* Faux élément partiel        */

    fake.path = (char *)path;
    fake.hash = fnv_64a_hash(path);

    if (lock)
        g_generic_config_rlock(config);

    item = g_list_find_custom(config->params, &fake, (GCompareFunc)g_config_param_compare);

    result = item ? item->data : NULL;

    if (result != NULL)
        g_object_ref(G_OBJECT(result));

    if (lock)
        g_generic_config_runlock(config);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = configuration à mettre à jour.                      *
*                param  = paramètre à intégrer dans la configuration.         *
*                lock   = pose un verrou si ce n'est déjà fait.               *
*                                                                             *
*  Description : Ajoute un paramètre à une configuration.                     *
*                                                                             *
*  Retour      : Validation de l'ajout : true ou false.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _g_generic_config_add_param(GGenConfig *config, GCfgParam *param, bool lock)
{
    bool result;                            /* Bilan à retourner           */
    const char *path;                       /* Chemin d'accès unique       */
    GCfgParam *old;                         /* Test de présence            */

    path = g_config_param_get_path(param);

    if (lock)
        g_generic_config_wlock(config);

    old = _g_generic_config_search(config, path, false);
    if (old != NULL)
    {
        g_object_unref(G_OBJECT(old));
        result = false;
        goto exit;
    }

    g_object_ref(G_OBJECT(param));

    config->params = g_list_append(config->params, param);

    g_signal_connect(param, "modified", G_CALLBACK(on_config_param_modified), config);

    result = true;

 exit:

    if (lock)
        g_generic_config_wunlock(config);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : param  = instance dont le contenu a évolué.                  *
*                config = configuration globalement mise à jour.              *
*                                                                             *
*  Description : Réagit à un changement de valeur pour un paramètre.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_config_param_modified(GCfgParam *param, GGenConfig *config)
{
    g_signal_emit_by_name(config, "modified", param);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = configuration à mettre à jour.                      *
*                path   = chemin d'accès au paramètre visé.                   *
*                                                                             *
*  Description : Retire un paramètre d'une configuration.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_generic_config_delete_param(GGenConfig *config, const char *path)
{
    GCfgParam *old;                         /* Test de présence            */

    g_generic_config_wlock(config);

    old = _g_generic_config_search(config, path, false);

    if (old != NULL)
    {
        g_signal_handlers_disconnect_by_func(old, G_CALLBACK(on_config_param_modified), config);

        config->params = g_list_remove(config->params, old);

        g_object_unref(G_OBJECT(old));
        g_object_unref(G_OBJECT(old));

    }

    g_generic_config_wunlock(config);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : config = configuration à consulter.                          *
*                                                                             *
*  Description : Renvoie la liste des paramètres de configuration.            *
*                                                                             *
*  Retour      : Liste d'éléments à parcourir.                                *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GList *g_generic_config_list_params(const GGenConfig *config)
{
    /**
     * Un verrou doit être posé !
     * Il n'y a pas d'assert() possible pour le vérifier...
     */

    return config->params;

}
