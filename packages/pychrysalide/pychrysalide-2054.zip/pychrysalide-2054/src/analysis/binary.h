
/* Chrysalide - Outil d'analyse de fichiers binaires
 * binary.h - prototypes pour le traitement des flots de code binaire
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ANALYSIS_BINARY_H
#define _ANALYSIS_BINARY_H


#include <glib-object.h>
#include <stdbool.h>

#include "content.h"
#include "loaded.h"
#include "db/collection.h"
#include "db/analyst.h"
#include "db/protocol.h"
#include "../arch/processor.h"
#include "../format/debuggable.h"
#include "../format/executable.h"
#include "../glibext/buffercache.h"



/* ------------------------ ENCADREMENTS D'UN BINAIRE CHARGE ------------------------ */


#define G_TYPE_LOADED_BINARY            g_loaded_binary_get_type()
#define G_LOADED_BINARY(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_LOADED_BINARY, GLoadedBinary))
#define G_IS_LOADED_BINARY(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_LOADED_BINARY))
#define G_LOADED_BINARY_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass), G_TYPE_LOADED_BINARY, GLoadedBinaryClass))
#define G_IS_LOADED_BINARY_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass), G_TYPE_LOADED_BINARY))
#define G_LOADED_BINARY_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), G_TYPE_LOADED_BINARY, GLoadedBinaryClass))


/* Description de fichier binaire (instance) */
typedef struct _GLoadedBinary GLoadedBinary;

/* Description de fichier binaire (classe) */
typedef struct _GLoadedBinaryClass GLoadedBinaryClass;


/* Modèle de sélection des parties */
typedef enum _BinaryPartModel
{
    BPM_DEFAULT,                            /* Selon le modèle par défaut  */
    BPM_ROUTINES,                           /* Sélection par les routines  */
    BPM_USER,                               /* Définitions utilisateur     */

    BPM_COUNT

} BinaryPartModel;


/* Indique le type défini pour une description de fichier binaire. */
GType g_loaded_binary_get_type(void);

/* Interprète un contenu binaire chargé. */
GLoadedContent *g_loaded_binary_new(GExeFormat *);



/* ------------------------- INFORMATIONS D'ENREGISTREMENTS ------------------------- */


/* Détermine si tous les enregistrements sont locaux ou non. */
bool g_loaded_binary_use_remote_storage(const GLoadedBinary *);

/* Définit si tous les enregistrements sont locaux ou non. */
void g_loaded_binary_set_remote_storage_usage(GLoadedBinary *, bool);

/* Identifie le serveur distant associé au binaire courant. */
void g_loaded_binary_get_remote_server(const GLoadedBinary *, const char **, const char **);

/* Définit le serveur distant associé au binaire courant. */
void g_loaded_binary_set_remote_server(GLoadedBinary *, const char *, const char *);

/* Sauvegarde le cache des instructions désassemblées. */
bool g_loaded_binary_save_cache(const GLoadedBinary *);



/* -------------------------- MANIPULATION DES COLLECTIONS -------------------------- */


/* Fournit un client assurant la liaison avec un serveur. */
GAnalystClient *g_loaded_binary_get_client(const GLoadedBinary *);

/* Fournit l'ensemble des collections utilisées par un binaire. */
GDbCollection **g_loaded_binary_get_collections(const GLoadedBinary *, size_t *);

/* Trouve une collection assurant une fonctionnalité donnée. */
GDbCollection *g_loaded_binary_find_collection(const GLoadedBinary *, DBFeatures);

/* Demande l'intégration d'une modification dans une collection. */
bool g_loaded_binary_add_to_collection(GLoadedBinary *, GDbItem *);

/* Spécifie la bordure temporelle limite des activations. */
bool g_loaded_binary_set_last_active(GLoadedBinary *, timestamp_t);






/* Fournit le format de fichier reconnu dans le contenu binaire. */
GExeFormat *g_loaded_binary_get_format(const GLoadedBinary *);

/* Fournit le processeur de l'architecture liée au binaire. */
GArchProcessor *g_loaded_binary_get_processor(const GLoadedBinary *);

/* Fournit le tampon associé au contenu assembleur d'un binaire. */
GBufferCache *g_loaded_binary_get_disassembly_cache(const GLoadedBinary *);


/* -------------------- SAUVEGARDE ET RESTAURATION DE PARAMETRES -------------------- */


/* Complète la liste des destinations déjà visitées. */
void g_loaded_binary_remember_new_goto(GLoadedBinary *, const vmpa2t *);

/* Fournit la liste des anciennes destinations déjà visitées. */
vmpa2t *g_loaded_binary_get_old_gotos(GLoadedBinary *, size_t *);



/* ---------------------- GESTION SOUS FORME DE CONTENU CHARGE ---------------------- */


/* Type de représentations */
typedef enum _BinaryView
{
    BVW_HEX,                                /* Contenu en hexadécimal      */
    BVW_BLOCK,                              /* Version basique             */
    BVW_GRAPH,                              /* Affichage en graphique      */

    BVW_COUNT

} BinaryView;



#endif  /* _ANALYSIS_BINARY_H */
