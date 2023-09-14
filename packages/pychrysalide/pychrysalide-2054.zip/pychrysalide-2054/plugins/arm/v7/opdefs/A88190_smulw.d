
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


@title SMULWB, SMULWT

@id 185

@desc {

	Signed Multiply (word by halfword) multiplies a signed 32-bit quantity and a signed 16-bit quantity. The signed 16-bit quantity is taken from either the bottom or the top half of its source register. The other half of the second source register is ignored. The top 32 bits of the 48-bit product are written to the destination register. The bottom 16 bits of the 48-bit product are ignored. No overflow is possible during this instruction.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 1 1 0 0 1 1 Rn(4) 1 1 1 1 Rd(4) 0 0 0 M(1) Rm(4)

	@syntax {

		@subid 572

		@assert {

			M == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smulwt ?reg_D reg_N reg_M

	}

	@syntax {

		@subid 573

		@assert {

			M == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smulwb ?reg_D reg_N reg_M

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 0 1 0 Rd(4) 0 0 0 0 Rm(4) 1 M(1) 1 0 Rn(4)

	@syntax {

		@subid 574

		@assert {

			M == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smulwt ?reg_D reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 575

		@assert {

			M == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smulwb ?reg_D reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

