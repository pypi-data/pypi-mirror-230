
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


@title MUL

@id 109

@desc {

	Multiply multiplies two register values. The least significant 32 bits of the result are written to the destination register. These 32 bits do not depend on whether the source register values are considered to be signed values or unsigned values. Optionally, it can update the condition flags based on the result. In the Thumb instruction set, this option is limited to only a few forms of the instruction. Use of this option adversely affects performance on many processor implementations.

}

@encoding (t1) {

	@half 0 1 0 0 0 0 1 1 0 1 Rn(3) Rdm(3)

	@syntax {

		@subid 340

		@conv {

			reg_D = Register(Rdm)
			reg_N = Register(Rn)
			reg_M = Register(Rdm)

		}

		@asm mul reg_D reg_N ?reg_M

	}

}

@encoding (T2) {

	@word 1 1 1 1 1 0 1 1 0 0 0 0 Rn(4) 1 1 1 1 Rd(4) 0 0 0 0 Rm(4)

	@syntax {

		@subid 341

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm mul reg_D reg_N ?reg_M

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 0 0 0 0 S(1) Rd(4) 0 0 0 0 Rm(4) 1 0 0 1 Rn(4)

	@syntax {

		@subid 342

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm mul reg_D reg_N ?reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 343

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm muls reg_D reg_N ?reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

