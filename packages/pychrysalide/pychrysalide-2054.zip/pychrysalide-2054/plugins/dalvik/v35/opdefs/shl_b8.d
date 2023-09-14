
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


@title shl-int/2addr

@id 184

@desc {

    Perform the identified binary operation on the two source registers, storing the result in the first source register.

<b>Note:</b> Contrary to other <b>-long/2addr</b> mathematical operations (which take register pairs for both their destination/first source and their second source), <b>shl-long/2addr</b>, <b>shr-long/2addr</b>, and <b>ushr-long/2addr</b> take a register pair for their destination/first source (the value to be shifted), but a single register for their second source (the shifting distance).

}

@encoding() {

    @format 12x

}
