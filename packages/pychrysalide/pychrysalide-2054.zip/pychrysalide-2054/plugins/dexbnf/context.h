
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.h - prototypes pour la fourniture de contexte aux phases de décodage Dex
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


#ifndef _PLUGINS_DEXBNF_CONTEXT_H
#define _PLUGINS_DEXBNF_CONTEXT_H


#include <glib-object.h>



#define G_TYPE_DEX_DEMANGLING            g_dex_demangling_get_type()
#define G_DEX_DEMANGLING(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DEX_DEMANGLING, GDexDemangling))
#define G_IS_DEX_DEMANGLING(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DEX_DEMANGLING))
#define G_DEX_DEMANGLING_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DEX_DEMANGLING, GDexDemanglingClass))
#define G_IS_DEX_DEMANGLING_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DEX_DEMANGLING))
#define G_DEX_DEMANGLING_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DEX_DEMANGLING, GDexDemanglingClass))


/* Contexte de décodage Dex (instance) */
typedef struct _GDexDemangling GDexDemangling;

/* Contexte de décodage Dex (classe) */
typedef struct _GDexDemanglingClass GDexDemanglingClass;


/* Indique le type défini pour un contexte de décodage Dex. */
GType g_dex_demangling_get_type(void);



#endif  /* _PLUGINS_DEXBNF_CONTEXT_H */
