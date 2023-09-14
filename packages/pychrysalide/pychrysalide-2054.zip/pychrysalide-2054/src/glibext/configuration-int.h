
/* Chrysalide - Outil d'analyse de fichiers binaires
 * configuration-int.h - accès interne aux éléments de configuration du programme
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _GLIBEXT_CONFIGURATION_INT_H
#define _GLIBEXT_CONFIGURATION_INT_H


#include "configuration.h"


#include "../common/fnv1a.h"



/* ---------------------------- ELEMENT DE CONFIGURATION ---------------------------- */


/* Valeurs supportées par les paramètres */
typedef union _param_value
{
    bool boolean;                           /* Valeur booléenne            */
    int integer;                            /* Valeur entière              */
    unsigned long ulong;                    /* Valeur entière positive     */
    char *string;                           /* Chaîne de caractères        */
    GdkRGBA color;                          /* Couleur avec transparence   */

} param_value;

/* Configuration générique quelconque (instance) */
struct _GCfgParam
{
    GObject parent;                         /* A laisser en premier        */

    char *path;                             /* Chemin d'accès XML          */
    fnv64_t hash;                           /* Empreinte pour accès rapide */

    ConfigParamType type;                   /* Type de valeur              */

    ConfigParamState cached_state;          /* Etat du paramétrage         */

    param_value def;                        /* Valeur par défaut           */
    bool def_empty;                         /* Non défini par défaut ?     */
    param_value cur;                        /* Valeur courante             */
    bool cur_empty;                         /* Actuellement non défini ?   */

};

/* Configuration générique quelconque (classe) */
struct _GCfgParamClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    /* Signaux */

    void (* modified) (GCfgParam *);

};


/* Construit un paramètre de configuration. */
void g_config_param_build(GCfgParam *, const char *, ConfigParamType, const param_value *);

/* Construit un paramètre de configuration sans valeur. */
void g_config_param_build_empty(GCfgParam *, const char *, ConfigParamType);



/* ----------------------- GESTION GENERIQUE DE CONFIGURATION ----------------------- */


/* Configuration générique quelconque (instance) */
struct _GGenConfig
{
    GObject parent;                         /* A laisser en premier        */

    char *filename;                         /* CHemin d'accès complet      */

    GList *groups;                          /* Groupes d'éléments non fixés*/
    GList *params;                          /* Eléments de configuration   */
    GRWLock params_access;                  /* Verrou de protection        */

};

/* Configuration générique quelconque (classe) */
struct _GGenConfigClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    /* Signaux */

    void (* modified) (GGenConfig *, GCfgParam *);

};


/* Crée un gestionnaire configuration générique. */
void g_generic_config_build(GGenConfig *, const char *);



#endif  /* _GLIBEXT_CONFIGURATION_INT_H */
