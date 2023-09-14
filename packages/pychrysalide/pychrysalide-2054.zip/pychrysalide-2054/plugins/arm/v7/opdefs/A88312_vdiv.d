
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


@title VDIV

@id 305

@desc {

	This instruction divides one floating-point value by another floating-point value and writes the result to a third floating-point register. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 summarizes these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 0 0 Vn(4) Vd(4) 1 0 1 sz(1) N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 1277

		@assert {

			sz == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vdiv.f64 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1278

		@assert {

			sz == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vdiv.f32 ?swvec_D swvec_N swvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 0 0 Vn(4) Vd(4) 1 0 1 sz(1) N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 1279

		@assert {

			sz == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vdiv.f64 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1280

		@assert {

			sz == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vdiv.f32 ?swvec_D swvec_N swvec_M

	}

}

