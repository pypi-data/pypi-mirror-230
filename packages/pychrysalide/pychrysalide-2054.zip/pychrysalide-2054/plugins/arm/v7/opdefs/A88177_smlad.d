
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


@title SMLAD

@id 172

@desc {

	Signed Multiply Accumulate Dual performs two signed 16 × 16-bit multiplications. It adds the products to a 32-bit accumulate operand. Optionally, the instruction can exchange the halfwords of the second operand before performing the arithmetic. This produces top × bottom and bottom × top multiplication. This instruction sets the Q flag if the accumulate operation overflows. Overflow cannot occur during the multiplications.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 1 1 0 0 1 0 Rn(4) Ra(4) Rd(4) 0 0 0 M(1) Rm(4)

	@syntax {

		@subid 514

		@assert {

			M == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smlad reg_D reg_N reg_M reg_A

	}

	@syntax {

		@subid 515

		@assert {

			M == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smladx reg_D reg_N reg_M reg_A

	}

}

@encoding (A1) {

	@word cond(4) 0 1 1 1 0 0 0 0 Rd(4) Ra(4) Rm(4) 0 0 M(1) 1 Rn(4)

	@syntax {

		@subid 516

		@assert {

			M == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smlad reg_D reg_N reg_M reg_A

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 517

		@assert {

			M == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			reg_A = Register(Ra)

		}

		@asm smladx reg_D reg_N reg_M reg_A

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

