
/* Chrysalide - Outil d'analyse de fichiers binaires
 * plugin-def.h - prototypes pour les définitions de base utiles aux greffons
 *
 * Copyright (C) 2009-2019 Cyrille Bagard
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _PLUGINS_PLUGIN_DEF_H
#define _PLUGINS_PLUGIN_DEF_H


#include <gmodule.h>
#include <stdbool.h>
#include <stdint.h>



/* ------------------------ IDENTIFICATION DE COMPATIBILITES ------------------------ */


/* Version identifiant les définitions courantes */
typedef uint32_t plugin_abi_version_t;

#define DEFINE_PLUGIN_ABI_VERSION(maj, min, rev) \
    (((maj & 0xff) << 24) | ((min & 0xff) << 16) | (rev & 0xffff))

#define GET_ABI_MAJ_VERSION(vs) ((vs >> 24) & 0xff)
#define GET_ABI_MIN_VERSION(vs) ((vs >> 16) & 0xff)
#define GET_ABI_REV_VERSION(vs) (vs & 0xffff)

#define CURRENT_ABI_VERSION DEFINE_PLUGIN_ABI_VERSION(0, 3, 0)



/* ------------------------- DEFINITION D'UN PROJET INTERNE ------------------------- */


/* Idenifiant d'une action menée */
typedef uint32_t plugin_action_t;

#define DEFINE_PLUGIN_CATEGORY(cat) ((cat & 0xff) << 24)
#define DEFINE_PLUGIN_SUB_CATEGORY(sub) ((sub & 0xff) << 16)
#define DEFINE_PLUGIN_ACTION(a) (a & 0xffff)

#define GET_PLUGIN_CATEGORY(val) ((val >> 24) & 0xff)
#define GET_PLUGIN_SUB_CATEGORY(val) ((val >> 16) & 0xff)

#define MASK_PLUGIN_CATEGORY(val) (val & (0xff << 24))
#define MASK_PLUGIN_SUB_CATEGORY(val) (val & (0xff << 16))


#define DPC_BASIC               DEFINE_PLUGIN_CATEGORY(0)
#define DPC_GUI                 DEFINE_PLUGIN_CATEGORY(1)
#define DPC_BINARY_PROCESSING   DEFINE_PLUGIN_CATEGORY(2)

/* DPC_BASIC */

#define DPS_NONE                DEFINE_PLUGIN_SUB_CATEGORY(0)
#define DPS_PG_MANAGEMENT       DEFINE_PLUGIN_SUB_CATEGORY(1)
#define DPS_CORE_MANAGEMENT     DEFINE_PLUGIN_SUB_CATEGORY(2)

/* DPC_GUI */

#define DPS_SETUP               DEFINE_PLUGIN_SUB_CATEGORY(0)
#define DPS_RUNNING             DEFINE_PLUGIN_SUB_CATEGORY(1)

/* DPC_BINARY_PROCESSING */

#define DPS_CONTENT             DEFINE_PLUGIN_SUB_CATEGORY(0)
#define DPS_FORMAT              DEFINE_PLUGIN_SUB_CATEGORY(1)
#define DPS_DISASSEMBLY         DEFINE_PLUGIN_SUB_CATEGORY(2)
#define DPS_DETECTION           DEFINE_PLUGIN_SUB_CATEGORY(3)

// GUI -> project
// binary loaded
// binary unload

// GUI -> dialog box



/* Action(s) menée(s) par un greffon */
typedef enum _PluginAction
{
    /**
     * DPC_BASIC | DPS_NONE
     */

    /* Aucun intérêt */
    PGA_BASIC_NONE = DPC_BASIC | DPS_NONE | DEFINE_PLUGIN_ACTION(0),

    /**
     * DPC_BASIC | DPS_PG_MANAGEMENT
     */

    /* Chargement */
    PGA_PLUGIN_INIT   = DPC_BASIC | DPS_PG_MANAGEMENT | DEFINE_PLUGIN_ACTION(0),

    /* Chargement des paramètres  */
    PGA_PLUGIN_LOADED = DPC_BASIC | DPS_PG_MANAGEMENT | DEFINE_PLUGIN_ACTION(1),

    /* Déchargement */
    PGA_PLUGIN_EXIT   = DPC_BASIC | DPS_PG_MANAGEMENT | DEFINE_PLUGIN_ACTION(2),

    /**
     * DPC_BASIC | DPS_CORE_MANAGEMENT
     */

    /* Fin du chargement des greffons natifs */
    PGA_NATIVE_PLUGINS_LOADED = DPC_BASIC | DPS_CORE_MANAGEMENT | DEFINE_PLUGIN_ACTION(0),

    /* Fin du chargement de tous greffons */
    PGA_ALL_PLUGINS_LOADED    = DPC_BASIC | DPS_CORE_MANAGEMENT | DEFINE_PLUGIN_ACTION(1),

    /* Mise en place de type à partir de code externe */
    PGA_TYPE_BUILDING         = DPC_BASIC | DPS_CORE_MANAGEMENT | DEFINE_PLUGIN_ACTION(2),

    /**
     * DPC_GUI | DPS_SETUP
     */

    /* Inclusion de thèmes */
    PGA_GUI_THEME = DPC_GUI | DPS_SETUP | DEFINE_PLUGIN_ACTION(0),

    /**
     * DPC_GUI | DPS_RUNNING
     */

    /* Accrochage / décrochage de panneaux */
    PGA_PANEL_CREATION = DPC_GUI | DPS_RUNNING | DEFINE_PLUGIN_ACTION(0),

    /* Accrochage / décrochage de panneaux */
    PGA_PANEL_DOCKING = DPC_GUI | DPS_RUNNING | DEFINE_PLUGIN_ACTION(1),

    /**
     * DPC_BINARY_PROCESSING | DPS_CONTENT
     */

    /* Exploration de contenus binaires */
    PGA_CONTENT_EXPLORER = DPC_BINARY_PROCESSING | DPS_CONTENT | DEFINE_PLUGIN_ACTION(0),

    /* Conversion de contenus binaires en contenus chargés */
    PGA_CONTENT_RESOLVER = DPC_BINARY_PROCESSING | DPS_CONTENT | DEFINE_PLUGIN_ACTION(1),

    /* Intervention en toute fin d'analyse de contenu chargé */
    PGA_CONTENT_ANALYZED = DPC_BINARY_PROCESSING | DPS_CONTENT | DEFINE_PLUGIN_ACTION(2),

    /**
     * DPC_BINARY_PROCESSING | DPS_FORMAT
     */

    /* Début de l'analyse d'un format */
    PGA_FORMAT_ANALYSIS_STARTED      = DPC_BINARY_PROCESSING | DPS_FORMAT | DEFINE_PLUGIN_ACTION(0),

    /* Accompagnement du chargement */
    PGA_FORMAT_PRELOAD               = DPC_BINARY_PROCESSING | DPS_FORMAT | DEFINE_PLUGIN_ACTION(1),

    /* Accompagnement du chargement */
    PGA_FORMAT_ATTACH_DEBUG          = DPC_BINARY_PROCESSING | DPS_FORMAT | DEFINE_PLUGIN_ACTION(2),

    /* Fin de l'analyse d'un format */
    PGA_FORMAT_ANALYSIS_ENDED        = DPC_BINARY_PROCESSING | DPS_FORMAT | DEFINE_PLUGIN_ACTION(3),

    /* Début de la vague finale d'analyse d'un format */
    PGA_FORMAT_POST_ANALYSIS_STARTED = DPC_BINARY_PROCESSING | DPS_FORMAT | DEFINE_PLUGIN_ACTION(4),

    /* Fin de la vague finale d'analyse d'un format */
    PGA_FORMAT_POST_ANALYSIS_ENDED   = DPC_BINARY_PROCESSING | DPS_FORMAT | DEFINE_PLUGIN_ACTION(5),

    /**
     * DPC_BINARY_PROCESSING | DPS_DISASSEMBLY
     */

    /* Désassemblage démarré */
    PGA_DISASSEMBLY_STARTED     = DPC_BINARY_PROCESSING | DPS_DISASSEMBLY | DEFINE_PLUGIN_ACTION(0),

    /* Instructions toutes jutes désassemblées */
    PGA_DISASSEMBLY_RAW         = DPC_BINARY_PROCESSING | DPS_DISASSEMBLY | DEFINE_PLUGIN_ACTION(1),

    /* Crochets de type 'link' exécutés */
    PGA_DISASSEMBLY_HOOKED_LINK = DPC_BINARY_PROCESSING | DPS_DISASSEMBLY | DEFINE_PLUGIN_ACTION(2),

    /* Crochets de type 'post' exécutés */
    PGA_DISASSEMBLY_HOOKED_POST = DPC_BINARY_PROCESSING | DPS_DISASSEMBLY | DEFINE_PLUGIN_ACTION(3),

    /* Limites de routines définies */
    PGA_DISASSEMBLY_LIMITED     = DPC_BINARY_PROCESSING | DPS_DISASSEMBLY | DEFINE_PLUGIN_ACTION(4),

    /* Détection d'éventuelles boucles effectuée */
    PGA_DISASSEMBLY_LOOPS       = DPC_BINARY_PROCESSING | DPS_DISASSEMBLY | DEFINE_PLUGIN_ACTION(5),

    /* Liaisons entre instructions mises en place */
    PGA_DISASSEMBLY_LINKED      = DPC_BINARY_PROCESSING | DPS_DISASSEMBLY | DEFINE_PLUGIN_ACTION(6),

    /* Instructions regroupées en blocs basiques */
    PGA_DISASSEMBLY_GROUPED     = DPC_BINARY_PROCESSING | DPS_DISASSEMBLY | DEFINE_PLUGIN_ACTION(7),

    /* Définitions de profondeurs d'exécution */
    PGA_DISASSEMBLY_RANKED      = DPC_BINARY_PROCESSING | DPS_DISASSEMBLY | DEFINE_PLUGIN_ACTION(8),

    /* Désassemblage fini */
    PGA_DISASSEMBLY_ENDED       = DPC_BINARY_PROCESSING | DPS_DISASSEMBLY | DEFINE_PLUGIN_ACTION(9),

    /**
     * DPC_BINARY_PROCESSING | DPS_DETECTION
     */

    /* Intervention en toute fin d'analyse de contenu chargé */
    PGA_DETECTION_OBFUSCATORS = DPC_BINARY_PROCESSING | DPS_DETECTION | DEFINE_PLUGIN_ACTION(0),

} PluginAction;



/* ------------------------ PREMIER INTERFACAGE PROTOCOLAIRE ------------------------ */


#define CHRYSALIDE_PLUGIN_MAGIC 0xdeadc0de1234abcdull


/* Définition d'un greffon */
typedef struct _plugin_interface
{
    uint64_t magic;                         /* Vérification a minima       */
    plugin_abi_version_t abi_version;       /* Version du protocole utilisé*/

    /**
     * Les champs suivants ne sont généralement pas alloués dynamiquement,
     * car issus des données des greffons natifs.
     *
     * Dans le cas des autres types d'extensions (par exemple ceux en Python),
     * les éléments sont construits à la volée, donc à libérer après usage.
     */

    char *gtp_name;                         /* Désignation du GType associé*/
    char *name;                             /* Désignation humaine courte  */
    char *desc;                             /* Description plus loquace    */
    char *version;                          /* Version du greffon          */
    char *url;                              /* Site Web associé            */

    bool container;                         /* Mise en place de greffons ? */

    char **required;                        /* Pré-chargements requis      */
    size_t required_count;                  /* Quantité de ces dépendances */

    plugin_action_t *actions;               /* Liste des actions gérées    */
    size_t actions_count;                   /* Quantité de ces actions     */

} plugin_interface;



#endif  /* _PLUGINS_PLUGIN_DEF_H */
