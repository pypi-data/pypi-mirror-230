
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


@title VCVT (between double-precision and single-precision)

@id 302

@desc {

	This instruction does one of the following: • converts the value in a double-precision register to single-precision and writes the result to a single-precision register • converts the value in a single-precision register to double-precision and writes the result to a double-precision register. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 summarizes these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 1 1 0 1 1 1 Vd(4) 1 0 1 sz(1) 1 1 M(1) 0 Vm(4)

	@syntax {

		@subid 1261

		@assert {

			sz == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvt.f64.f32 dwvec_D swvec_M

	}

	@syntax {

		@subid 1262

		@assert {

			sz == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.f32.f64 swvec_D dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 1 1 0 1 1 1 Vd(4) 1 0 1 sz(1) 1 1 M(1) 0 Vm(4)

	@syntax {

		@subid 1263

		@assert {

			sz == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvt.f64.f32 dwvec_D swvec_M

	}

	@syntax {

		@subid 1264

		@assert {

			sz == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.f32.f64 swvec_D dwvec_M

	}

}

