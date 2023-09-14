
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


@title SMC (previously SMI)

@id 401

@desc {

	Secure Monitor Call causes a Secure Monitor Call exception. For more information see Secure Monitor Call (SMC) exception on page B1-1210. SMC is available only from software executing at PL1 or higher. It is UNDEFINED in User mode. In an implementation that includes the Virtualization Extensions: • If HCR.TSC is set to 1, execution of an SMC instruction in a Non-secure PL1 mode generates a Hyp Trap exception, regardless of the value of SCR.SCD. For more information see Trapping use of the SMC instruction on page B1-1254. • Otherwise, when SCR.SCD is set to 1, the SMC instruction is: — UNDEFINED in Non-secure state — UNPREDICTABLE if executed in a Secure PL1 mode.

}

@encoding (T1) {

	@word 1 1 1 1 0 1 1 1 1 1 1 1 imm4(4) 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

	@syntax {

		@subid 3817

		@conv {

			direct_imm4 = UInt(imm4)

		}

		@asm smc direct_imm4

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 imm4(4)

	@syntax {

		@subid 3818

		@conv {

			direct_imm4 = UInt(imm4)

		}

		@asm smc direct_imm4

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

