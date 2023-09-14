
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


@title BL, BLX (immediate)

@id 24

@desc {

	Branch with Link calls a subroutine at a PC-relative address. Branch with Link and Exchange Instruction Sets (immediate) calls a subroutine at a PC-relative address, and changes instruction set from ARM to Thumb, or from Thumb to ARM.

}

@encoding (T1) {

	@word 1 1 1 1 0 S(1) imm10(10) 1 1 J1(1) 1 J2(1) imm11(11)

	@syntax {

		@subid 87

		@conv {

			I1 = NOT(J1 EOR S)
			I2 = NOT(J2 EOR S)
			imm32 = SignExtend(S:I1:I2:imm10:imm11:'0', 32, 24)

		}

		@asm bl imm32

	}

	@hooks {

		fetch = help_fetching_with_instruction_bl_from_thumb
		link = handle_call_as_link
		post = post_process_branch_and_link_instructions

	}

}

@encoding (T2) {

	@word 1 1 1 1 0 S(1) imm10H(10) 1 1 J1(1) 0 J2(1) imm10L(10) H(1)

	@syntax {

		@subid 88

		@conv {

			I1 = NOT(J1 EOR S)
			I2 = NOT(J2 EOR S)
			imm32 = SignExtend(S:I1:I2:imm10H:imm10L:'00', 32, 24)

		}

		@asm blx imm32

	}

	@hooks {

		fetch = help_fetching_with_instruction_blx_from_thumb
		link = handle_call_as_link
		post = post_process_branch_and_link_instructions

	}

}

@encoding (A1) {

	@word cond(4) 1 0 1 1 imm24(24)

	@syntax {

		@subid 89

		@conv {

			imm32 = SignExtend(imm24:'00', 32, 25)

		}

		@asm bl imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@hooks {

		fetch = help_fetching_with_instruction_bl_from_arm
		link = handle_call_as_link
		post = post_process_branch_and_link_instructions

	}

}

@encoding (A2) {

	@word 1 1 1 1 1 0 1 H(1) imm24(24)

	@syntax {

		@subid 90

		@conv {

			imm32 = SignExtend(imm24:H:'0', 32, 25)

		}

		@asm blx imm32

	}

	@hooks {

		fetch = help_fetching_with_instruction_blx_from_arm
		link = handle_call_as_link
		post = post_process_branch_and_link_instructions

	}

}

