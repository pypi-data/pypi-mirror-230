
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


@title VMOV (between two ARM core registers and a doubleword extension register)

@id 327

@desc {

	This instruction copies two words from two ARM core registers into a doubleword extension register, or from a doubleword extension register to two ARM core registers. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 and Summary of access controls for Advanced SIMD functionality on page B1-1232 summarize these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 0 0 0 1 0 op(1) Rt2(4) Rt(4) 1 0 1 1 0 0 M(1) 1 Vm(4)

	@syntax {

		@subid 2385

		@assert {

			op == 0

		}

		@conv {

			dwvec_M = DoubleWordVector(M:Vm)
			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)

		}

		@asm vmov dwvec_M reg_T reg_T2

	}

	@syntax {

		@subid 2386

		@assert {

			op == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmov reg_T reg_T2 dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 0 0 0 1 0 op(1) Rt2(4) Rt(4) 1 0 1 1 0 0 M(1) 1 Vm(4)

	@syntax {

		@subid 2387

		@assert {

			op == 0

		}

		@conv {

			dwvec_M = DoubleWordVector(M:Vm)
			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)

		}

		@asm vmov dwvec_M reg_T reg_T2

	}

	@syntax {

		@subid 2388

		@assert {

			op == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmov reg_T reg_T2 dwvec_M

	}

}

