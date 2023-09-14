
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


@title check-cast

@id 31

@desc {

    Throw a <b>ClassCastException</b> if the reference in the given register cannot be cast to the indicated type.

<b>Note:</b> Since <b>A</b> must always be a reference (and not a primitive value), this will necessarily fail at runtime (that is, it will throw an exception) if <b>B</b> refers to a primitive type.

}

@encoding() {

    @format 21c | pool_type

}
