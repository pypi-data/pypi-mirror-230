
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


@title MOV (register, Thumb)

@id 98

@desc {

	Move (register) copies a value from a register to the destination register. It can optionally update the condition flags based on the value.

}

@encoding (t1) {

	@half 0 1 0 0 0 1 1 0 D(1) Rm(4) Rd(3)

	@syntax {

		@subid 319

		@conv {

			reg_D = Register(D:Rd)
			reg_M = Register(Rm)

		}

		@asm mov reg_D reg_M

	}

}

@encoding (t2) {

	@half 0 0 0 0 0 0 0 0 0 0 Rm(3) Rd(3)

	@syntax {

		@subid 320

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)

		}

		@asm movs reg_D reg_M

	}

}

@encoding (T3) {

	@word 1 1 1 0 1 0 1 0 0 1 0 S(1) 1 1 1 1 0 0 0 0 Rd(4) 0 0 0 0 Rm(4)

	@syntax {

		@subid 321

		@assert {

			S == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)

		}

		@asm mov.w reg_D reg_M

	}

	@syntax {

		@subid 322

		@assert {

			S == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)

		}

		@asm movs.w reg_D reg_M

	}

}

