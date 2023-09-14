
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


@title ADD (register, Thumb)

@id 5

@desc {

	This instruction adds a register value and an optionally-shifted register value, and writes the result to the destination register. It can optionally update the condition flags based on the result.

}

@encoding (t1) {

	@half 0 0 0 1 1 0 0 Rm(3) Rn(3) Rd(3)

	@syntax {

		@subid 18

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm add ?reg_D reg_N reg_M

	}

}

@encoding (t2) {

	@half 0 1 0 0 0 1 0 0 DN(1) Rm(4) Rdn(3)

	@syntax {

		@subid 19

		@conv {

			reg_D = Register(DN:Rdn)
			reg_N = Register(DN:Rdn)
			reg_M = Register(Rm)

		}

		@asm add ?reg_D reg_N reg_M

	}

}

@encoding (T3) {

	@word 1 1 1 0 1 0 1 1 0 0 0 S(1) Rn(4) 0 imm3(3) Rd(4) imm2(2) type(2) Rm(4)

	@syntax {

		@subid 20

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm3:imm2)

		}

		@asm add.w ?reg_D reg_N reg_M ?shift

	}

	@syntax {

		@subid 21

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(type, imm3:imm2)

		}

		@asm adds.w ?reg_D reg_N reg_M ?shift

	}

}

