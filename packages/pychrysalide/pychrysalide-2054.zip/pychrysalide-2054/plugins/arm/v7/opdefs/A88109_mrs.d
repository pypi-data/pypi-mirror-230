
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


@title MRS

@id 104

@desc {

	Move to Register from Special register moves the value from the APSR into an ARM core register. For details of system level use of this instruction, see MRS on page B9-1988.

}

@encoding (T1) {

	@word 1 1 1 1 0 0 1 1 1 1 1 0 1 1 1 1 1 0 0 0 Rd(4) 0 0 0 0 0 0 0 0

	@syntax {

		@subid 335

		@conv {

			reg_D = Register(Rd)
			spec_reg = SpecReg(SRT_APSR)

		}

		@asm mrs reg_D spec_reg

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 0 0 0 1 1 1 1 Rd(4) 0 0 0 0 0 0 0 0 0 0 0 0

	@syntax {

		@subid 336

		@conv {

			reg_D = Register(Rd)
			spec_reg = SpecReg(SRT_APSR)

		}

		@asm mrs reg_D spec_reg

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

