
/* Chrysalide - Outil d'analyse de fichiers binaires
 * rename-int.h - définitions internes propres aux opérandes ciblant une portion de désassemblage
 *
 * Copyright (C) 2020 Cyrille Bagard
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


#ifndef _ARCH_OPERANDS_RENAME_INT_H
#define _ARCH_OPERANDS_RENAME_INT_H


#include "rename.h"



/* ------------------------ INTERFACE POUR OPERANDE RENOMMEE ------------------------ */


/* Obtient l'adresse de la cible visée par un opérande. */
typedef char * (* get_renamed_text_fc) (const GRenamedOperand *);


/* Opérande renommé avec un texte alternatif (interface) */
struct _GRenamedOperandIface
{
    GTypeInterface base_iface;              /* A laisser en premier        */

    get_renamed_text_fc get_text;           /* Récupération d'alternative  */

};


/* Redéfinition */
typedef GRenamedOperandIface GRenamedOperandInterface;



/* ----------------------- INTERFACE POUR OPERANDE RENOMMABLE ----------------------- */


/* Obtient l'adresse de la cible visée par un opérande. */
typedef GRenamedOperand * (* build_renameable_fc) (const GRenameableOperand *, const char *);


/* Opérande offrant une capacité de renommage (interface) */
struct _GRenameableOperandIface
{
    GTypeInterface base_iface;              /* A laisser en premier        */

    build_renameable_fc build;              /* Obtention de la cible       */

};


/* Redéfinition */
typedef GRenameableOperandIface GRenameableOperandInterface;



#endif  /* _ARCH_OPERANDS_RENAME_INT_H */
