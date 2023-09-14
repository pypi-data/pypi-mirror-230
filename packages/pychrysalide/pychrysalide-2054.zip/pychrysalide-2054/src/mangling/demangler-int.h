
/* Chrysalide - Outil d'analyse de fichiers binaires
 * demangler-int.h - prototypes internes utiles aux décodeurs de désignations de symboles
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


#ifndef _MANGLING_DEMANGLER_INT_H
#define _MANGLING_DEMANGLER_INT_H


#include "context.h"
#include "demangler.h"



/* Fournit la désignation interne du décodeur de désignations. */
typedef char *(* get_demangler_key_fc) (const GCompDemangler *);

/* Indique si une chaîne peut être traitée par le décodeur. */
typedef bool (* can_be_demangled_fc) (const char *);


/* Décodeur de désignations générique (instance) */
struct _GCompDemangler
{
    GObject parent;                         /* A laisser en premier        */

};

/* Décodeur de désignations générique (classe) */
struct _GCompDemanglerClass
{
    GObjectClass parent;                    /* A laisser en premier        */

    get_demangler_key_fc get_key;           /* Code représentant la classe */
    can_be_demangled_fc can_demangle;       /* Possibilité de traitement   */

    const char *ns_sep;                     /* Motif de séparation         */
    GType context_type;                     /* Contexte de décodage        */

};



#endif  /* _FORMAT_MANGLING_DEMANGLER_H */
