
/* Chrysalide - Outil d'analyse de fichiers binaires
 * linegen-int.h - définitions internes propres aux intermédiaires de génération de lignes
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


#ifndef _GLIBEXT_LINEGEN_INT_H
#define _GLIBEXT_LINEGEN_INT_H


#include "linegen.h"



/* Indique le nombre de ligne prêtes à être générées. */
typedef size_t (* linegen_count_lines_fc) (const GLineGenerator *);

/* Retrouve l'emplacement correspondant à une position donnée. */
typedef void (* linegen_compute_fc) (const GLineGenerator *, gint, size_t, size_t, GLineCursor **);

/* Détermine si le conteneur s'inscrit dans une plage donnée. */
typedef int (* linegen_contain_fc) (const GLineGenerator *, size_t, size_t, const GLineCursor *);

/* Renseigne sur les propriétés liées à un générateur. */
typedef BufferLineFlags (* linegen_get_flags_fc) (const GLineGenerator *, size_t, size_t);

/* Imprime dans une ligne de rendu le contenu représenté. */
typedef void (* linegen_print_fc) (GLineGenerator *, GBufferLine *, size_t, size_t, const GBinContent *);


/* Intermédiaire pour la génération de lignes (interface) */
struct _GLineGeneratorIface
{
    GTypeInterface base_iface;              /* A laisser en premier        */

    linegen_count_lines_fc count;           /* Décompte des lignes         */
    linegen_compute_fc compute;             /* Calcul d'emplacement        */
    linegen_contain_fc contain;             /* Inclusion de positions      */
    linegen_get_flags_fc get_flags;         /* Récupération des drapeaux   */
    linegen_print_fc print;                 /* Impression d'une ligne      */

};


/* Redéfinition */
typedef GLineGeneratorIface GLineGeneratorInterface;



#endif  /* _GLIBEXT_LINEGEN_INT_H */
