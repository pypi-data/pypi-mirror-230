
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


@title USAT

@id 261

@desc {

	Unsigned Saturate saturates an optionally-shifted signed value to a selected unsigned range. The Q flag is set if the operation saturates.

}

@encoding (T1) {

	@word 1 1 1 1 0 0 1 1 1 0 sh(1) 0 Rn(4) 0 imm3(3) Rd(4) imm2(2) 0 sat_imm(5)

	@syntax {

		@subid 783

		@conv {

			reg_D = Register(Rd)
			saturate_to = UInt(sat_imm)
			reg_N = Register(Rn)
			shift = DecodeImmShift(sh:'0', imm3:imm2)

		}

		@asm usat reg_D saturate_to reg_N ?shift

	}

}

@encoding (A1) {

	@word cond(4) 0 1 1 0 1 1 1 sat_imm(5) Rd(4) imm5(5) sh(1) 0 1 Rn(4)

	@syntax {

		@subid 784

		@conv {

			reg_D = Register(Rd)
			saturate_to = UInt(sat_imm)
			reg_N = Register(Rn)
			shift = DecodeImmShift(sh:'0', imm5)

		}

		@asm usat reg_D saturate_to reg_N ?shift

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

