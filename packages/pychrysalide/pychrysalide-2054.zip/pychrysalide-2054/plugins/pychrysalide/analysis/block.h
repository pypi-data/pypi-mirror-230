
/* Chrysalide - Outil d'analyse de fichiers binaires
 * block.h - prototypes pour l'équivalent Python du fichier "analysis/block.h"
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#ifndef _PLUGINS_PYCHRYSALIDE_ANALYSIS_BLOCK_H
#define _PLUGINS_PYCHRYSALIDE_ANALYSIS_BLOCK_H


#include <Python.h>
#include <stdbool.h>



/* ----------------------------- BLOC DE CODE GENERIQUE ----------------------------- */


/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_code_block_type(void);

/* Prend en charge l'objet 'pychrysalide.analysis.CodeBlock'. */
bool ensure_python_code_block_is_registered(void);

/* Tente de convertir en bloc de code. */
int convert_to_code_block(PyObject *, void *);



/* ------------------------- REGROUPEMENT EN LISTE DE BLOCS ------------------------- */


/* Fournit un accès à une définition de type à diffuser. */
PyTypeObject *get_python_block_list_type(void);

/* Prend en charge l'objet 'pychrysalide.analysis.BlockList'. */
bool ensure_python_block_list_is_registered(void);

/* Tente de convertir en liste de blocs de code. */
int convert_to_block_list_with_ref(PyObject *, void *);



#endif  /* _PLUGINS_PYCHRYSALIDE_ANALYSIS_BLOCK_H */
