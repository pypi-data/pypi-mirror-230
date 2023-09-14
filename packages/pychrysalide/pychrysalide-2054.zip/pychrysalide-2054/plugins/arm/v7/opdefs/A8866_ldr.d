
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


@title LDR (register, ARM)

@id 61

@desc {

	Load Register (register) calculates an address from a base register value and an offset register value, loads a word from memory, and writes it to a register. The offset register value can optionally be shifted. For information about memory accesses, see Memory accesses on page A8-294.

}

@encoding (A1) {

	@word cond(4) 0 1 1 P(1) U(1) 0 W(1) 1 Rn(4) Rt(4) imm5(5) type(2) 0 Rm(4)

	@syntax {

		@subid 184

		@assert {

			P == 1
			P == 1 && W == 0

		}

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm5)
			maccess = MemAccessOffsetExtended(reg_N, reg_M, shift)

		}

		@asm ldr reg_T maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 185

		@assert {

			P == 1
			P == 0 || W == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm5)
			maccess = MemAccessPreIndexedExtended(reg_N, reg_M, shift)

		}

		@asm ldr reg_T maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 186

		@assert {

			P == 0
			P == 0 || W == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm5)
			maccess = MemAccessPostIndexedExtended(reg_N, reg_M, shift)

		}

		@asm ldr reg_T maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

