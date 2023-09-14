
/* Chrysalide - Outil d'analyse de fichiers binaires
 * target.h - prototypes pour l'équivalent Python du fichier "arch/operands/target.h"
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _PLUGINS_PYCHRYSALIDE_ARCH_OPERANDS_TARGET_H
#define _PLUGINS_PYCHRYSALIDE_ARCH_OPERANDS_TARGET_H


#include <Python.h>
#include <stdbool.h>



/* ------------------ OPERANDES CONSTITUANT DE PURS INTERMEDIAIRES ------------------ */


/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_target_operand_type(void);

/* Prend en charge l'objet 'pychrysalide.arch.operands.TargetOperand'. */
bool ensure_python_target_operand_is_registered(void);

/* Tente de convertir en opérande ciblant idéalement un symbole. */
int convert_to_target_operand(PyObject *, void *);



#endif  /* _PLUGINS_PYCHRYSALIDE_ARCH_OPERANDS_TARGET_H */
