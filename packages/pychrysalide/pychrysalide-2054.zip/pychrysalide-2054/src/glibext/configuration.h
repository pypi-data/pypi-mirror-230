
/* Chrysalide - Outil d'analyse de fichiers binaires
 * configuration.h - prototypes pour les éléments de configuration du programme
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


#ifndef _GLIBEXT_CONFIGURATION_H
#define _GLIBEXT_CONFIGURATION_H


#include <glib-object.h>
#include <stdbool.h>
#ifdef INCLUDE_GTK_SUPPORT
#   include <gdk/gdk.h>
#endif


#if !defined(INCLUDE_GTK_SUPPORT) && !defined(HOMEMADE_RGBA)

#   define HOMEMADE_RGBA

/**
 * Copie depuis /usr/include/gtk-3.0/gdk/gdkrgba.h
 */
typedef struct _GdkRGBA
{
    gdouble red;
    gdouble green;
    gdouble blue;
    gdouble alpha;

} GdkRGBA;

#endif



/* ---------------------------- ELEMENT DE CONFIGURATION ---------------------------- */


/* Types de valeur pour élement de configuration */
typedef enum _ConfigParamType
{
    CPT_BOOLEAN,                            /* Valeur booléenne            */
    CPT_INTEGER,                            /* Valeur entière              */
    CPT_ULONG,                              /* Valeur entière positive     */
    CPT_STRING,                             /* Chaîne de caractère         */
    CPT_COLOR,                              /* Couleur avec transparence   */

    CPT_COUNT

} ConfigParamType;


/* Liste dess états d'un paramètre de configuration */
typedef enum _ConfigParamState
{
    CPS_UNDEFINED = (0 << 0),               /* Etat non déterminé          */
    CPS_CHANGED   = (1 << 0),               /* Modification utilisateur    */
    CPS_DEFAULT   = (1 << 1),               /* Valeur par défaut           */
    CPS_EMPTY     = (1 << 2)                /* Valeur vide                 */

} ConfigParamState;


#define G_TYPE_CFG_PARAM                (g_config_param_get_type())
#define G_CFG_PARAM(obj)                (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_CFG_PARAM, GCfgParam))
#define G_IS_CFG_PARAM(obj)             (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_CFG_PARAM))
#define G_CFG_PARAM_CLASS(klass)        (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_CFG_PARAM, GCfgParamClass))
#define G_IS_CFG_PARAM_CLASS(klass)     (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_CFG_PARAM))
#define G_CFG_PARAM_GET_CLASS(obj)      (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_CFG_PARAM, GCfgParamClass))


/* Configuration générique quelconque (instance) */
typedef struct _GCfgParam GCfgParam;

/* Configuration générique quelconque (classe) */
typedef struct _GCfgParamClass GCfgParamClass;


/* Indique le type défini par la GLib pour les configurations génériques. */
GType g_config_param_get_type(void);

/* Crée un paramètre de configuration. */
GCfgParam *g_config_param_new(const char *, ConfigParamType, ...);

/* Crée un paramètre de configuration sans valeur. */
GCfgParam *g_config_param_new_empty(const char *, ConfigParamType);

/* Etablit une comparaison selon un chemin d'accès. */
gint g_config_param_compare(const GCfgParam *, const GCfgParam *);

/* Indique le chemin d'accès utilisé pour un paramètre. */
const char *g_config_param_get_path(const GCfgParam *);

/* Indique le type de valeur utilisée par un paramètre. */
ConfigParamType g_config_param_get_ptype(const GCfgParam *);

/* Indique le statut d'une valeur utilisée par un paramètre. */
ConfigParamState g_config_param_get_state(GCfgParam *);

/* Efface toute valeur courante d'un paramètre de configuration. */
void g_config_param_make_empty(GCfgParam *);

/* Réinitialise la valeur d'un paramètre de configuration. */
void g_config_param_reset(GCfgParam *);

/* Modifie la valeur courante d'un paramètre de configuration. */
void g_config_param_set_value(GCfgParam *, ...);

/* Indique la valeur courante d'un paramètre de configuration. */
void g_config_param_get_value(const GCfgParam *, ...);



/* --------------------- PARTIES IMPREVISIBLES DE CONFIGURATION --------------------- */


#define G_TYPE_CFG_GROUP                (g_config_group_get_type())
#define G_CFG_GROUP(obj)                (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_CFG_GROUP, GCfgGroup))
#define G_IS_CFG_GROUP(obj)             (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_CFG_GROUP))
#define G_CFG_GROUP_CLASS(klass)        (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_CFG_GROUP, GCfgGroupClass))
#define G_IS_CFG_GROUP_CLASS(klass)     (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_CFG_GROUP))
#define G_CFG_GROUP_GET_CLASS(obj)      (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_CFG_GROUP, GCfgGroupClass))


/* Groupe de paramètres non fixés à l'avance (instance) */
typedef struct _GCfgGroup GCfgGroup;

/* Groupe de paramètres non fixés à l'avance (classe) */
typedef struct _GCfgGroupClass GCfgGroupClass;


/* Indique le type défini par la GLib pour les groupes de paramètres non prévisibiles. */
GType g_config_group_get_type(void);

/* Crée un groupe de paramètres de configuration. */
GCfgGroup *g_config_group_new(const char *, ConfigParamType);



/* ----------------------- GESTION GENERIQUE DE CONFIGURATION ----------------------- */


#define G_TYPE_GEN_CONFIG                (g_generic_config_get_type())
#define G_GEN_CONFIG(obj)                (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_GEN_CONFIG, GGenConfig))
#define G_IS_GEN_CONFIG(obj)             (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_GEN_CONFIG))
#define G_GEN_CONFIG_CLASS(klass)        (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_GEN_CONFIG, GGenConfigClass))
#define G_IS_GEN_CONFIG_CLASS(klass)     (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_GEN_CONFIG))
#define G_GEN_CONFIG_GET_CLASS(obj)      (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_GEN_CONFIG, GGenConfigClass))


/* Configuration générique quelconque (instance) */
typedef struct _GGenConfig GGenConfig;

/* Configuration générique quelconque (classe) */
typedef struct _GGenConfigClass GGenConfigClass;


/* Indique le type défini par la GLib pour les configurations génériques. */
GType g_generic_config_get_type(void);

/* Crée un gestionnaire configuration générique. */
GGenConfig *g_generic_config_new(void);

/* Crée un gestionnaire configuration générique. */
GGenConfig *g_generic_config_new_from_file(const char *);

/* Indique le fichier utilisé pour l'enregistrement XML. */
const char *g_generic_config_get_filename(const GGenConfig *);

/* Met à disposition un encadrement des accès aux paramètres. */
void g_generic_config_lock_unlock(GGenConfig *, bool, bool);


#define g_generic_config_wlock(cfg) g_generic_config_lock_unlock(cfg, true, true);
#define g_generic_config_wunlock(cfg) g_generic_config_lock_unlock(cfg, true, false);

#define g_generic_config_rlock(cfg) g_generic_config_lock_unlock(cfg, false, true);
#define g_generic_config_runlock(cfg) g_generic_config_lock_unlock(cfg, false, false);


/* Lit la configuration depuis un fichier. */
bool g_generic_config_read(GGenConfig *);

/* Ecrit la configuration dans un fichier. */
bool g_generic_config_write(GGenConfig *);

/* Ajoute la définition d'un groupe à une configuration. */
void g_generic_config_add_group(GGenConfig *, GCfgGroup *);


#define g_generic_config_create_group(c, p, t)                  \
    ({                                                          \
        GCfgGroup *__group;                                     \
        __group = g_config_group_new(p, t);                     \
        g_generic_config_add_group(c, __group);                 \
        g_object_unref(G_OBJECT(__group));                      \
    })


/* Retrouve un élément de configuration par son chemin. */
GCfgParam *_g_generic_config_search(GGenConfig *, const char *, bool);


#define g_generic_config_search(cfg, p) _g_generic_config_search(cfg, p, true)

#define g_generic_config_set_value(c, p, v)                     \
    ({                                                          \
        GCfgParam *__param;                                     \
        __param = g_generic_config_search(c, p);                \
        if (__param != NULL)                                    \
        {                                                       \
            g_config_param_set_value(__param, v);               \
            g_object_unref(G_OBJECT(__param));                  \
        }                                                       \
        __param != NULL ? true : false;                         \
    })

#define g_generic_config_get_value(c, p, v)                     \
    ({                                                          \
        GCfgParam *__param;                                     \
        __param = g_generic_config_search(c, p);                \
        if (__param != NULL)                                    \
        {                                                       \
            g_config_param_get_value(__param, v);               \
            g_object_unref(G_OBJECT(__param));                  \
        }                                                       \
        __param != NULL ? true : false;                         \
    })


/* Ajoute un paramètre à une configuration. */
bool _g_generic_config_add_param(GGenConfig *, GCfgParam *, bool);


#define g_generic_config_add_param(c, p) _g_generic_config_add_param(c, p, true)

#define g_generic_config_create_param(c, p, t, d)               \
    ({                                                          \
        bool __result;                                          \
        GCfgParam *__param;                                     \
        __param = g_config_param_new(p, t, d);                  \
        __result = g_generic_config_add_param(c, __param);      \
        g_object_unref(G_OBJECT(__param));                      \
        __result;                                               \
    })


#define g_generic_config_create_param_if_not_exist(c, p, t, d)  \
    ({                                                          \
        bool __result;                                          \
        GCfgParam *__param;                                     \
        __param = g_generic_config_search(c, p);                \
        if (__param == NULL)                                    \
        {                                                       \
            __param = g_config_param_new(p, t, d);              \
            __result = g_generic_config_add_param(c, __param);  \
        }                                                       \
        else                                                    \
            __result = true;                                    \
        g_object_unref(G_OBJECT(__param));                      \
        __result;                                               \
    })


#define g_generic_config_create_or_udpdate_param(c, p, t, d, v) \
    ({                                                          \
        bool __result;                                          \
        GCfgParam *__param;                                     \
        __param = g_generic_config_search(c, p);                \
        if (__param == NULL)                                    \
        {                                                       \
            __param = g_config_param_new(p, t, d);              \
            __result = g_generic_config_add_param(c, __param);  \
        }                                                       \
        else                                                    \
            __result = true;                                    \
        g_config_param_set_value(__param, v);                   \
        g_object_unref(G_OBJECT(__param));                      \
        __result;                                               \
    })


/* Retire un paramètre d'une configuration. */
void g_generic_config_delete_param(GGenConfig *, const char *);

/* Renvoie la liste des paramètres de configuration. */
GList *g_generic_config_list_params(const GGenConfig *);



#endif  /* _GLIBEXT_CONFIGURATION_H */
