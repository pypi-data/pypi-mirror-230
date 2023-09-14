
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


@title MSR (register)

@id 399

@desc {

	Move to Special register from ARM core register moves the value of an ARM core register to the CPSR or the SPSR of the current mode. MSR (register) is UNPREDICTABLE if: • In Non-debug state, it is attempting to update the CPSR, and that update would change to a mode that is not permitted in the context in which the instruction is executed, see Restrictions on updates to the CPSR.M field on page B9-1970. • In Debug state, it is attempting an update to the CPSR with a <fields> value that is not <fsxc>. See Behavior of MRS and MSR instructions that access the CPSR in Debug state on page C5-2097. An MSR (register) executed in User mode: • is UNPREDICTABLE if it attempts to update the SPSR • otherwise, does not update any CPSR field that is accessible only at PL1 or higher, Note MSR (register) on page A8-500 describes the valid application level uses of the MSR (register) instruction. An MSR (register) executed in System mode is UNPREDICTABLE if it attempts to update the SPSR.

}

@encoding (T1) {

	@word 1 1 1 1 0 0 1 1 1 0 0 R(1) Rn(4) 1 0 0 0 mask(4) 0 0 0 0 0 0 0 0

	@syntax {

		@subid 3809

		@conv {

			spec_reg = SpecRegFromMask(mask)
			reg_N = Register(Rn)

		}

		@asm msr spec_reg reg_N

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 R(1) 1 0 mask(4) 1 1 1 1 0 0 0 0 0 0 0 0 Rn(4)

	@syntax {

		@subid 3810

		@conv {

			spec_reg = SpecRegFromMask(mask)
			reg_N = Register(Rn)

		}

		@asm msr spec_reg reg_N

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

