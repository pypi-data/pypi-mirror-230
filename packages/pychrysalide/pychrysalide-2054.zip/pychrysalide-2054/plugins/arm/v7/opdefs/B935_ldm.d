
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


@title LDM (exception return)

@id 392

@desc {

	Load Multiple (exception return) loads multiple registers from consecutive memory locations using an address from a base register. The SPSR of the current mode is copied to the CPSR. An address adjusted by the size of the data loaded can optionally be written back to the base register. The registers loaded include the PC. The word loaded for the PC is treated as an address and a branch occurs to that address. LDM (exception return) is: • UNDEFINED in Hyp mode • UNPREDICTABLE in: — the cases described in Restrictions on exception return instructions on page B9-1970 — Debug state.

}

@encoding (A1) {

	@word cond(4) 1 0 0 P(1) U(1) 1 W(1) 1 Rn(4) 1 register_list(15)

	@syntax {

		@subid 3794

		@assert {

			P == 0
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			registers = RegListWithPC(register_list)

		}

		@asm ldmda wb_reg registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 3795

		@assert {

			P == 1
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			registers = RegListWithPC(register_list)

		}

		@asm ldmdb wb_reg registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 3796

		@assert {

			P == 0
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			registers = RegListWithPC(register_list)

		}

		@asm ldmia wb_reg registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 3797

		@assert {

			P == 1
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			registers = RegListWithPC(register_list)

		}

		@asm ldmib wb_reg registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

