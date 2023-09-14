
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


@title BFC

@id 18

@desc {

	Bit Field Clear clears any number of adjacent bits at any position in a register, without affecting the other bits in the register.

}

@encoding (T1) {

	@word 1 1 1 1 0 0 1 1 0 1 1 0 1 1 1 1 0 imm3(3) Rd(4) imm2(2) 0 msb(5)

	@syntax {

		@subid 70

		@conv {

			reg_D = Register(Rd)
			lsbit = UInt(imm3:imm2)
			msbit = UInt(msb)
			width = BitDiff(msbit, lsbit)

		}

		@asm bfc reg_D lsbit width

	}

}

@encoding (A1) {

	@word cond(4) 0 1 1 1 1 1 0 msb(5) Rd(4) lsb(5) 0 0 1 1 1 1 1

	@syntax {

		@subid 71

		@conv {

			reg_D = Register(Rd)
			lsbit = UInt(lsb)
			msbit = UInt(msb)
			width = BitDiff(msbit, lsbit)

		}

		@asm bfc reg_D lsbit width

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

