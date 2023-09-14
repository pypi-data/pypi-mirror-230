
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


@title UQADD16

@id 253

@desc {

	Unsigned Saturating Add 16 performs two unsigned 16-bit integer additions, saturates the results to the 16-bit unsigned integer range 0 ≤ x ≤ 216 – 1, and writes the results to the destination register.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 1 0 1 0 0 1 Rn(4) 1 1 1 1 Rd(4) 0 1 0 1 Rm(4)

	@syntax {

		@subid 767

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm uqadd16 ?reg_D reg_N reg_M

	}

}

@encoding (A1) {

	@word cond(4) 0 1 1 0 0 1 1 0 Rn(4) Rd(4) 1 1 1 1 0 0 0 1 Rm(4)

	@syntax {

		@subid 768

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)

		}

		@asm uqadd16 ?reg_D reg_N reg_M

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

