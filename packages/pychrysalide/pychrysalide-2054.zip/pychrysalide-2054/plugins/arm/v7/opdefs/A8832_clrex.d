
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


@title CLREX

@id 31

@desc {

	Clear-Exclusive clears the local record of the executing processor that an address has had a request for an exclusive access.

}

@encoding (T1) {

	@word 1 1 1 1 0 0 1 1 1 0 1 1 1 1 1 1 1 0 0 0 1 1 1 1 0 0 1 0 1 1 1 1

	@syntax {

		@subid 103

		@asm clrex

	}

}

@encoding (A1) {

	@word 1 1 1 1 0 1 0 1 0 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 1 1 1 1 1

	@syntax {

		@subid 104

		@asm clrex

	}

}

