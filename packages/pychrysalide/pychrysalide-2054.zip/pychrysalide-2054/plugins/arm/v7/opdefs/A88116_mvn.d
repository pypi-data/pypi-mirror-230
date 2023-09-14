
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


@title MVN (register)

@id 111

@desc {

	Bitwise NOT (register) writes the bitwise inverse of a register value to the destination register. It can optionally update the condition flags based on the result.

}

@encoding (t1) {

	@half 0 1 0 0 0 0 1 1 1 1 Rm(3) Rd(3)

	@syntax {

		@subid 348

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)

		}

		@asm mvn reg_D reg_M

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 0 1 0 0 1 1 S(1) 1 1 1 1 0 imm3(3) Rd(4) imm2(2) type(2) Rm(4)

	@syntax {

		@subid 349

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm3:imm2)

		}

		@asm mvn.w reg_D reg_M ?shift

	}

	@syntax {

		@subid 350

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm3:imm2)

		}

		@asm mvns.w reg_D reg_M ?shift

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 1 1 1 S(1) 0 0 0 0 Rd(4) imm5(5) type(2) 0 Rm(4)

	@syntax {

		@subid 351

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm5)

		}

		@asm mvn reg_D reg_M ?shift

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 352

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm5)

		}

		@asm mvns reg_D reg_M ?shift

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

