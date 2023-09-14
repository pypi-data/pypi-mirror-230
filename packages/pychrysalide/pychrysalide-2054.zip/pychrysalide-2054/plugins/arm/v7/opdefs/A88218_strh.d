
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


@title STRH (register)

@id 213

@desc {

	Store Register Halfword (register) calculates an address from a base register value and an offset register value, and stores a halfword from a register to memory. The offset register value can be shifted left by 0, 1, 2, or 3 bits. For information about memory accesses see Memory accesses on page A8-294.

}

@encoding (t1) {

	@half 0 1 0 1 0 0 1 Rm(3) Rn(3) Rt(3)

	@syntax {

		@subid 668

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessOffset(reg_N, reg_M)

		}

		@asm strh reg_T maccess

	}

}

@encoding (T2) {

	@word 1 1 1 1 1 0 0 0 0 0 1 0 Rn(4) Rt(4) 0 0 0 0 0 0 imm2(2) Rm(4)

	@syntax {

		@subid 669

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = FixedShift(SRType_LSL, imm2)
			maccess = MemAccessOffsetExtended(reg_N, reg_M, shift)

		}

		@asm strh.w reg_T maccess

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 P(1) U(1) 0 W(1) 0 Rn(4) Rt(4) 0 0 0 0 1 0 1 1 Rm(4)

	@syntax {

		@subid 670

		@assert {

			P == 1
			P == 1 && W == 0

		}

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessOffset(reg_N, reg_M)

		}

		@asm strh reg_T maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 671

		@assert {

			P == 1
			P == 0 || W == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessPreIndexed(reg_N, reg_M)

		}

		@asm strh reg_T maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 672

		@assert {

			P == 0
			P == 0 || W == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(reg_N, reg_M)

		}

		@asm strh reg_T maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

