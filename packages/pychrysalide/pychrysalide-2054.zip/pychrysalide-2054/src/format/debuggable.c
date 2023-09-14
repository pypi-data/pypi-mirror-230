
/* Chrysalide - Outil d'analyse de fichiers binaires
 * debuggable.c - support des formats d'exécutables
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#include "debuggable.h"


#include <malloc.h>
#include <stdlib.h>


#include "debuggable-int.h"
#include "format.h"



/* Initialise la classe des formats d'exécutables génériques. */
static void g_debuggable_format_class_init(GDbgFormatClass *);

/* Initialise une instance de format d'exécutable générique. */
static void g_debuggable_format_init(GDbgFormat *);

/* Indique le boutisme employé par le format binaire analysé. */
static SourceEndian g_debuggable_format_get_endianness(const GDbgFormat *);



/* Indique le type défini pour un format de débogage générique. */
G_DEFINE_TYPE(GDbgFormat, g_debuggable_format, G_TYPE_BIN_FORMAT);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des formats d'exécutables génériques.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_debuggable_format_class_init(GDbgFormatClass *klass)
{
    GBinFormatClass *fmt;                   /* Version en format basique   */

    fmt = G_BIN_FORMAT_CLASS(klass);

    fmt->get_endian = (format_get_endian_fc)g_debuggable_format_get_endianness;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de format d'exécutable générique.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_debuggable_format_init(GDbgFormat *format)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format = description du binaire de débogage à consulter.     *
*                                                                             *
*  Description : Indique le boutisme employé par le format binaire analysé.   *
*                                                                             *
*  Retour      : Boutisme associé au format.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static SourceEndian g_debuggable_format_get_endianness(const GDbgFormat *format)
{
    return g_binary_format_get_endianness(G_BIN_FORMAT(format->executable));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : format     = description du binaire de débogage à compléter. *
*                executable = référence vers le binaire exécutable à lier.    *
*                                                                             *
*  Description : Associe officiellement des formats exécutable et de débogage.*
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_debuggable_format_attach_executable(GDbgFormat *format, GExeFormat *executable)
{
    format->executable = executable;

}
