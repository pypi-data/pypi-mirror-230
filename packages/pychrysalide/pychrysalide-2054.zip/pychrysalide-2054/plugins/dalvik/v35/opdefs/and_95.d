
/* Chrysalide - Outil d'analyse de fichiers binaires
 * ##FILE## - traduction d'instructions Dalvik
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
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


@title and-int

@id 149

@desc {

    Perform the identified binary operation on the two source registers, storing the result in the destination register.

<b>Note:</b> Contrary to other <b>-long</b> mathematical operations (which take register pairs for both their first and their second source), <b>shl-long</b>, <b>shr-long</b>, and <b>ushr-long</b> take a register pair for their first source (the value to be shifted), but a single register for their second source (the shifting distance).

}

@encoding() {

    @format 23x

}
