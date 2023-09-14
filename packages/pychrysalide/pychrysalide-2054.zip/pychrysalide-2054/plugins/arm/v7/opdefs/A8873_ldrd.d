
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


@title LDRD (literal)

@id 68

@desc {

	Load Register Dual (literal) calculates an address from the PC value and an immediate offset, loads two words from memory, and writes them to two registers. For information about memory accesses see Memory accesses on page A8-294.

}

@encoding (T1) {

	@word 1 1 1 0 1 0 0 P(1) U(1) 1 W(1) 1 1 1 1 1 Rt(4) Rt2(4) imm8(8)

	@syntax {

		@subid 211

		@conv {

			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			imm32 = ZeroExtend(imm8:'00', 32)

		}

		@asm ldrd reg_T reg_T2 imm32

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 U(1) 1 0 0 1 1 1 1 Rt(4) imm4H(4) 1 1 0 1 imm4L(4)

	@syntax {

		@subid 212

		@conv {

			reg_T = Register(Rt)
			reg_T2 = NextRegister(Rt)
			imm32 = ZeroExtend(imm4H:imm4L, 32)

		}

		@asm ldrd reg_T reg_T2 imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

