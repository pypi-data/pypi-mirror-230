
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


@title STM (User registers)

@id 404

@desc {

	In a PL1 mode other than System mode, Store Multiple (user registers) stores multiple User mode registers to consecutive memory locations using an address from a base register. The processor reads the base register value normally, using the current mode to determine the correct Banked version of the register. This instruction cannot writeback to the base register. STM (User registers) is UNDEFINED in Hyp mode, and UNPREDICTABLE in User or System modes.

}

@encoding (A1) {

	@word cond(4) 1 0 0 P(1) U(1) 1 0 0 Rn(4) register_list(16)

	@syntax {

		@subid 3825

		@assert {

			P == 0
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			registers = RegList(register_list)

		}

		@asm stmda reg_N registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 3826

		@assert {

			P == 1
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			registers = RegList(register_list)

		}

		@asm stmdb reg_N registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 3827

		@assert {

			P == 0
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			registers = RegList(register_list)

		}

		@asm stmia reg_N registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 3828

		@assert {

			P == 1
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			registers = RegList(register_list)

		}

		@asm stmib reg_N registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

