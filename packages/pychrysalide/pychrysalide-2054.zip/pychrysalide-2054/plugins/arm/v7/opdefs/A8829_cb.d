
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


@title CBNZ, CBZ

@id 28

@desc {

	Compare and Branch on Nonzero and Compare and Branch on Zero compare the value in a register with zero, and conditionally branch forward a constant value. They do not affect the condition flags.

}

@encoding (t1) {

	@half 1 0 1 1 op(1) 0 i(1) 1 imm5(5) Rn(3)

	@syntax {

		@subid 97

		@assert {

			op == 0

		}

		@conv {

			reg_N = Register(Rn)
			imm32 = ZeroExtend(i:imm5:'0', 32)

		}

		@asm cbz reg_N imm32

	}

	@syntax {

		@subid 98

		@assert {

			op == 1

		}

		@conv {

			reg_N = Register(Rn)
			imm32 = ZeroExtend(i:imm5:'0', 32)

		}

		@asm cbnz reg_N imm32

	}

	@hooks {

		fetch = help_fetching_with_instruction_cb_n_z
		link = handle_comp_and_branch_if_true_as_link
		post = post_process_comp_and_branch_instructions

	}

}

