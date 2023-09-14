
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


@title MRS (Banked register)

@id 396

@desc {

	Move to Register from Banked or Special register moves the value from the Banked ARM core register or SPSR of the specified mode, or the value of ELR_hyp, to an ARM core register. MRS (Banked register) is UNPREDICTABLE if executed in User mode. The effect of using an MRS (Banked register) instruction with a register argument that is not valid for the current mode is UNPREDICTABLE. For more information see Usage restrictions on the Banked register transfer instructions on page B9-1972.

}

@encoding (T1) {

	@word 1 1 1 1 0 0 1 1 1 1 1 R(1) m1(4) 1 0 0 0 Rd(4) 0 0 1 m(1) 0 0 0 0

	@syntax {

		@subid 3804

		@conv {

			reg_D = Register(Rd)
			banked_reg = BankedRegister(R, m:m1)

		}

		@asm mrs reg_D banked_reg

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 R(1) 0 0 m1(4) Rd(4) 0 0 1 m(1) 0 0 0 0 0 0 0 0

	@syntax {

		@subid 3805

		@conv {

			reg_D = Register(Rd)
			banked_reg = BankedRegister(R, m:m1)

		}

		@asm mrs reg_D banked_reg

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

