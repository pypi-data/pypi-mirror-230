
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.h - prototypes pour les instances d'actions d'un greffon donné
 *
 * Copyright (C) 2010-2016 Cyrille Bagard
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


#ifndef _PLUGINS_CONTEXT_H
#define _PLUGINS_CONTEXT_H


#include <glib-object.h>



/* Instance de greffon pour Chrysalide (instance) */
typedef struct _GPluginContext GPluginContext;

/* Instance de greffon pour Chrysalide (classe) */
typedef struct _GPluginContextClass GPluginContextClass;


#define G_TYPE_PLUGIN_CONTEXT                (g_plugin_context_get_type())
#define G_PLUGIN_CONTEXT(obj)                (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_PLUGIN_CONTEXT, GPluginContext))
#define G_IS_PLUGIN_CONTEXT(obj)             (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_PLUGIN_CONTEXT))
#define G_PLUGIN_CONTEXT_CLASS(klass)        (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_PLUGIN_CONTEXT, GPluginContextClass))
#define G_IS_PLUGIN_CONTEXT_CLASS(klass)     (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_PLUGIN_CONTEXT))
#define G_PLUGIN_CONTEXT_GET_CLASS(obj)      (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_PLUGIN_CONTEXT, GPluginContextClass))


/* Indique le type défini pour une instance de greffon. */
GType g_plugin_context_get_type(void);



#endif  /* _PLUGINS_CONTEXT_H */
