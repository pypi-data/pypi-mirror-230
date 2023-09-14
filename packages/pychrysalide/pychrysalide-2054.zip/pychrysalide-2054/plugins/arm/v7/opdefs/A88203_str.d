
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


@title STR (immediate, Thumb)

@id 198

@desc {

	Store Register (immediate) calculates an address from a base register value and an immediate offset, and stores a word from a register to memory. It can use offset, post-indexed, or pre-indexed addressing. For information about memory accesses see Memory accesses on page A8-294.

}

@encoding (t1) {

	@half 0 1 1 0 0 imm5(5) Rn(3) Rt(3)

	@syntax {

		@subid 613

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm5:'00', 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm str reg_T maccess

	}

}

@encoding (t2) {

	@half 1 0 0 1 0 Rt(3) imm8(8)

	@syntax {

		@subid 614

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(13)
			imm32 = ZeroExtend(imm8:'00', 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm str reg_T maccess

	}

}

@encoding (T3) {

	@word 1 1 1 1 1 0 0 0 1 1 0 0 Rn(4) Rt(4) imm12(12)

	@syntax {

		@subid 615

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm12, 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm str.w reg_T maccess

	}

}

@encoding (T4) {

	@word 1 1 1 1 1 0 0 0 0 1 0 0 Rn(4) Rt(4) 1 P(1) U(1) W(1) imm8(8)

	@syntax {

		@subid 616

		@assert {

			P == 1
			W == 0

		}

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm8, 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm str reg_T maccess

	}

	@syntax {

		@subid 617

		@assert {

			P == 1
			W == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm8, 32)
			maccess = MemAccessPreIndexed(reg_N, imm32)

		}

		@asm str reg_T maccess

	}

	@syntax {

		@subid 618

		@assert {

			P == 0
			W == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm8, 32)
			maccess = MemAccessPostIndexed(reg_N, imm32)

		}

		@asm str reg_T maccess

	}

}

