
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


@title WFI

@id 385

@desc {

	Wait For Interrupt is a hint instruction that permits the processor to enter a low-power state until one of a number of asynchronous events occurs. For more information, see Wait For Interrupt on page B1-1202. In an implementation that includes the Virtualization Extensions, if HCR.TWI is set to 1, execution of a WFI instruction in a Non-secure mode other than Hyp mode generates a Hyp Trap exception if, ignoring the value of the HCR.TWI bit, conditions permit the processor to suspend execution. For more information see Trapping use of the WFI and WFE instructions on page B1-1255.

}

@encoding (t1) {

	@half 1 0 1 1 1 1 1 1 0 0 1 1 0 0 0 0

	@syntax {

		@subid 3774

		@asm wfi

	}

}

@encoding (T2) {

	@word 1 1 1 1 0 0 1 1 1 0 1 0 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1

	@syntax {

		@subid 3775

		@asm wfi.w

	}

}

@encoding (A1) {

	@word cond(4) 0 0 1 1 0 0 1 0 0 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 0 0 1 1

	@syntax {

		@subid 3776

		@asm wfi

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

