
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


@title CMN (immediate)

@id 33

@desc {

	Compare Negative (immediate) adds a register value and an immediate value. It updates the condition flags based on the result, and discards the result.

}

@encoding (T1) {

	@word 1 1 1 1 0 i(1) 0 1 0 0 0 1 Rn(4) 0 imm3(3) 1 1 1 1 imm8(8)

	@syntax {

		@subid 107

		@conv {

			reg_N = Register(Rn)
			imm32 = ThumbExpandImm(i:imm3:imm8)

		}

		@asm cmn reg_N imm32

	}

}

@encoding (A1) {

	@word cond(4) 0 0 1 1 0 1 1 1 Rn(4) 0 0 0 0 imm12(12)

	@syntax {

		@subid 108

		@conv {

			reg_N = Register(Rn)
			imm32 = ARMExpandImm(imm12)

		}

		@asm cmn reg_N imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

