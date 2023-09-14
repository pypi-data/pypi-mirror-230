
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


@title BXJ

@id 27

@desc {

	Branch and Exchange Jazelle attempts to change to Jazelle state. If the attempt fails, it branches to an address and instruction set specified by a register as though it were a BX instruction. In an implementation that includes the Virtualization Extensions, if HSTR.TJDBX is set to 1, execution of a BXJ instruction in a Non-secure mode other than Hyp mode generates a Hyp Trap exception. For more information see Trapping accesses to Jazelle functionality on page B1-1255.

}

@encoding (T1) {

	@word 1 1 1 1 0 0 1 1 1 1 0 0 Rm(4) 1 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0

	@syntax {

		@subid 95

		@conv {

			reg_M = Register(Rm)

		}

		@asm bxj reg_M

	}

	@hooks {

		fetch = help_fetching_with_instruction_bx_from_thumb
		link = handle_armv7_conditional_branch_from_register

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 0 1 0 1 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 Rm(4)

	@syntax {

		@subid 96

		@conv {

			reg_M = Register(Rm)

		}

		@asm bxj reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@hooks {

		fetch = help_fetching_with_instruction_bx_from_arm
		link = handle_armv7_conditional_branch_from_register

	}

}

