
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


@title VRHADD

@id 361

@desc {

	Vector Rounding Halving Add adds corresponding elements in two vectors of integers, shifts each result right one bit, and places the final results in the destination vector. The operand and result elements are all the same type, and can be any one of: • 8-bit, 16-bit, or 32-bit signed integers • 8-bit, 16-bit, or 32-bit unsigned integers. The results of the halving operations are rounded. For truncated results see VHADD, VHSUB on page A8-896. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 0 0 1 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2923

		@assert {

			Q == 1
			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrhadd.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2924

		@assert {

			Q == 1
			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrhadd.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2925

		@assert {

			Q == 1
			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrhadd.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2926

		@assert {

			Q == 1
			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrhadd.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2927

		@assert {

			Q == 1
			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrhadd.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2928

		@assert {

			Q == 1
			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrhadd.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2929

		@assert {

			Q == 0
			size == 0
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrhadd.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2930

		@assert {

			Q == 0
			size == 1
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrhadd.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2931

		@assert {

			Q == 0
			size == 10
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrhadd.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2932

		@assert {

			Q == 0
			size == 0
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrhadd.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2933

		@assert {

			Q == 0
			size == 1
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrhadd.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2934

		@assert {

			Q == 0
			size == 10
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrhadd.u32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 0 0 1 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2935

		@assert {

			Q == 1
			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrhadd.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2936

		@assert {

			Q == 1
			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrhadd.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2937

		@assert {

			Q == 1
			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrhadd.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2938

		@assert {

			Q == 1
			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrhadd.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2939

		@assert {

			Q == 1
			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrhadd.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2940

		@assert {

			Q == 1
			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrhadd.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2941

		@assert {

			Q == 0
			size == 0
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrhadd.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2942

		@assert {

			Q == 0
			size == 1
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrhadd.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2943

		@assert {

			Q == 0
			size == 10
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrhadd.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2944

		@assert {

			Q == 0
			size == 0
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrhadd.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2945

		@assert {

			Q == 0
			size == 1
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrhadd.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2946

		@assert {

			Q == 0
			size == 10
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrhadd.u32 ?dwvec_D dwvec_N dwvec_M

	}

}

