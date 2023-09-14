
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


@title VCEQ (register)

@id 286

@desc {

	VCEQ (Vector Compare Equal) takes each element in a vector, and compares it with the corresponding element of a second vector. If they are equal, the corresponding element in the destination vector is set to all ones. Otherwise, it is set to all zeros. The operand vector elements can be any one of: • 8-bit, 16-bit, or 32-bit integers. There is no distinction between signed and unsigned integers. • 32-bit floating-point numbers. The result vector elements are fields the same size as the operand vector elements. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 1 0 0 0 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 1025

		@assert {

			Q == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vceq.i8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1026

		@assert {

			Q == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vceq.i16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1027

		@assert {

			Q == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vceq.i32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1028

		@assert {

			Q == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vceq.i8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1029

		@assert {

			Q == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vceq.i16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1030

		@assert {

			Q == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vceq.i32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 1 1 1 0 D(1) 0 sz(1) Vn(4) Vd(4) 1 1 1 0 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1031

		@assert {

			Q == 1
			sz == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vceq.f32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1032

		@assert {

			Q == 0
			sz == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vceq.f32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 1 0 0 0 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 1033

		@assert {

			Q == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vceq.i8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1034

		@assert {

			Q == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vceq.i16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1035

		@assert {

			Q == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vceq.i32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1036

		@assert {

			Q == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vceq.i8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1037

		@assert {

			Q == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vceq.i16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1038

		@assert {

			Q == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vceq.i32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A2) {

	@word 1 1 1 0 1 1 1 1 0 D(1) 0 sz(1) Vn(4) Vd(4) 1 1 1 0 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1039

		@assert {

			Q == 1
			sz == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vceq.f32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1040

		@assert {

			Q == 0
			sz == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vceq.f32 ?dwvec_D dwvec_N dwvec_M

	}

}

