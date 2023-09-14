
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


@title ERET

@id 390

@desc {

	When executed in Hyp mode, Exception Return loads the PC from ELR_hyp and loads the CPSR from SPSR_hyp. When executed in a Secure or Non-secure PL1 mode, ERET behaves as: MOVS PC, • LR in the ARM instruction set, see SUBS PC, LR and related instructions (ARM) on page B9-2010 • the equivalent SUBS PC, LR, #0 in the Thumb instruction set, see SUBS PC, LR (Thumb) on page B9-2008. ERET is UNPREDICTABLE: • in the cases described in Restrictions on exception return instructions on page B9-1970 • if it is executed in Debug state. Note In an implementation that includes the Virtualization Extensions: • LR, #0 in the Thumb The T1 encoding of ERET is not a new encoding but, is the preferred synonym of SUBS PC, instruction set. See SUBS PC, LR (Thumb) on page B9-2008 for more information. • Because ERET is the preferred encoding, when decoding Thumb instructions, a disassembler will report an ERET where the original assembler code used SUBS PC, LR, #0.

}

@encoding (T1) {

	@word 1 1 1 1 0 0 1 1 1 1 0 1 1 1 1 0 1 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0

	@syntax {

		@subid 3790

		@asm eret

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 1 1 0

	@syntax {

		@subid 3791

		@asm eret

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

