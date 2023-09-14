
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


@title LSL (register)

@id 90

@desc {

	Logical Shift Left (register) shifts a register value left by a variable number of bits, shifting in zeros, and writes the result to the destination register. The variable number of bits is read from the bottom byte of a register. It can optionally update the condition flags based on the result.

}

@encoding (t1) {

	@half 0 1 0 0 0 0 0 0 1 0 Rm(3) Rdn(3)

	@syntax {

		@subid 284

		@conv {

			reg_D = Register(Rdn)
			reg_N = Register(Rdn)
			reg_M = Register(Rm)

		}

		@asm lsl ?reg_D reg_N reg_M

	}

}

@encoding (T2) {

	@word 1 1 1 1 1 0 1 0 0 0 0 S(1) Rn(4) 1 1 1 1 Rd(4) 0 0 0 0 Rm(4)

	@syntax {

		@subid 285

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm lsl.w ?reg_D reg_N reg_M

	}

	@syntax {

		@subid 286

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm lsls.w ?reg_D reg_N reg_M

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 1 0 1 S(1) 0 0 0 0 Rd(4) Rm(4) 0 0 0 1 Rn(4)

	@syntax {

		@subid 287

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm lsl ?reg_D reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 288

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm lsls ?reg_D reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

