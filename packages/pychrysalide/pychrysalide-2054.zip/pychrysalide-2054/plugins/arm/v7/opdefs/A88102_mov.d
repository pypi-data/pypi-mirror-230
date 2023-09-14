
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


@title MOV (immediate)

@id 97

@desc {

	Move (immediate) writes an immediate value to the destination register. It can optionally update the condition flags based on the value.

}

@encoding (t1) {

	@half 0 0 1 0 0 Rd(3) imm8(8)

	@syntax {

		@subid 312

		@conv {

			reg_D = Register(Rd)
			imm32 = ZeroExtend(imm8, 32)

		}

		@asm mov reg_D imm32

	}

}

@encoding (T2) {

	@word 1 1 1 1 0 i(1) 0 0 0 1 0 S(1) 1 1 1 1 0 imm3(3) Rd(4) imm8(8)

	@syntax {

		@subid 313

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			const = ThumbExpandImm_C(i:imm3:imm8, APSR_C)

		}

		@asm mov.w reg_D const

	}

	@syntax {

		@subid 314

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			const = ThumbExpandImm_C(i:imm3:imm8, APSR_C)

		}

		@asm movs.w reg_D const

	}

}

@encoding (T3) {

	@word 1 1 1 1 0 i(1) 1 0 0 1 0 0 imm4(4) 0 imm3(3) Rd(4) imm8(8)

	@syntax {

		@subid 315

		@conv {

			reg_D = Register(Rd)
			imm32 = ZeroExtend(imm4:i:imm3:imm8, 32)

		}

		@asm movw reg_D imm32

	}

}

@encoding (A1) {

	@word cond(4) 0 0 1 1 1 0 1 S(1) 0 0 0 0 Rd(4) imm12(12)

	@syntax {

		@subid 316

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			const = ARMExpandImm_C(imm12, APSR_C)

		}

		@asm mov reg_D const

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 317

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			const = ARMExpandImm_C(imm12, APSR_C)

		}

		@asm movs reg_D const

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

@encoding (A2) {

	@word cond(4) 0 0 1 1 0 0 0 0 imm4(4) Rd(4) imm12(12)

	@syntax {

		@subid 318

		@conv {

			reg_D = Register(Rd)
			imm32 = ZeroExtend(imm4:imm12, 32)

		}

		@asm movw reg_D imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

