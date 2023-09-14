
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


@title CMP (register)

@id 37

@desc {

	Compare (register) subtracts an optionally-shifted register value from a register value. It updates the condition flags based on the result, and discards the result.

}

@encoding (t1) {

	@half 0 1 0 0 0 0 1 0 1 0 Rm(3) Rn(3)

	@syntax {

		@subid 116

		@conv {

			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm cmp reg_N reg_M

	}

}

@encoding (t2) {

	@half 0 1 0 0 0 1 0 1 N(1) Rm(4) Rn(3)

	@syntax {

		@subid 117

		@conv {

			reg_N = Register(N:Rn)
			reg_M = Register(Rm)

		}

		@asm cmp reg_N reg_M

	}

}

@encoding (T3) {

	@word 1 1 1 0 1 0 1 1 1 0 1 1 Rn(4) 0 imm3(3) 1 1 1 1 imm2(2) type(2) Rm(4)

	@syntax {

		@subid 118

		@conv {

			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm3:imm2)

		}

		@asm cmp.w reg_N reg_M ?shift

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 1 0 1 Rn(4) 0 0 0 0 imm5(5) type(2) 0 Rm(4)

	@syntax {

		@subid 119

		@conv {

			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm5)

		}

		@asm cmp reg_N reg_M ?shift

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

