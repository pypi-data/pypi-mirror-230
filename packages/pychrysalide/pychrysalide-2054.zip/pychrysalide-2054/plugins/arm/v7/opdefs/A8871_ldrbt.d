
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


@title LDRBT

@id 66

@desc {

	Load Register Byte Unprivileged loads a byte from memory, zero-extends it to form a 32-bit word, and writes it to a register. For information about memory accesses see Memory accesses on page A8-294. The memory access is restricted as if the processor were running in User mode. This makes no difference if the processor is actually running in User mode. LDRBT is UNPREDICTABLE in Hyp mode. The Thumb instruction uses an offset addressing mode, that calculates the address used for the memory access from a base register value and an immediate offset, and leaves the base register unchanged. The ARM instruction uses a post-indexed addressing mode, that uses a base register value as the address for the memory access, and calculates a new address from a base register value and an offset and writes it back to the base register. The offset can be an immediate value or an optionally-shifted register value.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 0 0 0 0 1 Rn(4) Rt(4) 1 1 1 0 imm8(8)

	@syntax {

		@subid 202

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm8, 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm ldrbt reg_T maccess

	}

}

@encoding (A1) {

	@word cond(4) 0 1 0 0 U(1) 1 1 1 Rn(4) Rt(4) imm12(12)

	@syntax {

		@subid 203

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm12, 32)
			maccess = MemAccessPostIndexed(reg_N, imm32)

		}

		@asm ldrbt reg_T maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

@encoding (A2) {

	@word cond(4) 0 1 1 0 U(1) 1 1 1 Rn(4) Rt(4) imm5(5) type(2) 0 Rm(4)

	@syntax {

		@subid 204

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm5)
			maccess = MemAccessPostIndexedExtended(reg_N, reg_M, shift)

		}

		@asm ldrbt reg_T maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

