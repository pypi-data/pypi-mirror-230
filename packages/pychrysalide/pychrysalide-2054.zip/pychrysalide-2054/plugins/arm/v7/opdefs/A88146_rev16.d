
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


@title REV16

@id 141

@desc {

	Byte-Reverse Packed Halfword reverses the byte order in each16-bit halfword of a 32-bit register.

}

@encoding (t1) {

	@half 1 0 1 1 1 0 1 0 0 1 Rm(3) Rd(3)

	@syntax {

		@subid 430

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)

		}

		@asm rev16 reg_D reg_M

	}

}

@encoding (T2) {

	@word 1 1 1 1 1 0 1 0 1 0 0 1 Rm(4) 1 1 1 1 Rd(4) 1 0 0 1 Rm(4)

	@syntax {

		@subid 431

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)

		}

		@asm rev16.w reg_D reg_M

	}

}

@encoding (A1) {

	@word cond(4) 0 1 1 0 1 0 1 1 1 1 1 1 Rd(4) 1 1 1 1 1 0 1 1 Rm(4)

	@syntax {

		@subid 432

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)

		}

		@asm rev16 reg_D reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

