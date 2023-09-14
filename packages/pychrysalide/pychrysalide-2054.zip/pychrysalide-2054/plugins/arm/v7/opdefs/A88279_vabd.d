
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


@title VABD (floating-point)

@id 274

@desc {

	Vector Absolute Difference (floating-point) subtracts the elements of one vector from the corresponding elements of another vector, and places the absolute values of the results in the elements of the destination vector. Operand and result elements are all single-precision floating-point numbers. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction that is not also available as a VFP instruction, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 0 D(1) 1 sz(1) Vn(4) Vd(4) 1 1 0 1 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 879

		@assert {

			Q == 1
			sz == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vabd.f32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 880

		@assert {

			Q == 0
			sz == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabd.f32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 0 D(1) 1 sz(1) Vn(4) Vd(4) 1 1 0 1 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 881

		@assert {

			Q == 1
			sz == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vabd.f32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 882

		@assert {

			Q == 0
			sz == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabd.f32 ?dwvec_D dwvec_N dwvec_M

	}

}

