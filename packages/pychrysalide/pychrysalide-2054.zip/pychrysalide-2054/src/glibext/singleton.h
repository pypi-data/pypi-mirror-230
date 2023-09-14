
/* Chrysalide - Outil d'analyse de fichiers binaires
 * singleton.h - prototypes pour la réduction du nombre d'instances d'un même type
 *
 * Copyright (C) 2021 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _GLIBEXT_SINGLETON_H
#define _GLIBEXT_SINGLETON_H


#include <glib-object.h>
#include <stdbool.h>



/* Définition d'un compacteur d'instances de types (instance) */
typedef struct _GSingletonFactory GSingletonFactory;



/* ------------------ INTERFACE POUR CANDIDAT A UNE CENTRALISATION ------------------ */


#define G_TYPE_SINGLETON_CANDIDATE             (g_singleton_candidate_get_type())
#define G_SINGLETON_CANDIDATE(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SINGLETON_CANDIDATE, GSingletonCandidate))
#define G_SINGLETON_CANDIDATE_CLASS(vtable)    (G_TYPE_CHECK_CLASS_CAST((vtable), G_TYPE_SINGLETON_CANDIDATE, GSingletonCandidateIface))
#define G_IS_SINGLETON_CANDIDATE(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SINGLETON_CANDIDATE))
#define G_IS_SINGLETON_CANDIDATE_CLASS(vtable) (G_TYPE_CHECK_CLASS_TYPE((vtable), G_TYPE_SINGLETON_CANDIDATE))
#define G_SINGLETON_CANDIDATE_GET_IFACE(inst)  (G_TYPE_INSTANCE_GET_INTERFACE((inst), G_TYPE_SINGLETON_CANDIDATE, GSingletonCandidateIface))


/* Instance d'objet visant à être unique (coquille vide) */
typedef struct _GSingletonCandidate GSingletonCandidate;

/* Instance d'objet visant à être unique (interface) */
typedef struct _GSingletonCandidateIface GSingletonCandidateIface;


/* Détermine le type d'une interface pour la lecture de binaire. */
GType g_singleton_candidate_get_type(void) G_GNUC_CONST;

/* Fournit une liste de candidats embarqués par un candidat. */
GSingletonCandidate **g_singleton_candidate_list_inner_instances(const GSingletonCandidate *, size_t *);

/* Fournit l'empreinte d'un candidat à une centralisation. */
guint g_singleton_candidate_hash(GSingletonCandidate *);

/* Détermine si deux candidats à l'unicité sont identiques. */
gboolean g_singleton_candidate_is_equal(GSingletonCandidate *, GSingletonCandidate *);

/* Marque un candidat comme figé. */
void g_singleton_candidate_set_read_only(GSingletonCandidate *);

/* Indique si le candidat est figé. */
bool g_singleton_candidate_is_read_only(const GSingletonCandidate *);



/* ------------------------- COLLECTION D'INSTANCES UNIQUES ------------------------- */


#define G_TYPE_SINGLETON_FACTORY            g_singleton_factory_get_type()
#define G_SINGLETON_FACTORY(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SINGLETON_FACTORY, GSingletonFactory))
#define G_IS_SINGLETON_FACTORY(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SINGLETON_FACTORY))
#define G_SINGLETON_FACTORY_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SINGLETON_FACTORY, GSingletonFactoryClass))
#define G_IS_SINGLETON_FACTORY_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SINGLETON_FACTORY))
#define G_SINGLETON_FACTORY_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SINGLETON_FACTORY, GSingletonFactoryClass))


/* Définition d'un compacteur d'instances de types (classe) */
typedef struct _GSingletonFactoryClass GSingletonFactoryClass;


/* Indique le type défini pour une mémoire de types d'objets. */
GType g_singleton_factory_get_type(void);

/* Crée un compacteur d'instances de types. */
GSingletonFactory *g_singleton_factory_new(void);

/* Fournit l'instance unique correspondant à un objet. */
GSingletonCandidate *g_singleton_factory_get_instance(GSingletonFactory *, GSingletonCandidate *);



#endif  /* _GLIBEXT_SINGLETON_H */
