
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


@title VRSUBHN

@id 365

@desc {

	Vector Rounding Subtract and Narrow, returning High Half subtracts the elements of one quadword vector from the corresponding elements of another quadword vector takes the most significant half of each result, and places the final results in a doubleword vector. The results are rounded. (For truncated results, see VSUBHN on page A8-1088.) The operand elements can be 16-bit, 32-bit, or 64-bit integers. There is no distinction between signed and unsigned integers. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) size(2) Vn(4) Vd(4) 0 1 1 0 N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 2991

		@assert {

			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrsubhn.i16 dwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2992

		@assert {

			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrsubhn.i32 dwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2993

		@assert {

			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrsubhn.i64 dwvec_D qwvec_N qwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) size(2) Vn(4) Vd(4) 0 1 1 0 N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 2994

		@assert {

			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrsubhn.i16 dwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2995

		@assert {

			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrsubhn.i32 dwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2996

		@assert {

			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrsubhn.i64 dwvec_D qwvec_N qwvec_M

	}

}

