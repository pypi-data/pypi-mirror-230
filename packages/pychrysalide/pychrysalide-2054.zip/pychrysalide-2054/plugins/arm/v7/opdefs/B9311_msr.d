
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

@id 398

@desc {

	Move immediate value to Special register moves selected bits of an immediate value to the CPSR or the SPSR of the current mode. MSR (immediate) is UNPREDICTABLE if: • In Non-debug state, it is attempting to update the CPSR, and that update would change to a mode that is not permitted in the context in which the instruction is executed, see Restrictions on updates to the CPSR.M field on page B9-1970. • In Debug state, it is attempting an update to the CPSR with a <fields> value that is not <fsxc>. See Behavior of MRS and MSR instructions that access the CPSR in Debug state on page C5-2097. An MSR (immediate) executed in User mode: • is UNPREDICTABLE if it attempts to update the SPSR • otherwise, does not update any CPSR field that is accessible only at PL1 or higher, Note MSR (immediate) on page A8-498 describes the valid application level uses of the MSR (immediate) instruction. An MSR (immediate) executed in System mode is UNPREDICTABLE if it attempts to update the SPSR.

}

@encoding (A1) {

	@word cond(4) 0 0 1 1 0 R(1) 1 0 mask(4) 1 1 1 1 imm12(12)

	@syntax {

		@subid 3808

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

