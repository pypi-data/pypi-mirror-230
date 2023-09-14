
/* Chrysalide - Outil d'analyse de fichiers binaires
 * columns.h - prototypes pour l'énumération globale des colonnes de rendu
 *
 * Copyright (C) 2022 Cyrille Bagard
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


#ifndef _CORE_COLUMNS_H
#define _CORE_COLUMNS_H



/* Désignation des colonnes d'une ligne */
typedef enum _DisassLineColumn
{
    DLC_PHYSICAL,                           /* Position physique           */
    DLC_VIRTUAL,                            /* Adresse virtuelle           */
    DLC_BINARY,                             /* Contenu sous forme binaire  */
    DLC_ASSEMBLY_LABEL,                     /* Etiquette dans les données  */
    DLC_ASSEMBLY_HEAD,                      /* Instruction pour assembleur */
    DLC_ASSEMBLY,                           /* Code pour assembleur        */
    DLC_COMMENTS,                           /* Commentaires éventuels      */

    DLC_COUNT,

} DisassLineColumn;


/* Désignation des colonnes d'une ligne */
typedef enum _HexLineColumn
{
    HLC_PHYSICAL,                           /* Position physique           */
    HLC_BINARY,                             /* Données binaires brutes     */
    HLC_PADDING,                            /* Espacement forcé            */
    HLC_TRANSLATION,                        /* Traduction de contenu       */

    HLC_COUNT,

} HexLineColumn;



#endif  /* _CORE_COLUMNS_H */
