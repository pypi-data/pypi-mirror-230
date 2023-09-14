
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


@title MSR (Banked register)

@id 397

@desc {

	Move to Banked or Special register from ARM core register moves the value of an ARM core register to the Banked ARM core register or SPSR of the specified mode, or to ELR_hyp. MSR (Banked register) is UNPREDICTABLE if executed in User mode. The effect of using an MSR (Banked register) instruction with a register argument that is not valid for the current mode is UNPREDICTABLE. For more information see Usage restrictions on the Banked register transfer instructions on page B9-1972.

}

@encoding (T1) {

	@word 1 1 1 1 0 0 1 1 1 0 0 R(1) Rn(4) 1 0 0 0 m1(4) 0 0 1 m(1) 0 0 0 0

	@syntax {

		@subid 3806

		@conv {

			banked_reg = BankedRegister(R, m:m1)
			reg_N = Register(Rn)

		}

		@asm msr banked_reg reg_N

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 R(1) 1 0 m1(4) 1 1 1 1 0 0 1 m(1) 0 0 0 0 Rn(4)

	@syntax {

		@subid 3807

		@conv {

			banked_reg = BankedRegister(R, m:m1)
			reg_N = Register(Rn)

		}

		@asm msr banked_reg reg_N

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

