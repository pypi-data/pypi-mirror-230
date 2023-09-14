
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


@title MSR (immediate)

@id 106

@desc {

	Move immediate value to Special register moves selected bits of an immediate value to the corresponding bits in the APSR. For details of system level use of this instruction, see MSR (immediate) on page B9-1994.

}

@encoding (A1) {

	@word cond(4) 0 0 1 1 0 0 1 0 mask(2) 0 0 1 1 1 1 imm12(12)

	@syntax {

		@subid 337

		@conv {

			spec_reg = SpecRegFromMask(mask)
			imm32 = ARMExpandImm(imm12)

		}

		@asm msr spec_reg imm32

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

