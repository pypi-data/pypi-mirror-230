
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


@title SUB (immediate, Thumb)

@id 216

@desc {

	This instruction subtracts an immediate value from a register value, and writes the result to the destination register. It can optionally update the condition flags based on the result.

}

@encoding (t1) {

	@half 0 0 0 1 1 1 1 imm3(3) Rn(3) Rd(3)

	@syntax {

		@subid 679

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm3, 32)

		}

		@asm sub ?reg_D reg_N imm32

	}

}

@encoding (t2) {

	@half 0 0 1 1 1 Rdn(3) imm8(8)

	@syntax {

		@subid 680

		@conv {

			reg_D = Register(Rdn)
			reg_N = Register(Rdn)
			imm32 = ZeroExtend(imm8, 32)

		}

		@asm sub ?reg_D reg_N imm32

	}

}

@encoding (T3) {

	@word 1 1 1 1 0 i(1) 0 1 1 0 1 S(1) Rn(4) 0 imm3(3) Rd(4) imm8(8)

	@syntax {

		@subid 681

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			imm32 = ThumbExpandImm(i:imm3:imm8)

		}

		@asm sub.w ?reg_D reg_N imm32

	}

	@syntax {

		@subid 682

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			imm32 = ThumbExpandImm(i:imm3:imm8)

		}

		@asm subs.w ?reg_D reg_N imm32

	}

}

@encoding (T4) {

	@word 1 1 1 1 0 i(1) 1 0 1 0 1 0 Rn(4) 0 imm3(3) Rd(4) imm8(8)

	@syntax {

		@subid 683

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(i:imm3:imm8, 32)

		}

		@asm subw ?reg_D reg_N imm32

	}

}

