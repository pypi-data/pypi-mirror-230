
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


@title RSB (immediate)

@id 147

@desc {

	Reverse Subtract (immediate) subtracts a register value from an immediate value, and writes the result to the destination register. It can optionally update the condition flags based on the result.

}

@encoding (t1) {

	@half 0 1 0 0 0 0 1 0 0 1 Rn(3) Rd(3)

	@syntax {

		@subid 449

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			imm32 = Zeros(32)

		}

		@asm rsb ?reg_D reg_N imm32

	}

}

@encoding (T2) {

	@word 1 1 1 1 0 i(1) 0 1 1 1 0 S(1) Rn(4) 0 imm3(3) Rd(4) imm8(8)

	@syntax {

		@subid 450

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			imm32 = ThumbExpandImm(i:imm3:imm8)

		}

		@asm rsb.w ?reg_D reg_N imm32

	}

	@syntax {

		@subid 451

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			imm32 = ThumbExpandImm(i:imm3:imm8)

		}

		@asm rsbs.w ?reg_D reg_N imm32

	}

}

@encoding (A1) {

	@word cond(4) 0 0 1 0 0 1 1 S(1) Rn(4) Rd(4) imm12(12)

	@syntax {

		@subid 452

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			imm32 = ARMExpandImm(imm12)

		}

		@asm rsb ?reg_D reg_N imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 453

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			imm32 = ARMExpandImm(imm12)

		}

		@asm rsbs ?reg_D reg_N imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

