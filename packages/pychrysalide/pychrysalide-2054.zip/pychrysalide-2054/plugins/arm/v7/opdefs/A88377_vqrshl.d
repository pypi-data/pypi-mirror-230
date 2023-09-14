
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


@title VQRSHL

@id 354

@desc {

	Vector Saturating Rounding Shift Left takes each element in a vector, shifts them by a value from the least significant byte of the corresponding element of a second vector, and places the results in the destination vector. If the shift value is positive, the operation is a left shift. Otherwise, it is a right shift. For truncated results see VQSHL (register) on page A8-1014. The first operand and result elements are the same data type, and can be any one of: • 8-bit, 16-bit, 32-bit, or 64-bit signed integers • 8-bit, 16-bit, 32-bit, or 64-bit unsigned integers. The second operand is a signed integer of the same size. If any of the results overflow, they are saturated. The cumulative saturation bit, FPSCR.QC, is set if saturation occurs. For details see Pseudocode details of saturation on page A2-44. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 1 0 1 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 2773

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

		@asm vqrshl.s8 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2774

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

		@asm vqrshl.s16 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2775

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

		@asm vqrshl.s32 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2776

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

		@asm vqrshl.s64 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2777

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

		@asm vqrshl.u8 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2778

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

		@asm vqrshl.u16 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2779

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

		@asm vqrshl.u32 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2780

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

		@asm vqrshl.u64 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2781

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

		@asm vqrshl.s8 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2782

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

		@asm vqrshl.s16 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2783

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

		@asm vqrshl.s32 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2784

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

		@asm vqrshl.s64 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2785

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

		@asm vqrshl.u8 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2786

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

		@asm vqrshl.u16 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2787

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

		@asm vqrshl.u32 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2788

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

		@asm vqrshl.u64 ?dwvec_D dwvec_M dwvec_N

	}

}

@encoding (A1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 1 0 1 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 2789

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

		@asm vqrshl.s8 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2790

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

		@asm vqrshl.s16 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2791

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

		@asm vqrshl.s32 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2792

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

		@asm vqrshl.s64 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2793

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

		@asm vqrshl.u8 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2794

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

		@asm vqrshl.u16 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2795

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

		@asm vqrshl.u32 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2796

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

		@asm vqrshl.u64 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2797

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

		@asm vqrshl.s8 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2798

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

		@asm vqrshl.s16 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2799

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

		@asm vqrshl.s32 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2800

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

		@asm vqrshl.s64 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2801

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

		@asm vqrshl.u8 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2802

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

		@asm vqrshl.u16 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2803

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

		@asm vqrshl.u32 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2804

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

		@asm vqrshl.u64 ?dwvec_D dwvec_M dwvec_N

	}

}

