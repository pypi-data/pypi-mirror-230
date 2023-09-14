
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


@title ADC (immediate)

@id 0

@desc {

	Add with Carry (immediate) adds an immediate value and the Carry flag value to a register value, and writes the result to the destination register. It can optionally update the condition flags based on the result.

}

@encoding (T1) {

	@word 1 1 1 1 0 i(1) 0 1 0 1 0 S(1) Rn(4) 0 imm3(3) Rd(4) imm8(8)

	@syntax {

		@subid 0

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			imm32 = ThumbExpandImm(i:imm3:imm8)

		}

		@asm adc ?reg_D reg_N imm32

	}

	@syntax {

		@subid 1

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			imm32 = ThumbExpandImm(i:imm3:imm8)

		}

		@asm adcs ?reg_D reg_N imm32

	}

}

@encoding (A1) {

	@word cond(4) 0 0 1 0 1 0 1 S(1) Rn(4) Rd(4) imm12(12)

	@syntax {

		@subid 2

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			imm32 = ARMExpandImm(imm12)

		}

		@asm adc ?reg_D reg_N imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 3

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			imm32 = ARMExpandImm(imm12)

		}

		@asm adcs ?reg_D reg_N imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

