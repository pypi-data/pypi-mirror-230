
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


@title SMMLS

@id 180

@desc {

	Signed Most Significant Word Multiply Subtract multiplies two signed 32-bit values, subtracts the result from a 32-bit accumulate value that is shifted left by 32 bits, and extracts the most significant 32 bits of the result of that subtraction. Optionally, the instruction can specify that the result of the instruction is rounded instead of being truncated. In this case, the constant 0x80000000 is added to the result of the subtraction before the high word is extracted.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 1 1 0 1 1 0 Rn(4) Ra(4) Rd(4) 0 0 0 R(1) Rm(4)

	@syntax {

		@subid 549

		@assert {

			R == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smmlsr reg_D reg_N reg_M reg_A

	}

	@syntax {

		@subid 550

		@assert {

			R == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smmls reg_D reg_N reg_M reg_A

	}

}

@encoding (A1) {

	@word cond(4) 0 1 1 1 0 1 0 1 Rd(4) Ra(4) Rm(4) 1 1 R(1) 1 Rn(4)

	@syntax {

		@subid 551

		@assert {

			R == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smmlsr reg_D reg_N reg_M reg_A

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 552

		@assert {

			R == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smmls reg_D reg_N reg_M reg_A

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

