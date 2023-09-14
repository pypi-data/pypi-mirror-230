
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


@title UMLAL

@id 251

@desc {

	Unsigned Multiply Accumulate Long multiplies two unsigned 32-bit values to produce a 64-bit value, and accumulates this with a 64-bit value. In ARM instructions, the condition flags can optionally be updated based on the result. Use of this option adversely affects performance on many processor implementations.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 1 1 1 1 1 0 Rn(4) RdLo(4) RdHi(4) 0 0 0 0 Rm(4)

	@syntax {

		@subid 761

		@conv {

			reg_DLO = Register(RdLo)
			reg_DHI = Register(RdHi)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm umlal reg_DLO reg_DHI reg_N reg_M

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 0 1 0 1 S(1) RdHi(4) RdLo(4) Rm(4) 1 0 0 1 Rn(4)

	@syntax {

		@subid 762

		@assert {

			S == 0

		}

		@conv {

			reg_DLO = Register(RdLo)
			reg_DHI = Register(RdHi)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm umlal reg_DLO reg_DHI reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 763

		@assert {

			S == 1

		}

		@conv {

			reg_DLO = Register(RdLo)
			reg_DHI = Register(RdHi)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm umlals reg_DLO reg_DHI reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

