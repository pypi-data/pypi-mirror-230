
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


@title RSC (register-shifted register)

@id 152

@desc {

	Reverse Subtract (register-shifted register) subtracts a register value and the value of NOT (Carry flag) from a register-shifted register value, and writes the result to the destination register. It can optionally update the condition flags based on the result.

}

@encoding (A1) {

	@word cond(4) 0 0 0 0 1 1 1 S(1) Rn(4) Rd(4) Rs(4) 0 type(2) 1 Rm(4)

	@syntax {

		@subid 464

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift_t = UInt(type)
			reg_S = Register(Rs)
			shift = BuildRegShift(shift_t, reg_S)

		}

		@asm rsc ?reg_D reg_N reg_M shift

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 465

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift_t = UInt(type)
			reg_S = Register(Rs)
			shift = BuildRegShift(shift_t, reg_S)

		}

		@asm rscs ?reg_D reg_N reg_M shift

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

