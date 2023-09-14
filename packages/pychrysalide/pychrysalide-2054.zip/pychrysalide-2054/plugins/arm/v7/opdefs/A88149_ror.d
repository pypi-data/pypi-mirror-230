
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


@title ROR (immediate)

@id 144

@desc {

	Rotate Right (immediate) provides the value of the contents of a register rotated by a constant value. The bits that are rotated off the right end are inserted into the vacated bit positions on the left. It can optionally update the condition flags based on the result.

}

@encoding (T1) {

	@word 1 1 1 0 1 0 1 0 0 1 0 S(1) 1 1 1 1 0 imm3(3) Rd(4) imm2(2) 1 1 Rm(4)

	@syntax {

		@subid 436

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)
			shift_n = DecodeImmShiftAmount('11', imm3:imm2)

		}

		@asm ror ?reg_D reg_M shift_n

	}

	@syntax {

		@subid 437

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)
			shift_n = DecodeImmShiftAmount('11', imm3:imm2)

		}

		@asm rors ?reg_D reg_M shift_n

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 1 0 1 S(1) 0 0 0 0 Rd(4) imm5(5) 1 1 0 Rm(4)

	@syntax {

		@subid 438

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)
			shift_n = DecodeImmShiftAmount('11', imm5)

		}

		@asm ror ?reg_D reg_M shift_n

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 439

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)
			shift_n = DecodeImmShiftAmount('11', imm5)

		}

		@asm rors ?reg_D reg_M shift_n

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

