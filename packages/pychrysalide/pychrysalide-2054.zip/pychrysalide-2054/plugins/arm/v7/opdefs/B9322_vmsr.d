
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


@title VMSR

@id 409

@desc {

	Move to Advanced SIMD and Floating-point Extension System Register from ARM core register moves the value of an ARM core register to a Floating-point system register. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute a VMSR instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 and Summary of access controls for Advanced SIMD functionality on page B1-1232 summarize these controls. When these settings permit the execution of floating-point and Advanced SIMD instructions, if the specified Floating-point Extension System Register is not the FPSCR, the instruction is UNDEFINED if executed in User mode. Note VMSR on page A8-956 describes the valid application level uses of the VMSR instruction.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 0 1 1 1 0 reg(4) Rt(4) 1 0 1 0 0 0 0 1 0 0 0 0

	@syntax {

		@subid 3834

		@conv {

			spec_reg = SpecRegFromReg(reg)
			reg_T = Register(Rt)

		}

		@asm vmsr spec_reg reg_T

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 0 1 1 1 0 reg(4) Rt(4) 1 0 1 0 0 0 0 1 0 0 0 0

	@syntax {

		@subid 3835

		@conv {

			spec_reg = SpecRegFromReg(reg)
			reg_T = Register(Rt)

		}

		@asm vmsr spec_reg reg_T

	}

}

