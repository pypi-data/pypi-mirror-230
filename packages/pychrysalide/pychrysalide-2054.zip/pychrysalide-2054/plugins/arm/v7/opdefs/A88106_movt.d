
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


@title MOVT

@id 101

@desc {

	Move Top writes an immediate value to the top halfword of the destination register. It does not affect the contents of the bottom halfword.

}

@encoding (T1) {

	@word 1 1 1 1 0 i(1) 1 0 1 1 0 0 imm4(4) 0 imm3(3) Rd(4) imm8(8)

	@syntax {

		@subid 325

		@conv {

			reg_D = Register(Rd)
			imm16 = UInt(imm4:i:imm3:imm8)

		}

		@asm movt reg_D imm16

	}

}

@encoding (A1) {

	@word cond(4) 0 0 1 1 0 1 0 0 imm4(4) Rd(4) imm12(12)

	@syntax {

		@subid 326

		@conv {

			reg_D = Register(Rd)
			imm16 = UInt(imm4:imm12)

		}

		@asm movt reg_D imm16

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

