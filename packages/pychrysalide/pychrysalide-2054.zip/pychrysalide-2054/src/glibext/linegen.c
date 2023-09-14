
/* Chrysalide - Outil d'analyse de fichiers binaires
 * linegen.c - intermédiaires de génération de lignes
 *
 * Copyright (C) 2016-2018 Cyrille Bagard
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


#include "linegen.h"


#include <assert.h>


#include "linegen-int.h"



/* Procède à l'initialisation de l'interface de génération. */
static void g_line_generator_default_init(GLineGeneratorInterface *);



/* Détermine le type d'une interface pour la mise en place de lignes. */
G_DEFINE_INTERFACE(GLineGenerator, g_line_generator, G_TYPE_OBJECT)


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de génération.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_line_generator_default_init(GLineGeneratorInterface *iface)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à consulter.                          *
*                                                                             *
*  Description : Indique le nombre de ligne prêtes à être générées.           *
*                                                                             *
*  Retour      : Nombre de lignes devant apparaître au final.                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_line_generator_count_lines(const GLineGenerator *generator)
{
    size_t result;                          /* Décompte à retourner        */
    GLineGeneratorIface *iface;             /* Interface utilisée          */

    iface = G_LINE_GENERATOR_GET_IFACE(generator);

    result = iface->count(generator);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à consulter.                          *
*                x         = position géographique sur la ligne concernée.    *
*                index     = indice de cette même ligne dans le tampon global.*
*                repeat    = indice d'utilisations successives du générateur. *
*                                                                             *
*  Description : Retrouve l'emplacement correspondant à une position donnée.  *
*                                                                             *
*  Retour      : Emplacement constitué.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GLineCursor *g_line_generator_compute_cursor(const GLineGenerator *generator, gint x, size_t index, size_t repeat)
{
    GLineCursor *result;                    /* Emplacement à renvoyer      */
    GLineGeneratorIface *iface;             /* Interface utilisée          */

    iface = G_LINE_GENERATOR_GET_IFACE(generator);

#ifndef NDEBUG
    if (iface->count != NULL)
        assert(repeat < g_line_generator_count_lines(generator));
#endif

    iface->compute(generator, x, index, repeat, &result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à consulter.                          *
*                index     = indice de cette même ligne dans le tampon global.*
*                repeat    = indice d'utilisations successives du générateur. *
*                cursor    = emplacement à analyser.                          *
*                                                                             *
*  Description : Détermine si le conteneur s'inscrit dans une plage donnée.   *
*                                                                             *
*  Retour      : Bilan de la détermination, utilisable en comparaisons.       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int g_line_generator_contain_cursor(const GLineGenerator *generator, size_t index, size_t repeat, const GLineCursor *cursor)
{
    int result;                             /* Bilan d'analyse à retourner */
    GLineGeneratorIface *iface;             /* Interface utilisée          */

    iface = G_LINE_GENERATOR_GET_IFACE(generator);

#ifndef NDEBUG
    if (iface->count != NULL)
        assert(repeat < g_line_generator_count_lines(generator));
#endif

    result = iface->contain(generator, index, repeat, cursor);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à consulter.                          *
*                index     = indice de cette même ligne dans le tampon global.*
*                repeat    = indice d'utilisations successives du générateur. *
*                                                                             *
*  Description : Renseigne sur les propriétés liées à un générateur.          *
*                                                                             *
*  Retour      : Propriétés particulières associées.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

BufferLineFlags g_line_generator_get_flags(const GLineGenerator *generator, size_t index, size_t repeat)
{
    BufferLineFlags result;                 /* Fanions à retourner         */
    GLineGeneratorIface *iface;             /* Interface utilisée          */

    iface = G_LINE_GENERATOR_GET_IFACE(generator);

#ifndef NDEBUG
    if (iface->count != NULL)
        assert(repeat < g_line_generator_count_lines(generator));
#endif

    result = iface->get_flags(generator, index, repeat);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : generator = générateur à utiliser pour l'impression.         *
*                line      = ligne de rendu à compléter.                      *
*                index     = indice de cette même ligne dans le tampon global.*
*                repeat    = indice d'utilisations successives du générateur. *
*                content   = éventuel contenu binaire brut à imprimer.        *
*                                                                             *
*  Description : Imprime dans une ligne de rendu le contenu représenté.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_line_generator_print(GLineGenerator *generator, GBufferLine *line, size_t index, size_t repeat, const GBinContent *content)
{
    GLineGeneratorIface *iface;             /* Interface utilisée          */

    iface = G_LINE_GENERATOR_GET_IFACE(generator);

#ifndef NDEBUG
    if (iface->count != NULL)
        assert(repeat < g_line_generator_count_lines(generator));
#endif

    iface->print(generator, line, index, repeat, content);

}
