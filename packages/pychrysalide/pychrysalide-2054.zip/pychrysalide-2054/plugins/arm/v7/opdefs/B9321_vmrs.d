
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

@id 408

@desc {

	Move to ARM core register from Advanced SIMD and Floating-point Extension System Register moves the value of an extension system register to an ARM core register. When the specified Floating-point Extension System Register is the FPSCR, a form of the instruction transfers the FPSCR.{N, Z, C, V} condition flags to the APSR.{N, Z, C, V} condition flags. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute a VMRS instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 and Summary of access controls for Advanced SIMD functionality on page B1-1232 summarize these controls. When these settings permit the execution of floating-point and Advanced SIMD instructions, if the specified Floating-point Extension System Register is not the FPSCR, the instruction is UNDEFINED if executed in User mode. In an implementation that includes the Virtualization Extensions, when HCR.TID0 is set to 1, any VMRS access to FPSID from a Non-secure PL1 mode, that would be permitted if HCR.TID0 was set to 0, generates a Hyp Trap exception. For more information, see ID group 0, Primary device identification registers on page B1-1251. Note • VMRS on page A8-954 describes the valid application level uses of the VMRS instruction • for simplicity, the VMRS pseudocode does not show the possible trap to Hyp mode.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 0 1 1 1 1 reg(4) Rt(4) 1 0 1 0 0 0 0 1 0 0 0 0

	@syntax {

		@subid 3832

		@conv {

			reg_T = Register(Rt)
			spec_reg = SpecRegFromReg(reg)

		}

		@asm vmrs reg_T spec_reg

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 0 1 1 1 1 reg(4) Rt(4) 1 0 1 0 0 0 0 1 0 0 0 0

	@syntax {

		@subid 3833

		@conv {

			reg_T = Register(Rt)
			spec_reg = SpecRegFromReg(reg)

		}

		@asm vmrs reg_T spec_reg

	}

}

