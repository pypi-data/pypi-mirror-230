
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


@title VQSUB

@id 356

@desc {

	Vector Saturating Subtract subtracts the elements of the second operand vector from the corresponding elements of the first operand vector, and places the results in the destination vector. Signed and unsigned operations are distinct. The operand and result elements must all be the same type, and can be any one of: • 8-bit, 16-bit, 32-bit, or 64-bit signed integers • 8-bit, 16-bit, 32-bit, or 64-bit unsigned integers. If any of the results overflow, they are saturated. The cumulative saturation bit, FPSCR.QC, is set if saturation occurs. For details see Pseudocode details of saturation on page A2-44. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 0 1 0 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 2837

		@assert {

			Q == 1
			U == 0
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2838

		@assert {

			Q == 1
			U == 0
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2839

		@assert {

			Q == 1
			U == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2840

		@assert {

			Q == 1
			U == 0
			size == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.s64 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2841

		@assert {

			Q == 1
			U == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2842

		@assert {

			Q == 1
			U == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2843

		@assert {

			Q == 1
			U == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2844

		@assert {

			Q == 1
			U == 1
			size == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.u64 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2845

		@assert {

			Q == 0
			U == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2846

		@assert {

			Q == 0
			U == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2847

		@assert {

			Q == 0
			U == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2848

		@assert {

			Q == 0
			U == 0
			size == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.s64 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2849

		@assert {

			Q == 0
			U == 1
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2850

		@assert {

			Q == 0
			U == 1
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2851

		@assert {

			Q == 0
			U == 1
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.u32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2852

		@assert {

			Q == 0
			U == 1
			size == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.u64 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 0 1 0 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 2853

		@assert {

			Q == 1
			U == 0
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2854

		@assert {

			Q == 1
			U == 0
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2855

		@assert {

			Q == 1
			U == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2856

		@assert {

			Q == 1
			U == 0
			size == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.s64 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2857

		@assert {

			Q == 1
			U == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2858

		@assert {

			Q == 1
			U == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2859

		@assert {

			Q == 1
			U == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2860

		@assert {

			Q == 1
			U == 1
			size == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqsub.u64 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2861

		@assert {

			Q == 0
			U == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2862

		@assert {

			Q == 0
			U == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2863

		@assert {

			Q == 0
			U == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2864

		@assert {

			Q == 0
			U == 0
			size == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.s64 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2865

		@assert {

			Q == 0
			U == 1
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2866

		@assert {

			Q == 0
			U == 1
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2867

		@assert {

			Q == 0
			U == 1
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.u32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2868

		@assert {

			Q == 0
			U == 1
			size == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vqsub.u64 ?dwvec_D dwvec_N dwvec_M

	}

}

