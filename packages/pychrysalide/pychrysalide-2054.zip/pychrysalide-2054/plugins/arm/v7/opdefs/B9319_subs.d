
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


@title SUBS PC, LR (Thumb)

@id 406

@desc {

	The SUBS PC, LR, #<const> instruction provides an exception return without the use of the stack. It subtracts the immediate constant from LR, branches to the resulting address, and also copies the SPSR to the CPSR. Note • The instruction SUBS PC, LR, #0 is equivalent to MOVS PC, LR and ERET. • For an implementation that includes the Virtualization Extensions, ERET is the preferred disassembly of the T1 encoding defined in this section. Therefore, a disassembler might report an ERET where the original assembler code used SUBS PC, LR, #0. When executing in Hyp mode: • the encoding for SUBS PC, LR, #0 is the encoding of the ERET instruction, see ERET on page B9-1980 • SUBS PC, LR, #<const> with a nonzero constant is UNDEFINED. SUBS PC, LR, #<const> is UNPREDICTABLE: • in the cases described in Restrictions on exception return instructions on page B9-1970 • if it is executed in Debug state.

}

@encoding (T1) {

	@word 1 1 1 1 0 0 1 1 1 1 0 1 1 1 1 0 1 0 0 0 1 1 1 1 imm8(8)

	@syntax {

		@subid 3829

		@conv {

			reg_PC = Register(15)
			reg_LR = Register(14)
			imm32 = ZeroExtend(imm8, 32)

		}

		@asm subs reg_PC reg_LR imm32

	}

}

