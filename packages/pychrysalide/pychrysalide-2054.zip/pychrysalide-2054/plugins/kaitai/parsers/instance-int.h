
/* Chrysalide - Outil d'analyse de fichiers binaires
 * instance-int.h - prototypes pour les spécifications internes d'une instance Kaitai
 *
 * Copyright (C) 2023 Cyrille Bagard
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


#ifndef _PLUGINS_KAITAI_PARSERS_INSTANCE_INT_H
#define _PLUGINS_KAITAI_PARSERS_INSTANCE_INT_H


#include "attribute-int.h"
#include "instance.h"



/* Spécification d'une instance Kaitai (instance) */
struct _GKaitaiInstance
{
    GKaitaiAttribute parent;                /* A laisser en premier        */

    char *name;                             /* Nom attribué à l'instance   */

    char *io;                               /* Contenu binaire forcé       */
    char *pos;                              /* Position forcée             */
    char *value;                            /* Formule pour calcul         */

};

/* Spécification d'une instance Kaitai (classe) */
struct _GKaitaiInstanceClass
{
    GKaitaiAttributeClass parent;           /* A laisser en premier        */

};


/* Met en place un lecteur d'instance Kaitai. */
bool g_kaitai_instance_create(GKaitaiInstance *, GYamlNode *);



#endif  /* _PLUGINS_KAITAI_PARSERS_INSTANCE_INT_H */
