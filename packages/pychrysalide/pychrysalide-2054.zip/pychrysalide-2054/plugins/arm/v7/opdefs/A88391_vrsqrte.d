
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


@title VRSQRTE

@id 363

@desc {

	Vector Reciprocal Square Root Estimate finds an approximate reciprocal square root of each element in a vector, and places the results in a second vector. The operand and result elements are the same type, and can be 32-bit floating-point numbers, or 32-bit unsigned integers. For details of the operation performed by this instruction see Floating-point reciprocal square root estimate and step on page A2-87. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 1 1 Vd(4) 0 1 0 F(1) 1 Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2979

		@assert {

			Q == 1
			F == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrsqrte.u32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2980

		@assert {

			Q == 1
			F == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrsqrte.f32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2981

		@assert {

			Q == 0
			F == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrsqrte.u32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2982

		@assert {

			Q == 0
			F == 1
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrsqrte.f32 dwvec_D dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 1 1 Vd(4) 0 1 0 F(1) 1 Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2983

		@assert {

			Q == 1
			F == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrsqrte.u32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2984

		@assert {

			Q == 1
			F == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrsqrte.f32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2985

		@assert {

			Q == 0
			F == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrsqrte.u32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2986

		@assert {

			Q == 0
			F == 1
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrsqrte.f32 dwvec_D dwvec_M

	}

}

