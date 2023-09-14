
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


@title VRSHL

@id 362

@desc {

	Vector Rounding Shift Left takes each element in a vector, shifts them by a value from the least significant byte of the corresponding element of a second vector, and places the results in the destination vector. If the shift value is positive, the operation is a left shift. If the shift value is negative, it is a rounding right shift. (For a truncating shift, see VSHL (register) on page A8-1048). The first operand and result elements are the same data type, and can be any one of: • 8-bit, 16-bit, 32-bit, or 64-bit signed integers • 8-bit, 16-bit, 32-bit, or 64-bit unsigned integers. The second operand is always a signed integer of the same size. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 1 0 1 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2947

		@assert {

			Q == 1
			U == 0
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.s8 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2948

		@assert {

			Q == 1
			U == 0
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.s16 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2949

		@assert {

			Q == 1
			U == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.s32 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2950

		@assert {

			Q == 1
			U == 0
			size == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.s64 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2951

		@assert {

			Q == 1
			U == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.u8 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2952

		@assert {

			Q == 1
			U == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.u16 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2953

		@assert {

			Q == 1
			U == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.u32 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2954

		@assert {

			Q == 1
			U == 1
			size == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.u64 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2955

		@assert {

			Q == 0
			U == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.s8 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2956

		@assert {

			Q == 0
			U == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.s16 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2957

		@assert {

			Q == 0
			U == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.s32 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2958

		@assert {

			Q == 0
			U == 0
			size == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.s64 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2959

		@assert {

			Q == 0
			U == 1
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.u8 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2960

		@assert {

			Q == 0
			U == 1
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.u16 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2961

		@assert {

			Q == 0
			U == 1
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.u32 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2962

		@assert {

			Q == 0
			U == 1
			size == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.u64 ?dwvec_D dwvec_M dwvec_N

	}

}

@encoding (A1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 1 0 1 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2963

		@assert {

			Q == 1
			U == 0
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.s8 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2964

		@assert {

			Q == 1
			U == 0
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.s16 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2965

		@assert {

			Q == 1
			U == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.s32 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2966

		@assert {

			Q == 1
			U == 0
			size == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.s64 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2967

		@assert {

			Q == 1
			U == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.u8 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2968

		@assert {

			Q == 1
			U == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.u16 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2969

		@assert {

			Q == 1
			U == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.u32 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2970

		@assert {

			Q == 1
			U == 1
			size == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			qwvec_N = QuadWordVector(N:Vn)

		}

		@asm vrshl.u64 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2971

		@assert {

			Q == 0
			U == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.s8 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2972

		@assert {

			Q == 0
			U == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.s16 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2973

		@assert {

			Q == 0
			U == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.s32 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2974

		@assert {

			Q == 0
			U == 0
			size == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.s64 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2975

		@assert {

			Q == 0
			U == 1
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.u8 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2976

		@assert {

			Q == 0
			U == 1
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.u16 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2977

		@assert {

			Q == 0
			U == 1
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.u32 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2978

		@assert {

			Q == 0
			U == 1
			size == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			dwvec_N = DoubleWordVector(N:Vn)

		}

		@asm vrshl.u64 ?dwvec_D dwvec_M dwvec_N

	}

}

