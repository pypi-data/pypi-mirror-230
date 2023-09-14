
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


@title cmpg-float

@id 46

@desc {

    Perform the indicated floating point or <b>long</b> comparison, setting <b>a</b> to <b>0</b> if <b>b == c</b>, <b>1</b> if <b>b &gt; c</b>, or <b>-1</b> if <b>b &lt; c</b>. The "bias" listed for the floating point operations indicates how <b>NaN</b> comparisons are treated: "gt bias" instructions return <b>1</b> for <b>NaN</b> comparisons, and "lt bias" instructions return <b>-1</b>.

For example, to check to see if floating point <b>x &lt; y</b> it is advisable to use <b>cmpg-float</b>; a result of <b>-1</b> indicates that the test was true, and the other values indicate it was false either due to a valid comparison or because one of the values was <b>NaN</b>.

}

@encoding() {

    @format 23x

}
