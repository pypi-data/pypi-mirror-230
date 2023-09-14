
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


@title SXTH

@id 230

@desc {

	Signed Extend Halfword extracts a 16-bit value from a register, sign-extends it to 32 bits, and writes the result to the destination register. The instruction can specify a rotation by 0, 8, 16, or 24 bits before extracting the 16-bit value.

}

@encoding (t1) {

	@half 1 0 1 1 0 0 1 0 0 0 Rm(3) Rd(3)

	@syntax {

		@subid 718

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)
			rotation = Rotation(0)

		}

		@asm sxth ?reg_D reg_M ?rotation

	}

}

@encoding (T2) {

	@word 1 1 1 1 1 0 1 0 0 0 0 0 1 1 1 1 1 1 1 1 Rd(4) 1 0 rotate(2) Rm(4)

	@syntax {

		@subid 719

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)
			rotation = Rotation(rotate:'000')

		}

		@asm sxth.w ?reg_D reg_M ?rotation

	}

}

@encoding (A1) {

	@word cond(4) 0 1 1 0 1 0 1 1 1 1 1 1 Rd(4) rotate(2) 0 0 0 1 1 1 Rm(4)

	@syntax {

		@subid 720

		@conv {

			reg_D = Register(Rd)
			reg_M = Register(Rm)
			rotation = Rotation(rotate:'000')

		}

		@asm sxth ?reg_D reg_M ?rotation

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

