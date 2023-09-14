
/* Chrysalide - Outil d'analyse de fichiers binaires
 * vmpa.h - prototypes pour l'équivalent Python du fichier "arch/vmpa.h"
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#ifndef _PLUGINS_PYCHRYSALIDE_ARCH_VMPA_H
#define _PLUGINS_PYCHRYSALIDE_ARCH_VMPA_H


#include <Python.h>
#include <stdbool.h>


#include <src/arch/vmpa.h>



/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_vmpa_type(void);

/* Prend en charge l'objet 'pychrysalide.arch.vmpa'. */
bool ensure_python_vmpa_is_registered(void);

/* Donne accès au coeur d'un objet 'pychrysalide.arch.vmpa'. */
vmpa2t *get_internal_vmpa(PyObject *);

/* Convertit une structure de type 'vmpa2t' en objet Python. */
PyObject *build_from_internal_vmpa(const vmpa2t *);

/* Tente de convertir en adresse n'importe quoi. */
int convert_any_to_vmpa(PyObject *, void *);

/* Libère la mémoire allouée pour un passage d'argument. */
void clean_vmpa_arg(vmpa2t *);



/* ------------------------ DEFINITION D'UNE ZONE EN MEMOIRE ------------------------ */


/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_mrange_type(void);

/* Prend en charge l'objet 'pychrysalide.arch.mrange'. */
bool ensure_python_mrange_is_registered(void);

/* Donne accès au coeur d'un objet 'pychrysalide.arch.mrange'. */
mrange_t *get_internal_mrange(PyObject *);

/* Convertit une structure de type 'mrange_t' en objet Python. */
PyObject *build_from_internal_mrange(const mrange_t *);

/* Tente de convertir en espace mémoire n'importe quoi. */
int convert_any_to_mrange(PyObject *, void *);



#endif  /* _PLUGINS_PYCHRYSALIDE_ARCH_VMPA_H */
