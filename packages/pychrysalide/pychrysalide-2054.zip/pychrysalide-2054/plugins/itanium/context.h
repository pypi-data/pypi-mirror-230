
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.h - prototypes pour le contexte de décodage à la sauce ABI C++ Itanium
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


#ifndef _PLUGINS_ITANIUM_CONTEXT_H
#define _PLUGINS_ITANIUM_CONTEXT_H


#include <glib-object.h>
#include <stdbool.h>


#include "component.h"



#define G_TYPE_ITANIUM_DEMANGLING            g_itanium_demangling_get_type()
#define G_ITANIUM_DEMANGLING(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_ITANIUM_DEMANGLING, GItaniumDemangling))
#define G_IS_ITANIUM_DEMANGLING(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_ITANIUM_DEMANGLING))
#define G_ITANIUM_DEMANGLING_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_ITANIUM_DEMANGLING, GItaniumDemanglingClass))
#define G_IS_ITANIUM_DEMANGLING_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_ITANIUM_DEMANGLING))
#define G_ITANIUM_DEMANGLING_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_ITANIUM_DEMANGLING, GItaniumDemanglingClass))


/* Contexte de décodage Itanium (instance) */
typedef struct _GItaniumDemangling GItaniumDemangling;

/* Contexte de décodage Itanium (classe) */
typedef struct _GItaniumDemanglingClass GItaniumDemanglingClass;


/* Indique le type défini pour un contexte de décodage. */
GType g_itanium_demangling_get_type(void);

/* Sauvegarde d'un état courant */
typedef struct _itd_state
{
    size_t pos;                             /* Position courante           */
    size_t targs_count;                     /* Quantité utilisée           */
    size_t subst_count;                     /* Nombre de substitutions     */

} itd_state;

/* Fournit l'état courant à une fin de retour en arrière. */
void g_itanium_demangling_push_state(const GItaniumDemangling *, itd_state *);

/* Définit l'état courant suite à un retour en arrière. */
void g_itanium_demangling_pop_state(GItaniumDemangling *, const itd_state *);

/* Indexe un composant représentant un argument de modèle. */
void g_itanium_demangling_add_template_args(GItaniumDemangling *, itanium_component *);

/* Fournit un composant représentant un argument de modèle. */
itanium_component *g_itanium_demangling_get_template_arg(GItaniumDemangling *, size_t);

/* Indexe un composant comme future substitution potentielle. */
void g_itanium_demangling_add_substitution(GItaniumDemangling *, itanium_component *);

/* Fournit un composant en place pour une substitution. */
itanium_component *g_itanium_demangling_get_substitution(GItaniumDemangling *, size_t);



#endif  /* _PLUGINS_ITANIUM_CONTEXT_H */
