
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


@title SMLAWB, SMLAWT

@id 176

@desc {

	Signed Multiply Accumulate (word by halfword) performs a signed multiply accumulate operation. The multiply acts on a signed 32-bit quantity and a signed 16-bit quantity. The signed 16-bit quantity is taken from either the bottom or the top half of its source register. The other half of the second source register is ignored. The top 32 bits of the 48-bit product are added to a 32-bit accumulate value and the result is written to the destination register. The bottom 16 bits of the 48-bit product are ignored. If overflow occurs during the addition of the accumulate value, the instruction sets the Q flag in the APSR. No overflow can occur during the multiplication.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 1 1 0 0 1 1 Rn(4) Ra(4) Rd(4) 0 0 0 M(1) Rm(4)

	@syntax {

		@subid 533

		@assert {

			M == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smlawt reg_D reg_N reg_M reg_A

	}

	@syntax {

		@subid 534

		@assert {

			M == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smlawb reg_D reg_N reg_M reg_A

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 0 1 0 Rd(4) Ra(4) Rm(4) 1 M(1) 0 0 Rn(4)

	@syntax {

		@subid 535

		@assert {

			M == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smlawt reg_D reg_N reg_M reg_A

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 536

		@assert {

			M == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smlawb reg_D reg_N reg_M reg_A

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

