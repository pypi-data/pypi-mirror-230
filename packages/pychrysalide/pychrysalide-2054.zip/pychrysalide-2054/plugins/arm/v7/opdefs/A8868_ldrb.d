
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


@title LDRB (immediate, ARM)

@id 63

@desc {

	Load Register Byte (immediate) calculates an address from a base register value and an immediate offset, loads a byte from memory, zero-extends it to form a 32-bit word, and writes it to a register. It can use offset, post-indexed, or pre-indexed addressing. For information about memory accesses see Memory accesses on page A8-294.

}

@encoding (A1) {

	@word cond(4) 0 1 0 P(1) U(1) 1 W(1) 1 Rn(4) Rt(4) imm12(12)

	@syntax {

		@subid 192

		@assert {

			P == 1
			P == 1 && W == 0

		}

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm12, 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm ldrb reg_T maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 193

		@assert {

			P == 1
			P == 0 || W == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm12, 32)
			maccess = MemAccessPreIndexed(reg_N, imm32)

		}

		@asm ldrb reg_T maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 194

		@assert {

			P == 0
			P == 0 || W == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm12, 32)
			maccess = MemAccessPostIndexed(reg_N, imm32)

		}

		@asm ldrb reg_T maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

