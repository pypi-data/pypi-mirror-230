
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


@title VMOV (between ARM core register and single-precision register)

@id 325

@desc {

	This instruction transfers the contents of a single-precision Floating-point register to an ARM core register, or the contents of an ARM core register to a single-precision Floating-point register. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 summarizes these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 0 0 0 0 op(1) Vn(4) Rt(4) 1 0 1 0 N(1) 0 0 1 0 0 0 0

	@syntax {

		@subid 2377

		@assert {

			op == 0

		}

		@conv {

			swvec_N = SingleWordVector(Vn:N)
			reg_T = Register(Rt)

		}

		@asm vmov swvec_N reg_T

	}

	@syntax {

		@subid 2378

		@assert {

			op == 1

		}

		@conv {

			reg_T = Register(Rt)
			swvec_N = SingleWordVector(Vn:N)

		}

		@asm vmov reg_T swvec_N

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 0 0 0 0 op(1) Vn(4) Rt(4) 1 0 1 0 N(1) 0 0 1 0 0 0 0

	@syntax {

		@subid 2379

		@assert {

			op == 0

		}

		@conv {

			swvec_N = SingleWordVector(Vn:N)
			reg_T = Register(Rt)

		}

		@asm vmov swvec_N reg_T

	}

	@syntax {

		@subid 2380

		@assert {

			op == 1

		}

		@conv {

			reg_T = Register(Rt)
			swvec_N = SingleWordVector(Vn:N)

		}

		@asm vmov reg_T swvec_N

	}

}

