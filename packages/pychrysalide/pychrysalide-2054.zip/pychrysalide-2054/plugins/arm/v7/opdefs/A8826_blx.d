
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


@title BLX (register)

@id 25

@desc {

	Branch with Link and Exchange (register) calls a subroutine at an address and instruction set specified by a register.

}

@encoding (t1) {

	@half 0 1 0 0 0 1 1 1 1 Rm(4) 0 0 0

	@syntax {

		@subid 91

		@conv {

			reg_M = Register(Rm)

		}

		@asm blx reg_M

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 0 1 0 1 1 1 1 1 1 1 1 1 1 1 1 0 0 1 1 Rm(4)

	@syntax {

		@subid 92

		@conv {

			reg_M = Register(Rm)

		}

		@asm blx reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

