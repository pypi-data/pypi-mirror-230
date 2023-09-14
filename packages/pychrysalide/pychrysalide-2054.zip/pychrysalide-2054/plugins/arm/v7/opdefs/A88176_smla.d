
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


@title SMLABB, SMLABT, SMLATB, SMLATT

@id 171

@desc {

	Signed Multiply Accumulate (halfwords) performs a signed multiply accumulate operation. The multiply acts on two signed 16-bit quantities, taken from either the bottom or the top half of their respective source registers. The other halves of these source registers are ignored. The 32-bit product is added to a 32-bit accumulate value and the result is written to the destination register. If overflow occurs during the addition of the accumulate value, the instruction sets the Q flag in the APSR. It is not possible for overflow to occur during the multiplication.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 1 1 0 0 0 1 Rn(4) Ra(4) Rd(4) 0 0 N(1) M(1) Rm(4)

	@syntax {

		@subid 506

		@assert {

			N == 1
			M == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smlatt reg_D reg_N reg_M reg_A

	}

	@syntax {

		@subid 507

		@assert {

			N == 1
			M == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smlatb reg_D reg_N reg_M reg_A

	}

	@syntax {

		@subid 508

		@assert {

			N == 0
			M == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smlabt reg_D reg_N reg_M reg_A

	}

	@syntax {

		@subid 509

		@assert {

			N == 0
			M == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smlabb reg_D reg_N reg_M reg_A

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 0 0 0 Rd(4) Ra(4) Rm(4) 1 M(1) N(1) 0 Rn(4)

	@syntax {

		@subid 510

		@assert {

			N == 1
			M == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smlatt reg_D reg_N reg_M reg_A

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 511

		@assert {

			N == 1
			M == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smlatb reg_D reg_N reg_M reg_A

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 512

		@assert {

			N == 0
			M == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smlabt reg_D reg_N reg_M reg_A

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 513

		@assert {

			N == 0
			M == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smlabb reg_D reg_N reg_M reg_A

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

