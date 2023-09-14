
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


@title LDR (literal)

@id 59

@desc {

	Load Register (literal) calculates an address from the PC value and an immediate offset, loads a word from memory, and writes it to a register. For information about memory accesses see Memory accesses on page A8-294.

}

@encoding (t1) {

	@half 0 1 0 0 1 Rt(3) imm8(8)

	@syntax {

		@subid 179

		@conv {

			reg_T = Register(Rt)
			imm32 = ZeroExtend(imm8:'00', 32)

		}

		@asm ldr reg_T imm32

	}

	@hooks {

		fetch = help_fetching_with_instruction_ldr_literal_from_thumb
		post = post_process_ldr_instructions

	}

}

@encoding (T2) {

	@word 1 1 1 1 1 0 0 0 U(1) 1 0 1 1 1 1 1 Rt(4) imm12(12)

	@syntax {

		@subid 180

		@conv {

			reg_T = Register(Rt)
			imm32 = ZeroExtend(imm12, 32)

		}

		@asm ldr.w reg_T imm32

	}

	@hooks {

		fetch = help_fetching_with_instruction_ldr_literal_from_thumb
		post = post_process_ldr_instructions

	}

}

@encoding (A1) {

	@word cond(4) 0 1 0 1 U(1) 0 0 1 1 1 1 1 Rt(4) imm12(12)

	@syntax {

		@subid 181

		@conv {

			reg_T = Register(Rt)
			imm32 = ZeroExtend(imm12, 32)

		}

		@asm ldr reg_T imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@hooks {

		fetch = help_fetching_with_instruction_ldr_literal_from_arm
		post = post_process_ldr_instructions

	}

}

