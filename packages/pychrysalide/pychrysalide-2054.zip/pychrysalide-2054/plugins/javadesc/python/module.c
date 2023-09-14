
/* Chrysalide - Outil d'analyse de fichiers binaires
 * module.c - intégration du répertoire javadesc en tant que module
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "module.h"


#include <Python.h>


#include <plugins/pychrysalide/access.h>


#include "demangler.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Etend le module 'mangling' avec des compléments pour Java.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_mangling_javadesc_module_to_python_module(void)
{
    bool result;                            /* Bilan à retourner           */
    PyObject *super;                        /* Module à compléter          */

    super = get_access_to_python_module("pychrysalide.mangling");

    result = register_python_java_demangler(super);

    return result;

}
