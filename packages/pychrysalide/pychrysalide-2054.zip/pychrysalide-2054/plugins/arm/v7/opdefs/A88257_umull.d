
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


@title UMULL

@id 252

@desc {

	Unsigned Multiply Long multiplies two 32-bit unsigned values to produce a 64-bit result. In ARM instructions, the condition flags can optionally be updated based on the result. Use of this option adversely affects performance on many processor implementations.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 1 1 1 0 1 0 Rn(4) RdLo(4) RdHi(4) 0 0 0 0 Rm(4)

	@syntax {

		@subid 764

		@conv {

			reg_DLO = Register(RdLo)
			reg_DHI = Register(RdHi)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm umull reg_DLO reg_DHI reg_N reg_M

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 0 1 0 0 S(1) RdHi(4) RdLo(4) Rm(4) 1 0 0 1 Rn(4)

	@syntax {

		@subid 765

		@assert {

			S == 0

		}

		@conv {

			reg_DLO = Register(RdLo)
			reg_DHI = Register(RdHi)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm umull reg_DLO reg_DHI reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 766

		@assert {

			S == 1

		}

		@conv {

			reg_DLO = Register(RdLo)
			reg_DHI = Register(RdHi)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm umulls reg_DLO reg_DHI reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

