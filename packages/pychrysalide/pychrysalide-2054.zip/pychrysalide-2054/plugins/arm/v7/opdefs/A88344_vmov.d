
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


@title VMOV (between two ARM core registers and two single-precision registers)

@id 326

@desc {

	This instruction transfers the contents of two consecutively numbered single-precision Floating-point registers to two ARM core registers, or the contents of two ARM core registers to a pair of single-precision Floating-point registers. The ARM core registers do not have to be contiguous. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 summarizes these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 0 0 0 1 0 op(1) Rt2(4) Rt(4) 1 0 1 0 0 0 M(1) 1 Vm(4)

	@syntax {

		@subid 2381

		@assert {

			op == 0

		}

		@conv {

			swvec_M = SingleWordVector(Vm:M)
			reg_Sm1 = NextSingleWordVector(swvec_M)
			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)

		}

		@asm vmov swvec_M reg_Sm1 reg_T reg_T2

	}

	@syntax {

		@subid 2382

		@assert {

			op == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			swvec_M = SingleWordVector(Vm:M)
			reg_Sm1 = NextSingleWordVector(swvec_M)

		}

		@asm vmov reg_T reg_T2 swvec_M reg_Sm1

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 0 0 0 1 0 op(1) Rt2(4) Rt(4) 1 0 1 0 0 0 M(1) 1 Vm(4)

	@syntax {

		@subid 2383

		@assert {

			op == 0

		}

		@conv {

			swvec_M = SingleWordVector(Vm:M)
			reg_Sm1 = NextSingleWordVector(swvec_M)
			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)

		}

		@asm vmov swvec_M reg_Sm1 reg_T reg_T2

	}

	@syntax {

		@subid 2384

		@assert {

			op == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			swvec_M = SingleWordVector(Vm:M)
			reg_Sm1 = NextSingleWordVector(swvec_M)

		}

		@asm vmov reg_T reg_T2 swvec_M reg_Sm1

	}

}

