
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


@title B

@id 17

@desc {

	Branch causes a branch to a target address.

}

@encoding (t1) {

	@half 1 1 0 1 cond(4) imm8(8)

	@syntax {

		@subid 65

		@conv {

			imm32 = SignExtend(imm8:'0', 32, 8)

		}

		@asm b imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@hooks {

		fetch = help_fetching_with_instruction_b_from_thumb
		link = handle_arm_conditional_branch_as_link
		post = post_process_branch_instructions

	}

}

@encoding (t2) {

	@half 1 1 1 0 0 imm11(11)

	@syntax {

		@subid 66

		@conv {

			imm32 = SignExtend(imm11:'0', 32, 11)

		}

		@asm b imm32

	}

	@hooks {

		fetch = help_fetching_with_instruction_b_from_thumb
		link = handle_arm_conditional_branch_as_link
		post = post_process_branch_instructions

	}

}

@encoding (T3) {

	@word 1 1 1 1 0 S(1) cond(4) imm6(6) 1 0 J1(1) 0 J2(1) imm11(11)

	@syntax {

		@subid 67

		@conv {

			imm32 = SignExtend(S:J2:J1:imm6:imm11:'0', 32, 20)

		}

		@asm b imm32

		@rules {

			check g_arm_instruction_set_cond(cond)
			check g_armv7_instruction_extend_keyword(".W")

		}

	}

	@hooks {

		fetch = help_fetching_with_instruction_b_from_thumb
		link = handle_arm_conditional_branch_as_link
		post = post_process_branch_instructions

	}

}

@encoding (T4) {

	@word 1 1 1 1 0 S(1) imm10(10) 1 0 J1(1) 1 J2(1) imm11(11)

	@syntax {

		@subid 68

		@conv {

			I1 = NOT(J1 EOR S)
			I2 = NOT(J2 EOR S)
			imm32 = SignExtend(S:I1:I2:imm10:imm11:'0', 32, 24)

		}

		@asm b.w imm32

	}

	@hooks {

		fetch = help_fetching_with_instruction_b_from_thumb
		link = handle_arm_conditional_branch_as_link
		post = post_process_branch_instructions

	}

}

@encoding (A1) {

	@word cond(4) 1 0 1 0 imm24(24)

	@syntax {

		@subid 69

		@conv {

			imm32 = SignExtend(imm24:'00', 32, 25)

		}

		@asm b imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@hooks {

		fetch = help_fetching_with_instruction_b_from_arm
		link = handle_arm_conditional_branch_as_link
		post = post_process_branch_instructions

	}

}

