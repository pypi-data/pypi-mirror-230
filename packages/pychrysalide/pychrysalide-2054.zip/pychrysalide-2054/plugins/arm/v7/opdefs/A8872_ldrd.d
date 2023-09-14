
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


@title LDRD (immediate)

@id 67

@desc {

	Load Register Dual (immediate) calculates an address from a base register value and an immediate offset, loads two words from memory, and writes them to two registers. It can use offset, post-indexed, or pre-indexed addressing. For information about memory accesses see Memory accesses on page A8-294.

}

@encoding (T1) {

	@word 1 1 1 0 1 0 0 P(1) U(1) 1 W(1) 1 Rn(4) Rt(4) Rt2(4) imm8(8)

	@syntax {

		@subid 205

		@assert {

			P == 1
			W == 0

		}

		@conv {

			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm8:'00', 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm ldrd reg_T reg_T2 maccess

	}

	@syntax {

		@subid 206

		@assert {

			P == 1
			W == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm8:'00', 32)
			maccess = MemAccessPreIndexed(reg_N, imm32)

		}

		@asm ldrd reg_T reg_T2 maccess

	}

	@syntax {

		@subid 207

		@assert {

			P == 0
			W == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm8:'00', 32)
			maccess = MemAccessPostIndexed(reg_N, imm32)

		}

		@asm ldrd reg_T reg_T2 maccess

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 P(1) U(1) 1 W(1) 0 Rn(4) Rt(4) imm4H(4) 1 1 0 1 imm4L(4)

	@syntax {

		@subid 208

		@assert {

			P == 1
			P == 1 && W == 0

		}

		@conv {

			reg_T = Register(Rt)
			reg_T2 = NextRegister(Rt)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm4H:imm4L, 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm ldrd reg_T reg_T2 maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 209

		@assert {

			P == 1
			P == 0 || W == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_T2 = NextRegister(Rt)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm4H:imm4L, 32)
			maccess = MemAccessPreIndexed(reg_N, imm32)

		}

		@asm ldrd reg_T reg_T2 maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 210

		@assert {

			P == 0
			P == 0 || W == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_T2 = NextRegister(Rt)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm4H:imm4L, 32)
			maccess = MemAccessPostIndexed(reg_N, imm32)

		}

		@asm ldrd reg_T reg_T2 maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

