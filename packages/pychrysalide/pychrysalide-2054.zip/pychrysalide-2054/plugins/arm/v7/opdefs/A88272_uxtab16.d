
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


@title UXTAB16

@id 267

@desc {

	Unsigned Extend and Add Byte 16 extracts two 8-bit values from a register, zero-extends them to 16 bits each, adds the results to two 16-bit values from another register, and writes the final results to the destination register. The instruction can specify a rotation by 0, 8, 16, or 24 bits before extracting the 8-bit values.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 1 0 0 0 1 1 Rn(4) 1 1 1 1 Rd(4) 1 0 rotate(2) Rm(4)

	@syntax {

		@subid 795

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			rotation = Rotation(rotate:'000')

		}

		@asm uxtab16 ?reg_D reg_N reg_M ?rotation

	}

}

@encoding (A1) {

	@word cond(4) 0 1 1 0 1 1 0 0 Rn(4) Rd(4) rotate(2) 0 0 0 1 1 1 Rm(4)

	@syntax {

		@subid 796

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			rotation = Rotation(rotate:'000')

		}

		@asm uxtab16 ?reg_D reg_N reg_M ?rotation

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

