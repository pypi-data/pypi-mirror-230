
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


@title RRX

@id 146

@desc {

	Rotate Right with Extend provides the value of the contents of a register shifted right by one place, with the Carry flag shifted into bit[31]. RRX can optionally update the condition flags based on the result. In that case, bit[0] is shifted into the Carry flag.

}

@encoding (T1) {

	@word 1 1 1 0 1 0 1 0 0 1 0 S(1) 1 1 1 1 0 0 0 0 Rd(4) 0 0 1 1 Rm(4)

	@syntax {

		@subid 445

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)

		}

		@asm rrx ?reg_D reg_M

	}

	@syntax {

		@subid 446

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)

		}

		@asm rrxs ?reg_D reg_M

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 1 0 1 S(1) 0 0 0 0 Rd(4) 0 0 0 0 0 1 1 0 Rm(4)

	@syntax {

		@subid 447

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)

		}

		@asm rrx ?reg_D reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 448

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)

		}

		@asm rrxs ?reg_D reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

