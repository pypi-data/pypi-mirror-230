
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


@title POP (ARM)

@id 127

@desc {

	Pop Multiple Registers loads multiple registers from the stack, loading from consecutive memory locations starting at the address in SP, and updates SP to point just above the loaded data.

}

@encoding (A1) {

	@word cond(4) 1 0 0 0 1 0 1 1 1 1 0 1 register_list(16)

	@syntax {

		@subid 398

		@conv {

			registers = RegList(register_list)

		}

		@asm pop registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@hooks {

		link = handle_armv7_return_from_pop

	}

}

@encoding (A2) {

	@word cond(4) 0 1 0 0 1 0 0 1 1 1 0 1 Rt(4) 0 0 0 0 0 0 0 0 0 1 0 0

	@syntax {

		@subid 399

		@conv {

			registers = SingleRegList(Rt)

		}

		@asm pop registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@hooks {

		link = handle_armv7_return_from_pop

	}

}

