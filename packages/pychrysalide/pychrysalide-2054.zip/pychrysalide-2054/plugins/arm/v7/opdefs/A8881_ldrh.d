
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


@title LDRH (literal)

@id 76

@desc {

	Load Register Halfword (literal) calculates an address from the PC value and an immediate offset, loads a halfword from memory, zero-extends it to form a 32-bit word, and writes it to a register. For information about memory accesses see Memory accesses on page A8-294.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 0 U(1) 0 1 1 1 1 1 1 Rt(4) imm12(12)

	@syntax {

		@subid 232

		@conv {

			reg_T = Register(Rt)
			imm32 = ZeroExtend(imm12, 32)

		}

		@asm ldrh reg_T imm32

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 P(1) U(1) 1 W(1) 1 1 1 1 1 Rt(4) imm4H(4) 1 0 1 1 imm4L(4)

	@syntax {

		@subid 233

		@conv {

			reg_T = Register(Rt)
			imm32 = ZeroExtend(imm4H:imm4L, 32)

		}

		@asm ldrh reg_T imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

