
/* Chrysalide - Outil d'analyse de fichiers binaires
 * feeder-int.h - définitions internes propres aux fournisseurs d'éléments non architecturaux
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


#ifndef _ARCH_OPERANDS_FEEDER_INT_H
#define _ARCH_OPERANDS_FEEDER_INT_H


#include "feeder.h"


#include "../../analysis/storage/serialize-int.h"



/* Compare un fournisseur avec un autre. */
typedef int (* compare_proxy_operand_fc) (const GProxyFeeder *, const GProxyFeeder *);

/* Traduit un fournisseur en version humainement lisible. */
typedef void (* print_proxy_feeder_fc) (const GProxyFeeder *, GBufferLine *);



/* Fournisseur d'élément non architectural (interface) */
struct _GProxyFeederIface
{
    GSerializableObjectInterface base_iface;/* A laisser en premier        */

    compare_proxy_operand_fc compare;       /* Comparaison entre éléments  */

    print_proxy_feeder_fc print;            /* Affichage sur une ligne     */

};


/* Redéfinition */
typedef GProxyFeederIface GProxyFeederInterface;



#endif  /* _ARCH_OPERANDS_FEEDER_INT_H */
