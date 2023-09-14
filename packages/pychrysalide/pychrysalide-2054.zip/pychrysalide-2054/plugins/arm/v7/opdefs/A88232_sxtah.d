
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


@title SXTAH

@id 227

@desc {

	Signed Extend and Add Halfword extracts a 16-bit value from a register, sign-extends it to 32 bits, adds the result to a value from another register, and writes the final result to the destination register. The instruction can specify a rotation by 0, 8, 16, or 24 bits before extracting the 16-bit value.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 1 0 0 0 0 0 Rn(4) 1 1 1 1 Rd(4) 1 0 rotate(2) Rm(4)

	@syntax {

		@subid 711

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			rotation = Rotation(rotate:'000')

		}

		@asm sxtah ?reg_D reg_N reg_M ?rotation

	}

}

@encoding (A1) {

	@word cond(4) 0 1 1 0 1 0 1 1 Rn(4) Rd(4) rotate(2) 0 0 0 1 1 1 Rm(4)

	@syntax {

		@subid 712

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			rotation = Rotation(rotate:'000')

		}

		@asm sxtah ?reg_D reg_N reg_M ?rotation

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

