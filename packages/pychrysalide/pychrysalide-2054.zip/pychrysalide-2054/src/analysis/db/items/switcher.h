
/* Chrysalide - Outil d'analyse de fichiers binaires
 * switcher.h - prototypes pour la gestion des basculements d'affichage d'opérandes numériques
 *
 * Copyright (C) 2015-2020 Cyrille Bagard
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


#ifndef _ANALYSIS_DB_ITEMS_SWITCHER_H
#define _ANALYSIS_DB_ITEMS_SWITCHER_H


#include <glib-object.h>


#include "../../../arch/instruction.h"
#include "../../../arch/operands/immediate.h"



/* --------------------- ELABORATION D'UN ELEMENT DE COLLECTION --------------------- */


#define G_TYPE_DB_SWITCHER            g_db_switcher_get_type()
#define G_DB_SWITCHER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_DB_SWITCHER, GDbSwitcher))
#define G_IS_DB_SWITCHER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_DB_SWITCHER))
#define G_DB_SWITCHER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_DB_SWITCHER, GDbSwitcherClass))
#define G_IS_DB_SWITCHER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_DB_SWITCHER))
#define G_DB_SWITCHER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_DB_SWITCHER, GDbSwitcherClass))


/* Bascule d'affichage pour un opérande numérique (instance) */
typedef struct _GDbSwitcher GDbSwitcher;

/* Bascule d'affichage pour un opérande numérique (classe) */
typedef struct _GDbSwitcherClass GDbSwitcherClass;


/* Indique le type défini pour un signet à l'intérieur d'une zone de texte. */
GType g_db_switcher_get_type(void);

/* Crée une définition de bascule d'affichage pour un immédiat. */
GDbSwitcher *g_db_switcher_new(GArchInstruction *, const GImmOperand *, ImmOperandDisplay);

/* Initialise la définition de bascule d'affichage. */
bool g_db_switcher_fill(GDbSwitcher *, GArchInstruction *, const GImmOperand *, ImmOperandDisplay);

/* Fournit l'adresse associée à une bascule. */
const vmpa2t *g_db_switcher_get_address(const GDbSwitcher *);

/* Fournit le chemin menant vers l'opérande basculé. */
const char *g_db_switcher_get_path(const GDbSwitcher *);

/* Indique l'affichage vers lequel un opérande a basculé. */
ImmOperandDisplay g_db_switcher_get_display(const GDbSwitcher *);



/* ---------------------- DEFINITION DE LA COLLECTION ASSOCIEE ---------------------- */


#define G_TYPE_SWITCHER_COLLECTION            g_switcher_collection_get_type()
#define G_SWITCHER_COLLECTION(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_SWITCHER_COLLECTION, GSwitcherCollection))
#define G_IS_SWITCHER_COLLECTION(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_SWITCHER_COLLECTION))
#define G_SWITCHER_COLLECTION_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_SWITCHER_COLLECTION, GSwitcherCollectionClass))
#define G_IS_SWITCHER_COLLECTION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_SWITCHER_COLLECTION))
#define G_SWITCHER_COLLECTION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_SWITCHER_COLLECTION, GSwitcherCollectionClass))


/* Collection dédiée aux basculements d'affichage (instance) */
typedef struct _GSwitcherCollection GSwitcherCollection;

/* Collection dédiée aux basculements d'affichage (classe) */
typedef struct _GSwitcherCollectionClass GSwitcherCollectionClass;


/* Indique le type défini pour une collection de basculements d'affichage. */
GType g_switcher_collection_get_type(void);

/* Crée une collection dédiée aux basculements d'affichage. */
GSwitcherCollection *g_switcher_collection_new(void);



#endif  /* _ANALYSIS_DB_ITEMS_SWITCH_H */
