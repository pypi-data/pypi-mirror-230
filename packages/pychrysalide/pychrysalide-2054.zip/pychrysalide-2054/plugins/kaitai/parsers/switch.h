
/* Chrysalide - Outil d'analyse de fichiers binaires
 * switch.h - prototypes pour la gestion des énumérations Kaitai
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


#ifndef _PLUGINS_KAITAI_PARSERS_SWITCH_H
#define _PLUGINS_KAITAI_PARSERS_SWITCH_H


#include <glib-object.h>


#include <plugins/yaml/node.h>


#include "attribute.h"



#define G_TYPE_KAITAI_SWITCH            g_kaitai_switch_get_type()
#define G_KAITAI_SWITCH(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_KAITAI_SWITCH, GKaitaiSwitch))
#define G_IS_KAITAI_SWITCH(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_KAITAI_SWITCH))
#define G_KAITAI_SWITCH_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_KAITAI_SWITCH, GKaitaiSwitchClass))
#define G_IS_KAITAI_SWITCH_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_KAITAI_SWITCH))
#define G_KAITAI_SWITCH_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_KAITAI_SWITCH, GKaitaiSwitchClass))


/* Sélection d'un type selon un contexte (instance) */
typedef struct _GKaitaiSwitch GKaitaiSwitch;

/* Sélection d'un type selon un contexte (classe) */
typedef struct _GKaitaiSwitchClass GKaitaiSwitchClass;


/* Indique le type défini pour un choix dynamique de type Kaitai. */
GType g_kaitai_switch_get_type(void);

/* Construit une sélection dynamique de type Kaitai. */
GKaitaiSwitch *g_kaitai_switch_new(GYamlNode *, GKaitaiAttribute *);



#endif  /* _PLUGINS_KAITAI_PARSERS_SWITCH_H */
