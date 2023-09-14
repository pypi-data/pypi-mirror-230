
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


@title SMUAD

@id 182

@desc {

	Signed Dual Multiply Add performs two signed 16 × 16-bit multiplications. It adds the products together, and writes the result to the destination register. Optionally, the instruction can exchange the halfwords of the second operand before performing the arithmetic. This produces top × bottom and bottom × top multiplication. This instruction sets the Q flag if the addition overflows. The multiplications cannot overflow.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 1 1 0 0 1 0 Rn(4) 1 1 1 1 Rd(4) 0 0 0 M(1) Rm(4)

	@syntax {

		@subid 557

		@assert {

			M == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smuad ?reg_D reg_N reg_M

	}

	@syntax {

		@subid 558

		@assert {

			M == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smuadx ?reg_D reg_N reg_M

	}

}

@encoding (A1) {

	@word cond(4) 0 1 1 1 0 0 0 0 Rd(4) 1 1 1 1 Rm(4) 0 0 M(1) 1 Rn(4)

	@syntax {

		@subid 559

		@assert {

			M == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smuad ?reg_D reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 560

		@assert {

			M == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smuadx ?reg_D reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

