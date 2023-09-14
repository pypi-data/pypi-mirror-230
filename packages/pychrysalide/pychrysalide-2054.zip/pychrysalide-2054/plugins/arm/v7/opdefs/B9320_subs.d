
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


@title SUBS PC, LR and related instructions (ARM)

@id 407

@desc {

	The SUBS PC, LR, #<const> instruction provides an exception return without the use of the stack. It subtracts the immediate constant from LR, branches to the resulting address, and also copies the SPSR to the CPSR. The ARM instruction set contains similar instructions based on other data-processing operations, or with a wider range of operands, or both. ARM deprecates using these other instructions, except for MOVS PC, LR. All of these instructions are: • UNDEFINED in Hyp mode • UNPREDICTABLE: — in the cases described in Restrictions on exception return instructions on page B9-1970 — if executed in Debug state.

}

@encoding (A1) {

	@word cond(4) 0 0 1 opcode(4) 1 Rn(4) 1 1 1 1 imm12(12)

	@syntax {

		@subid 3830

		@conv {

			reg_PC = Register(15)
			reg_LR = Register(14)
			imm32 = ARMExpandImm(imm12)

		}

		@asm subs reg_PC reg_LR imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

@encoding (A2) {

	@word cond(4) 0 0 0 opcode(4) 1 Rn(4) 1 1 1 1 imm5(5) type(2) 0 Rm(4)

	@syntax {

		@subid 3831

		@assert {

			opcode == 1111

		}

		@conv {

			reg_PC = Register(15)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm5)

		}

		@asm mvns reg_PC reg_M ?shift

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

