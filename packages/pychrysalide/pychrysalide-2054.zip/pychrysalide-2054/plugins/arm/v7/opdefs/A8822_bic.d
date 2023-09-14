
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


@title BIC (register)

@id 21

@desc {

	Bitwise Bit Clear (register) performs a bitwise AND of a register value and the complement of an optionally-shifted register value, and writes the result to the destination register. It can optionally update the condition flags based on the result.

}

@encoding (t1) {

	@half 0 1 0 0 0 0 1 1 1 0 Rm(3) Rdn(3)

	@syntax {

		@subid 78

		@conv {

			reg_D = Register(Rdn)
			reg_N = Register(Rdn)
			reg_M = Register(Rm)

		}

		@asm bic ?reg_D reg_N reg_M

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 0 1 0 0 0 1 S(1) Rn(4) 0 imm3(3) Rd(4) imm2(2) type(2) Rm(4)

	@syntax {

		@subid 79

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm3:imm2)

		}

		@asm bic.w ?reg_D reg_N reg_M ?shift

	}

	@syntax {

		@subid 80

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm3:imm2)

		}

		@asm bics.w ?reg_D reg_N reg_M ?shift

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 1 1 0 S(1) Rn(4) Rd(4) imm5(5) type(2) 0 Rm(4)

	@syntax {

		@subid 81

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm5)

		}

		@asm bic ?reg_D reg_N reg_M ?shift

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 82

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm5)

		}

		@asm bics ?reg_D reg_N reg_M ?shift

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

