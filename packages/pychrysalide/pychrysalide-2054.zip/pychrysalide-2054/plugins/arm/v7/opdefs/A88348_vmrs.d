
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


@title VMRS

@id 330

@desc {

	Move to ARM core register from Advanced SIMD and Floating-point Extension System Register moves the value of the FPSCR to an ARM core register. For details of system level use of this instruction, see VMRS on page B9-2012. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 and Summary of access controls for Advanced SIMD functionality on page B1-1232 summarize these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 0 1 1 1 1 0 0 0 1 Rt(4) 1 0 1 0 0 0 0 1 0 0 0 0

	@syntax {

		@subid 2407

		@conv {

			reg_T = Register(Rt)
			reg_FPSCR = SpecReg(SRT_FPSCR)

		}

		@asm vmrs reg_T reg_FPSCR

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 0 1 1 1 1 0 0 0 1 Rt(4) 1 0 1 0 0 0 0 1 0 0 0 0

	@syntax {

		@subid 2408

		@conv {

			reg_T = Register(Rt)
			reg_FPSCR = SpecReg(SRT_FPSCR)

		}

		@asm vmrs reg_T reg_FPSCR

	}

}

