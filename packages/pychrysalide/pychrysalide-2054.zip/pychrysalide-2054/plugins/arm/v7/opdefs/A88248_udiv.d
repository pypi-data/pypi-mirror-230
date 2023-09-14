
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


@title UDIV

@id 243

@desc {

	Unsigned Divide divides a 32-bit unsigned integer register value by a 32-bit unsigned integer register value, and writes the result to the destination register. The condition flags are not affected. See ARMv7 implementation requirements and options for the divide instructions on page A4-172 for more information about this instruction.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 1 1 1 0 1 1 Rn(4) 1 1 1 1 Rd(4) 1 1 1 1 Rm(4)

	@syntax {

		@subid 745

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm udiv ?reg_D reg_N reg_M

	}

}

@encoding (A1) {

	@word cond(4) 0 1 1 1 0 0 1 1 Rd(4) 1 1 1 1 Rm(4) 0 0 0 1 Rn(4)

	@syntax {

		@subid 746

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm udiv ?reg_D reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

