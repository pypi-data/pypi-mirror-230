
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


@title ADD (SP plus immediate)

@id 8

@desc {

	This instruction adds an immediate value to the SP value, and writes the result to the destination register.

}

@encoding (t1) {

	@half 1 0 1 0 1 Rd(3) imm8(8)

	@syntax {

		@subid 26

		@conv {

			reg_D = Register(Rd)
			reg_SP = Register(13)
			imm32 = ZeroExtend(imm8:'00', 32)

		}

		@asm add ?reg_D reg_SP imm32

	}

}

@encoding (t2) {

	@half 1 0 1 1 0 0 0 0 0 imm7(7)

	@syntax {

		@subid 27

		@conv {

			reg_D = Register(13)
			reg_SP = Register(13)
			imm32 = ZeroExtend(imm7:'00', 32)

		}

		@asm add ?reg_D reg_SP imm32

	}

}

@encoding (T3) {

	@word 1 1 1 1 0 i(1) 0 1 0 0 0 S(1) 1 1 0 1 0 imm3(3) Rd(4) imm8(8)

	@syntax {

		@subid 28

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_SP = Register(13)
			imm32 = ThumbExpandImm(i:imm3:imm8)

		}

		@asm add.w ?reg_D reg_SP imm32

	}

	@syntax {

		@subid 29

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_SP = Register(13)
			imm32 = ThumbExpandImm(i:imm3:imm8)

		}

		@asm adds.w ?reg_D reg_SP imm32

	}

}

@encoding (T4) {

	@word 1 1 1 1 0 i(1) 1 0 0 0 0 0 1 1 0 1 0 imm3(3) Rd(4) imm8(8)

	@syntax {

		@subid 30

		@conv {

			reg_D = Register(Rd)
			reg_SP = Register(13)
			imm32 = ZeroExtend(i:imm3:imm8, 32)

		}

		@asm addw ?reg_D reg_SP imm32

	}

}

@encoding (A1) {

	@word cond(4) 0 0 1 0 1 0 0 S(1) 1 1 0 1 Rd(4) imm12(12)

	@syntax {

		@subid 31

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_SP = Register(13)
			imm32 = ARMExpandImm(imm12)

		}

		@asm add ?reg_D reg_SP imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 32

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_SP = Register(13)
			imm32 = ARMExpandImm(imm12)

		}

		@asm adds ?reg_D reg_SP imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

