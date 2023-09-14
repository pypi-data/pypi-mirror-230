
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


@title VQSHL (register)

@id 355

@desc {

	Vector Saturating Shift Left (register) takes each element in a vector, shifts them by a value from the least significant byte of the corresponding element of a second vector, and places the results in the destination vector. If the shift value is positive, the operation is a left shift. Otherwise, it is a right shift. The results are truncated. For rounded results, see VQRSHL on page A8-1010. The first operand and result elements are the same data type, and can be any one of: • 8-bit, 16-bit, 32-bit, or 64-bit signed integers • 8-bit, 16-bit, 32-bit, or 64-bit unsigned integers. The second operand is a signed integer of the same size. If any of the results overflow, they are saturated. The cumulative saturation bit, FPSCR.QC, is set if saturation occurs. For details see Pseudocode details of saturation on page A2-44. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 1 0 0 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 2805

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

		@asm vqshl.s8 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2806

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

		@asm vqshl.s16 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2807

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

		@asm vqshl.s32 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2808

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

		@asm vqshl.s64 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2809

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

		@asm vqshl.u8 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2810

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

		@asm vqshl.u16 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2811

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

		@asm vqshl.u32 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2812

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

		@asm vqshl.u64 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2813

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

		@asm vqshl.s8 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2814

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

		@asm vqshl.s16 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2815

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

		@asm vqshl.s32 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2816

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

		@asm vqshl.s64 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2817

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

		@asm vqshl.u8 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2818

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

		@asm vqshl.u16 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2819

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

		@asm vqshl.u32 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2820

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

		@asm vqshl.u64 ?dwvec_D dwvec_M dwvec_N

	}

}

@encoding (A1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 1 0 0 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 2821

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

		@asm vqshl.s8 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2822

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

		@asm vqshl.s16 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2823

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

		@asm vqshl.s32 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2824

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

		@asm vqshl.s64 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2825

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

		@asm vqshl.u8 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2826

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

		@asm vqshl.u16 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2827

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

		@asm vqshl.u32 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2828

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

		@asm vqshl.u64 ?qwvec_D qwvec_M qwvec_N

	}

	@syntax {

		@subid 2829

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

		@asm vqshl.s8 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2830

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

		@asm vqshl.s16 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2831

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

		@asm vqshl.s32 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2832

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

		@asm vqshl.s64 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2833

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

		@asm vqshl.u8 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2834

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

		@asm vqshl.u16 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2835

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

		@asm vqshl.u32 ?dwvec_D dwvec_M dwvec_N

	}

	@syntax {

		@subid 2836

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

		@asm vqshl.u64 ?dwvec_D dwvec_M dwvec_N

	}

}

