
/* Chrysalide - Outil d'analyse de fichiers binaires
 * undefined-int.h - prototypes pour la définition générique interne des instructions au comportement non défini
 *
 * Copyright (C) 2019 Cyrille Bagard
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


#ifndef _ARCH_INSTRUCTIONS_UNDEFINED_INT_H
#define _ARCH_INSTRUCTIONS_UNDEFINED_INT_H


#include "undefined.h"
#include "../instruction-int.h"
#include "../../glibext/objhole.h"



/* Informations glissées dans la structure GObject de GArchInstruction */
typedef struct _undef_extra_data_t
{
    /**
     * Le champ uid de la structure parente attendue conduit à une taille
     * alignée sur 2 octets, donc à une taille totale de 4 octets ce qui
     * représente la limite maximale de taille supportée.
     *
     * Pour 3 octets à la base, qui devraient laisser 8 - 1 octets disponbibles
     * en incluant le bit de verrouillage.
     *
     * On reproduit donc la structure instr_extra_data_t ici, en basculant
     * l'énumération InstrExpectedBehavior en champ de bits.
     */

    itid_t uid;                             /* Identifiant unique du type  */
    ArchInstrFlag flags;                    /* Informations complémentaires*/

    unsigned int behavior : 2;              /* Conséquences réelles        */

} undef_extra_data_t;


/* Définition générique d'une instruction au comportement non défini (instance) */
struct _GUndefInstruction
{
    GArchInstruction parent;                /* A laisser en premier        */

};

/* Définition générique d'une instruction au comportement non défini (classe) */
struct _GUndefInstructionClass
{
    GArchInstructionClass parent;           /* A laisser en premier        */

};


/**
 * Accès aux informations éventuellement déportées.
 */

#if 1 //__SIZEOF_INT__ == __SIZEOF_LONG__

#   define GET_UNDEF_INSTR_EXTRA(ins) ((undef_extra_data_t *)&((GArchInstruction *)ins)->extra)

#else

#   define GET_UNDEF_INSTR_EXTRA(ins) GET_GOBJECT_EXTRA(G_OBJECT(ins), undef_extra_data_t)

#endif



#endif  /* _ARCH_INSTRUCTIONS_UNDEFINED_INT_H */
