
/* Chrysalide - Outil d'analyse de fichiers binaires
 * scanner.h - prototypes pour le parcours de contenus à la recherche de motifs
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


#ifndef _ANALYSIS_SCAN_RULE_H
#define _ANALYSIS_SCAN_RULE_H


#include <glib-object.h>


#include "cond.h"
#include "context.h"
#include "pattern.h"
#include "expr.h"
#include "patterns/backend.h"
#include "../../common/fnv1a.h"
#include "../../common/szstr.h"



#define G_TYPE_SCAN_RULE            g_scan_rule_get_type()
#define G_SCAN_RULE(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SCAN_RULE, GScanRule))
#define G_IS_SCAN_RULE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SCAN_RULE))
#define G_SCAN_RULE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SCAN_RULE, GScanRuleClass))
#define G_IS_SCAN_RULE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SCAN_RULE))
#define G_SCAN_RULE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SCAN_RULE, GScanRuleClass))


/* Représentation d'une règle de détection statique (instance) */
typedef struct _GScanRule GScanRule;

/* Représentation d'une règle de détection statique (classe) */
typedef struct _GScanRuleClass GScanRuleClass;


/* Indique le type défini pour une règle de détection par motifs. */
GType g_scan_rule_get_type(void);

/* Crée une règle de détection statique à l'aide de motifs. */
GScanRule *g_scan_rule_new(const char *);

/* Indique le nom associé à une règle de détection. */
const char *g_scan_rule_get_name(const GScanRule *, fnv64_t *);

/* Intègre une nouvelle variable locale à une règle. */
void g_scan_rule_add_local_variable(GScanRule *, GSearchPattern *);

/* Fournit une variable locale à une règle selon un nom. */
GSearchPattern *g_scan_rule_get_local_variable(GScanRule *, const char *);

/*  Fournit une liste de variables locales à partir d'un nom. */
GSearchPattern **g_scan_rule_get_local_variables(GScanRule *, const char *, size_t *);

/* Définit l'expression d'une correspondance recherchée. */
void g_scan_rule_set_match_condition(GScanRule *, GScanExpression *);

/* Prépare le suivi de recherche de motifs pour une règle. */
bool g_scan_rule_setup_backend(GScanRule *, GEngineBackend *, GScanContext *);

/* Lance une analyse d'un contenu binaire selon une règle. */
void g_scan_rule_check(GScanRule *, GEngineBackend *, GScanContext *);

/* Affiche une règle au format texte. */
void g_scan_rule_output_to_text(const GScanRule *, GScanContext *, bool, int);

/* Convertit une règle en texte. */
char *g_scan_rule_convert_as_text(const GScanRule *, GScanContext *);

/* Affiche une règle au format JSON. */
void g_scan_rule_output_to_json(const GScanRule *, GScanContext *, const sized_string_t *, unsigned int, int, bool);

/* Convertit une règle en JSON. */
char *g_scan_rule_convert_as_json(const GScanRule *, GScanContext *);



#endif  /* _ANALYSIS_SCAN_RULE_H */
