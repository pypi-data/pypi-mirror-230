
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


@title VCVT (between half-precision and single-precision, Advanced SIMD)

@id 303

@desc {

	This instruction converts each element in a vector from single-precision to half-precision floating-point or from half-precision to single-precision, and places the results in a second vector. The vector elements must be 32-bit floating-point numbers, or 16-bit floating-point numbers. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 1 0 Vd(4) 0 1 1 op(1) 0 0 M(1) 0 Vm(4)

	@syntax {

		@subid 1265

		@assert {

			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.f32.f16 qwvec_D dwvec_M

	}

	@syntax {

		@subid 1266

		@assert {

			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcvt.f16.f32 dwvec_D qwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 1 0 Vd(4) 0 1 1 op(1) 0 0 M(1) 0 Vm(4)

	@syntax {

		@subid 1267

		@assert {

			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.f32.f16 qwvec_D dwvec_M

	}

	@syntax {

		@subid 1268

		@assert {

			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcvt.f16.f32 dwvec_D qwvec_M

	}

}

