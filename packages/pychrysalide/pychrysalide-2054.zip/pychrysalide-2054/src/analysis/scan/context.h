
/* Chrysalide - Outil d'analyse de fichiers binaires
 * context.h - prototypes pour le suivi d'analyses via contextes
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#ifndef _ANALYSIS_SCAN_CONTEXT_H
#define _ANALYSIS_SCAN_CONTEXT_H


#include <glib-object.h>


#include "match.h"
#include "options.h"
#include "../content.h"



/* Depuis expr.h : expression d'évaluation généraliste (instance) */
typedef struct _GScanExpression GScanExpression;


#define G_TYPE_SCAN_CONTEXT            g_scan_context_get_type()
#define G_SCAN_CONTEXT(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_CONTEXT, GScanContext))
#define G_IS_SCAN_CONTEXT(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_CONTEXT))
#define G_SCAN_CONTEXT_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_CONTEXT, GScanContextClass))
#define G_IS_SCAN_CONTEXT_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_CONTEXT))
#define G_SCAN_CONTEXT_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_CONTEXT, GScanContextClass))


/* Contexte de suivi d'une analyse en cours (instance) */
typedef struct _GScanContext GScanContext;

/* Contexte de suivi d'une analyse en cours (classe) */
typedef struct _GScanContextClass GScanContextClass;


/* Identifiant de motif intégré */
typedef uint64_t patid_t;

#define INVALID_PATTERN_ID 0xffffffffffffffff


/* Indique le type défini pour un contexte de suivi d'analyse. */
GType g_scan_context_get_type(void);

/* Définit un contexte pour suivi d'analyse. */
GScanContext *g_scan_context_new(GScanOptions *);

/* Fournit l'ensemble des options à respecter pour les analyses. */
GScanOptions *g_scan_context_get_options(const GScanContext *);

/* Fournit un identifiant unique pour un motif recherché. */
patid_t g_scan_context_get_new_pattern_id(GScanContext *);

/* Définit le contenu principal à analyser. */
void g_scan_context_set_content(GScanContext *, GBinContent *);

/* Fournit une référence au contenu principal analysé. */
GBinContent *g_scan_context_get_content(const GScanContext *);

/* Indique si la phase d'analyse de contenu est terminée. */
bool g_scan_context_is_scan_done(const GScanContext *);

/* Note que la phase d'analyse de contenu est terminée. */
void g_scan_context_mark_scan_as_done(GScanContext *);

/* Enregistre une correspondance partielle dans un contenu. */
void g_scan_context_register_atom_match(GScanContext *, patid_t, phys_t);

/* Retourne tous les correspondances partielles notées. */
const phys_t *g_scan_context_get_atom_matches(const GScanContext *, patid_t, size_t *);

/* Enregistre une correspondance complète avec un contenu. */
void g_scan_context_register_full_match(GScanContext *, GScanMatch *);

/* Fournit la liste de toutes les correspondances d'un motif. */
const GScanMatch **g_scan_context_get_full_matches(const GScanContext *, const GSearchPattern *, size_t *);

/* Intègre une condition de correspondance pour règle. */
bool g_scan_context_set_rule_condition(GScanContext *, const char *, GScanExpression *);

/* Indique si un nom donné correspond à une règle. */
bool g_scan_context_has_rule_for_name(const GScanContext *, const char *);

/* Indique si une correspondance globale a pu être établie. */
bool g_scan_context_has_match_for_rule(GScanContext *, const char *);



#endif  /* _ANALYSIS_SCAN_CONTEXT_H */
