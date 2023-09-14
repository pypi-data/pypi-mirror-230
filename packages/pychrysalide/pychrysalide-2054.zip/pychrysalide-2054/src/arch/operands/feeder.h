
/* Chrysalide - Outil d'analyse de fichiers binaires
 * feeder.h - prototypes pour la fourniture d'éléments non architecturaux
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


#ifndef _ARCH_OPERANDS_FEEDER_H
#define _ARCH_OPERANDS_FEEDER_H


#include <glib-object.h>


#include "../../glibext/bufferline.h"



#define G_TYPE_PROXY_FEEDER             (g_proxy_feeder_get_type())
#define G_PROXY_FEEDER(obj)             (G_TYPE_CHECK_INSTANCE_CAST((obj), G_TYPE_PROXY_FEEDER, GProxyFeeder))
#define G_PROXY_FEEDER_CLASS(vtable)    (G_TYPE_CHECK_CLASS_CAST((vtable), G_TYPE_PROXY_FEEDER, GProxyFeederIface))
#define G_IS_PROXY_FEEDER(obj)          (G_TYPE_CHECK_INSTANCE_TYPE((obj), G_TYPE_PROXY_FEEDER))
#define G_IS_PROXY_FEEDER_CLASS(vtable) (G_TYPE_CHECK_CLASS_TYPE((vtable), G_TYPE_PROXY_FEEDER))
#define G_PROXY_FEEDER_GET_IFACE(inst)  (G_TYPE_INSTANCE_GET_INTERFACE((inst), G_TYPE_PROXY_FEEDER, GProxyFeederIface))


/* Fournisseur d'élément non architectural (coquille vide) */
typedef struct _GProxyFeeder GProxyFeeder;

/* Fournisseur d'élément non architectural (interface) */
typedef struct _GProxyFeederIface GProxyFeederIface;


/* Détermine le type d'une interface pour la Fourniture d'éléments non architecturaux. */
GType g_proxy_feeder_get_type(void) G_GNUC_CONST;

/* Compare un fournisseur avec un autre. */
int g_proxy_feeder_compare(const GProxyFeeder *, const GProxyFeeder *);

/* Traduit un fournisseur en version humainement lisible. */
void g_proxy_feeder_print(const GProxyFeeder *, GBufferLine *);



#endif  /* _ARCH_OPERANDS_FEEDER_H */
