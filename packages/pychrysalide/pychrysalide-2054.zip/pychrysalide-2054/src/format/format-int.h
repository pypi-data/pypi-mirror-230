
/* Chrysalide - Outil d'analyse de fichiers binaires
 * format-int.h - prototypes utiles aux formats binaires
 *
 * Copyright (C) 2009-2018 Cyrille Bagard
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


#ifndef _FORMAT_FORMAT_INT_H
#define _FORMAT_FORMAT_INT_H


#include "format.h"


#include "known-int.h"
#include "preload.h"
#include "../glibext/objhole.h"
#include "../mangling/demangler.h"



/* ------------------------ TRAITEMENT INDIVIDUEL DE FORMATS ------------------------ */


/* Indique le boutisme employé par le format binaire analysé. */
typedef SourceEndian (* format_get_endian_fc) (const GBinFormat *);

/* Rythme des allocations pour les entrées de code */
#define EXTRA_POINT_BLOCK 20


/* Informations glissées dans la structure GObject de GArchOperand */
typedef struct _fmt_extra_data_t
{
    FormatFlag flags;                       /* Informations complémentaires*/

} fmt_extra_data_t;

/* Encapsulation avec un verrou d'accès */
typedef union _fmt_obj_extra_t
{
    fmt_extra_data_t data;                  /* Données embarquées          */
    lockable_obj_extra_t lockable;          /* Gestion d'accès aux fanions */

} fmt_obj_extra_t;


/* Description d'une erreur */
typedef struct _fmt_error
{
    BinaryFormatError type;                 /* Type d'erreur               */

    vmpa2t addr;                            /* Localisation du problème    */
    char *desc;                             /* Description du soucis       */

} fmt_error;

/* Format binaire générique (instance) */
struct _GBinFormat
{
    GKnownFormat parent;                    /* A laisser en premier        */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

    /**
     * L'inclusion des informations suivantes dépend de l'architecture.
     *
     * Si la structure GObject possède un trou, on remplit de préférence
     * ce dernier.
     */

    fmt_obj_extra_t extra;                  /* Externalisation embarquée   */

#endif

    virt_t *start_points[DPL_COUNT];        /* Départ de désassemblage     */
    size_t pt_allocated[DPL_COUNT];         /* Taille d'inscription allouée*/
    size_t pt_count[DPL_COUNT];             /* Nombre de points enregistrés*/
    GRWLock pt_lock;                        /* Accès à la liste des points */

    GPreloadInfo *info;                     /* Préchargements du format    */

    GCompDemangler *demangler;              /* Décodage de noms privilégié */

    GBinSymbol **symbols;                   /* Liste des symboles trouvés  */
    size_t sym_count;                       /* Quantité de ces symboles    */
    unsigned int sym_stamp;                 /* Marque de suivi des modifs  */
    GRWLock syms_lock;                      /* Accès à la liste de symboles*/
#ifndef NDEBUG
    gint sym_locked;                        /* Statut d'accès à la liste   */
#endif

    fmt_error *errors;                      /* Liste d'erreurs rencontrées */
    size_t error_count;                     /* Taille de cette liste       */
    GMutex error_mutex;                     /* Verrou pour l'accès         */
#ifndef NDEBUG
    gint error_locked;                      /* Statut d'accès à la liste   */
#endif

};

/* Format binaire générique (classe) */
struct _GBinFormatClass
{
    GKnownFormatClass parent;               /* A laisser en premier        */

    format_get_endian_fc get_endian;        /* Boutisme employé            */

    /* Signaux */

    void (* symbol_added) (GBinFormat *, GBinSymbol *);
    void (* symbol_removed) (GBinFormat *, GBinSymbol *);

};


/**
 * Accès aux informations éventuellement déportées.
 */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

#   define GET_BIN_FORMAT_EXTRA(fmt) (fmt_extra_data_t *)&fmt->extra

#else

#   define GET_BIN_FORMAT_EXTRA(fmt) GET_GOBJECT_EXTRA(G_OBJECT(fmt), fmt_extra_data_t)

#endif



/* ------------------------------ DECODAGE DE SYMBOLES ------------------------------ */


/* Décode une chaîne de caractères donnée en type. */
GDataType *g_binary_format_decode_type(const GBinFormat *, const char *);

/* Décode une chaîne de caractères donnée en routine. */
GBinRoutine *g_binary_format_decode_routine(const GBinFormat *, const char *);



#endif  /* _FORMAT_FORMAT_INT_H */
