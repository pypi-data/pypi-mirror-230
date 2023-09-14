
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


@title SMLALBB, SMLALBT, SMLALTB, SMLALTT

@id 174

@desc {

	Signed Multiply Accumulate Long (halfwords) multiplies two signed 16-bit values to produce a 32-bit value, and accumulates this with a 64-bit value. The multiply acts on two signed 16-bit quantities, taken from either the bottom or the top half of their respective source registers. The other halves of these source registers are ignored. The 32-bit product is sign-extended and accumulated with a 64-bit accumulate value. Overflow is possible during this instruction, but only as a result of the 64-bit addition. This overflow is not detected if it occurs. Instead, the result wraps around modulo 264.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 1 1 1 1 0 0 Rn(4) RdLo(4) RdHi(4) 1 0 N(1) M(1) Rm(4)

	@syntax {

		@subid 521

		@assert {

			N == 1
			M == 1

		}

		@conv {

			reg_DLO = Register(RdLo)
			reg_DHI = Register(RdHi)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smlaltt reg_DLO reg_DHI reg_N reg_M

	}

	@syntax {

		@subid 522

		@assert {

			N == 1
			M == 0

		}

		@conv {

			reg_DLO = Register(RdLo)
			reg_DHI = Register(RdHi)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smlaltb reg_DLO reg_DHI reg_N reg_M

	}

	@syntax {

		@subid 523

		@assert {

			N == 0
			M == 1

		}

		@conv {

			reg_DLO = Register(RdLo)
			reg_DHI = Register(RdHi)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smlalbt reg_DLO reg_DHI reg_N reg_M

	}

	@syntax {

		@subid 524

		@assert {

			N == 0
			M == 0

		}

		@conv {

			reg_DLO = Register(RdLo)
			reg_DHI = Register(RdHi)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smlalbb reg_DLO reg_DHI reg_N reg_M

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 1 0 0 RdHi(4) RdLo(4) Rm(4) 1 M(1) N(1) 0 Rn(4)

	@syntax {

		@subid 525

		@assert {

			N == 1
			M == 1

		}

		@conv {

			reg_DLO = Register(RdLo)
			reg_DHI = Register(RdHi)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smlaltt reg_DLO reg_DHI reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 526

		@assert {

			N == 1
			M == 0

		}

		@conv {

			reg_DLO = Register(RdLo)
			reg_DHI = Register(RdHi)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smlaltb reg_DLO reg_DHI reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 527

		@assert {

			N == 0
			M == 1

		}

		@conv {

			reg_DLO = Register(RdLo)
			reg_DHI = Register(RdHi)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smlalbt reg_DLO reg_DHI reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 528

		@assert {

			N == 0
			M == 0

		}

		@conv {

			reg_DLO = Register(RdLo)
			reg_DHI = Register(RdHi)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm smlalbb reg_DLO reg_DHI reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

