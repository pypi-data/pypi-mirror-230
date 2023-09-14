
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


@title ADD (SP plus register, ARM)

@id 10

@desc {

	This instruction adds an optionally-shifted register value to the SP value, and writes the result to the destination register.

}

@encoding (A1) {

	@word cond(4) 0 0 0 0 1 0 0 S(1) 1 1 0 1 Rd(4) imm5(5) type(2) 0 Rm(4)

	@syntax {

		@subid 37

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_SP = Register(13)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm5)

		}

		@asm add ?reg_D reg_SP reg_M ?shift

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 38

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_SP = Register(13)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm5)

		}

		@asm adds ?reg_D reg_SP reg_M ?shift

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

