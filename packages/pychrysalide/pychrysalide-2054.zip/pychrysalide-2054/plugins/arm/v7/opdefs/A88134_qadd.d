
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


@title QADD

@id 129

@desc {

	Saturating Add adds two register values, saturates the result to the 32-bit signed integer range –231 to (231 – 1), and writes the result to the destination register. If saturation occurs, it sets the Q flag in the APSR.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 1 0 1 0 0 0 Rn(4) 1 1 1 1 Rd(4) 1 0 0 0 Rm(4)

	@syntax {

		@subid 405

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)
			reg_N = Register(Rn)

		}

		@asm qadd ?reg_D reg_M reg_N

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 0 0 0 Rn(4) Rd(4) 0 0 0 0 0 1 0 1 Rm(4)

	@syntax {

		@subid 406

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)
			reg_N = Register(Rn)

		}

		@asm qadd ?reg_D reg_M reg_N

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

