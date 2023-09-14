
/* Chrysalide - Outil d'analyse de fichiers binaires
 * elf_def.c - équivalent Python du fichier "plugins/elf/elf_def.c"
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


#include "elf_def.h"


#include <pygobject.h>


#include "../elf_def.h"
#include "../elf-int.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un format ELF.                 *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Indique la taille d'un entête ELF.                           *
*                                                                             *
*  Retour      : Taille d'une structure ELF adaptée à l'architecture.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_get_sizeof_hdr(PyObject *self, void *closure)
{
    PyObject *result;                       /* Liste éventuelle à renvoyer */
    GElfFormat *format;                     /* Version native              */

    format = G_ELF_FORMAT(pygobject_get(self));

    result = PyLong_FromSize_t(ELF_SIZEOF_HDR(format));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un format ELF.                 *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Indique la taille d'un entête de programme ELF.              *
*                                                                             *
*  Retour      : Taille d'une structure ELF adaptée à l'architecture.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_get_sizeof_phdr(PyObject *self, void *closure)
{
    PyObject *result;                       /* Liste éventuelle à renvoyer */
    GElfFormat *format;                     /* Version native              */

    format = G_ELF_FORMAT(pygobject_get(self));

    result = PyLong_FromSize_t(ELF_SIZEOF_PHDR(format));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un format ELF.                 *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Indique la taille d'un entête de section ELF.                *
*                                                                             *
*  Retour      : Taille d'une structure ELF adaptée à l'architecture.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_get_sizeof_shdr(PyObject *self, void *closure)
{
    PyObject *result;                       /* Liste éventuelle à renvoyer */
    GElfFormat *format;                     /* Version native              */

    format = G_ELF_FORMAT(pygobject_get(self));

    result = PyLong_FromSize_t(ELF_SIZEOF_SHDR(format));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un format ELF.                 *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Indique la taille d'une entité dynamique de format ELF.      *
*                                                                             *
*  Retour      : Taille d'une structure ELF adaptée à l'architecture.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_get_sizeof_dyn(PyObject *self, void *closure)
{
    PyObject *result;                       /* Liste éventuelle à renvoyer */
    GElfFormat *format;                     /* Version native              */

    format = G_ELF_FORMAT(pygobject_get(self));

    result = PyLong_FromSize_t(ELF_SIZEOF_DYN(format));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un format ELF.                 *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Indique la taille d'une information sur un symbole ELF.      *
*                                                                             *
*  Retour      : Taille d'une structure ELF adaptée à l'architecture.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_get_sizeof_sym(PyObject *self, void *closure)
{
    PyObject *result;                       /* Liste éventuelle à renvoyer */
    GElfFormat *format;                     /* Version native              */

    format = G_ELF_FORMAT(pygobject_get(self));

    result = PyLong_FromSize_t(ELF_SIZEOF_SYM(format));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = classe représentant un format ELF.                 *
*                closure = adresse non utilisée ici.                          *
*                                                                             *
*  Description : Indique la taille d'une information de relocalisation ELF.   *
*                                                                             *
*  Retour      : Taille d'une structure ELF adaptée à l'architecture.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *py_elf_format_get_sizeof_rel(PyObject *self, void *closure)
{
    PyObject *result;                       /* Liste éventuelle à renvoyer */
    GElfFormat *format;                     /* Version native              */

    format = G_ELF_FORMAT(pygobject_get(self));

    result = PyLong_FromSize_t(ELF_SIZEOF_REL(format));

    return result;

}
