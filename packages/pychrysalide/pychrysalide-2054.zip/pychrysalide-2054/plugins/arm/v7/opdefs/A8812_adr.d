
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


@title ADR

@id 11

@desc {

	This instruction adds an immediate value to the PC value to form a PC-relative address, and writes the result to the destination register.

}

@encoding (t1) {

	@half 1 0 1 0 0 Rd(3) imm8(8)

	@syntax {

		@subid 39

		@conv {

			reg_D = Register(Rd)
			imm32 = ZeroExtend(imm8:'00', 32)

		}

		@asm adr reg_D imm32

	}

}

@encoding (T2) {

	@word 1 1 1 1 0 i(1) 1 0 1 0 1 0 1 1 1 1 0 imm3(3) Rd(4) imm8(8)

	@syntax {

		@subid 40

		@conv {

			reg_D = Register(Rd)
			imm32 = ZeroExtend(i:imm3:imm8, 32)

		}

		@asm adr.w reg_D imm32

	}

}

@encoding (T3) {

	@word 1 1 1 1 0 i(1) 1 0 0 0 0 0 1 1 1 1 0 imm3(3) Rd(4) imm8(8)

	@syntax {

		@subid 41

		@conv {

			reg_D = Register(Rd)
			imm32 = ZeroExtend(i:imm3:imm8, 32)

		}

		@asm adr.w reg_D imm32

	}

}

@encoding (A1) {

	@word cond(4) 0 0 1 0 1 0 0 0 1 1 1 1 Rd(4) imm12(12)

	@syntax {

		@subid 42

		@conv {

			reg_D = Register(Rd)
			imm32 = ARMExpandImm(imm12)

		}

		@asm adr reg_D imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

@encoding (A2) {

	@word cond(4) 0 0 1 0 0 1 0 0 1 1 1 1 Rd(4) imm12(12)

	@syntax {

		@subid 43

		@conv {

			reg_D = Register(Rd)
			imm32 = ARMExpandImm(imm12)

		}

		@asm adr reg_D imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

