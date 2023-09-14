
/* Chrysalide - Outil d'analyse de fichiers binaires
 * ##FILE## - traduction d'instructions ARMv7
 *
 * Copyright (C) 2017 Cyrille Bagard
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


@title SETEND

@id 162

@desc {

	Set Endianness writes a new value to ENDIANSTATE.

}

@encoding (t1) {

	@half 1 0 1 1 0 1 1 0 0 1 0 1 E(1) 0 0 0

	@syntax {

		@subid 489

		@conv {

			endian_specifier = Endian(E)

		}

		@asm setend endian_specifier

	}

}

@encoding (A1) {

	@word 1 1 1 1 0 0 0 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 E(1) 0 0 0 0 0 0 0 0 0

	@syntax {

		@subid 490

		@conv {

			endian_specifier = Endian(E)

		}

		@asm setend endian_specifier

	}

}

