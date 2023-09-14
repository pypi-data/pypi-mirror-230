
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


@title ENTERX, LEAVEX

@id 387

@desc {

	ENTERX causes a change from Thumb state to ThumbEE state, or has no effect in ThumbEE state. ENTERX is UNDEFINED in Hyp mode. LEAVEX causes a change from ThumbEE state to Thumb state, or has no effect in Thumb state.

}

@encoding (T1) {

	@word 1 1 1 1 0 0 1 1 1 0 1 1 1 1 1 1 1 0 0 0 1 1 1 1 0 0 0 J(1) 1 1 1 1

	@syntax {

		@subid 3780

		@assert {

			J == 1

		}

		@asm enterx

	}

	@syntax {

		@subid 3781

		@assert {

			J == 0

		}

		@asm leavex

	}

}

