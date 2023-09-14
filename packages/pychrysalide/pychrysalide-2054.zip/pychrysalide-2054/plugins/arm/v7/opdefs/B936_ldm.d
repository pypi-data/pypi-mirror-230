
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


@title LDM (User registers)

@id 393

@desc {

	In a PL1 mode other than System mode, Load Multiple (User registers) loads multiple User mode registers from consecutive memory locations using an address from a base register. The registers loaded cannot include the PC. The processor reads the base register value normally, using the current mode to determine the correct Banked version of the register. This instruction cannot writeback to the base register. LDM (user registers) is UNDEFINED in Hyp mode, and UNPREDICTABLE in User and System modes.

}

@encoding (A1) {

	@word cond(4) 1 0 0 P(1) U(1) 1 0 1 Rn(4) 0 register_list(15)

	@syntax {

		@subid 3798

		@assert {

			P == 0
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			registers = RegListWithoutPC(register_list)

		}

		@asm ldmda reg_N registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 3799

		@assert {

			P == 1
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			registers = RegListWithoutPC(register_list)

		}

		@asm ldmdb reg_N registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 3800

		@assert {

			P == 0
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			registers = RegListWithoutPC(register_list)

		}

		@asm ldmia reg_N registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 3801

		@assert {

			P == 1
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			registers = RegListWithoutPC(register_list)

		}

		@asm ldmib reg_N registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

